//+------------------------------------------------------------------+
//|                                                      Logger.mqh  |
//|                                        Logging Utility v1.0      |
//|                     File logging, console output, notifications  |
//+------------------------------------------------------------------+
#property copyright "Your Name"
#property link      "https://www.example.com"
#property version   "1.00"
#property strict

//+------------------------------------------------------------------+
//| Log Levels                                                        |
//+------------------------------------------------------------------+
enum ENUM_LOG_LEVEL
{
   LOG_DEBUG = 0,     // Debug
   LOG_INFO,          // Info
   LOG_WARNING,       // Warning
   LOG_ERROR,         // Error
   LOG_CRITICAL       // Critical
};

//+------------------------------------------------------------------+
//| Log Entry Structure                                               |
//+------------------------------------------------------------------+
struct LogEntry
{
   datetime    time;
   ENUM_LOG_LEVEL level;
   string      category;
   string      message;
   
   string ToString()
   {
      string levelStr;
      switch(level)
      {
         case LOG_DEBUG:    levelStr = "DEBUG"; break;
         case LOG_INFO:     levelStr = "INFO"; break;
         case LOG_WARNING:  levelStr = "WARN"; break;
         case LOG_ERROR:    levelStr = "ERROR"; break;
         case LOG_CRITICAL: levelStr = "CRIT"; break;
         default:           levelStr = "???"; break;
      }
      
      return StringFormat("[%s] [%s] [%s] %s",
                         TimeToString(time, TIME_DATE|TIME_SECONDS),
                         levelStr,
                         category,
                         message);
   }
};

//+------------------------------------------------------------------+
//| Logger Class                                                      |
//+------------------------------------------------------------------+
class CLogger
{
private:
   string         m_Name;
   string         m_FilePath;
   int            m_FileHandle;
   ENUM_LOG_LEVEL m_MinLevel;
   bool           m_ConsoleOutput;
   bool           m_FileOutput;
   bool           m_AlertOnError;
   bool           m_PushOnCritical;
   
   //--- Buffer for recent logs
   LogEntry       m_Buffer[];
   int            m_BufferSize;
   int            m_BufferIndex;
   
public:
   //--- Constructor
   CLogger()
   {
      m_Name = "Logger";
      m_FilePath = "";
      m_FileHandle = INVALID_HANDLE;
      m_MinLevel = LOG_INFO;
      m_ConsoleOutput = true;
      m_FileOutput = false;
      m_AlertOnError = false;
      m_PushOnCritical = false;
      m_BufferSize = 100;
      m_BufferIndex = 0;
      ArrayResize(m_Buffer, m_BufferSize);
   }
   
   //--- Destructor
   ~CLogger()
   {
      Close();
   }
   
   //--- Initialize logger
   bool Init(string name, string filePath = "", ENUM_LOG_LEVEL minLevel = LOG_INFO)
   {
      m_Name = name;
      m_MinLevel = minLevel;
      
      if(filePath != "")
      {
         m_FilePath = filePath;
         m_FileHandle = FileOpen(filePath, FILE_WRITE|FILE_TXT|FILE_SHARE_READ|FILE_ANSI);
         
         if(m_FileHandle == INVALID_HANDLE)
         {
            Print("Logger: Failed to open file: ", filePath, " Error: ", GetLastError());
            return false;
         }
         
         m_FileOutput = true;
         
         //--- Write header
         FileWriteString(m_FileHandle, "=== Log Started: " + TimeToString(TimeCurrent()) + " ===\n");
         FileFlush(m_FileHandle);
      }
      
      Info("Logger initialized: " + name);
      return true;
   }
   
   //--- Close logger
   void Close()
   {
      if(m_FileHandle != INVALID_HANDLE)
      {
         FileWriteString(m_FileHandle, "=== Log Ended: " + TimeToString(TimeCurrent()) + " ===\n");
         FileClose(m_FileHandle);
         m_FileHandle = INVALID_HANDLE;
      }
   }
   
   //--- Settings
   void SetMinLevel(ENUM_LOG_LEVEL level)     { m_MinLevel = level; }
   void SetConsoleOutput(bool enable)         { m_ConsoleOutput = enable; }
   void SetFileOutput(bool enable)            { m_FileOutput = enable && m_FileHandle != INVALID_HANDLE; }
   void SetAlertOnError(bool enable)          { m_AlertOnError = enable; }
   void SetPushOnCritical(bool enable)        { m_PushOnCritical = enable; }
   void SetBufferSize(int size)
   {
      m_BufferSize = size;
      ArrayResize(m_Buffer, size);
   }
   
   //+------------------------------------------------------------------+
   //| Logging Methods                                                   |
   //+------------------------------------------------------------------+
   
   //--- Main log method
   void Log(ENUM_LOG_LEVEL level, string category, string message)
   {
      //--- Check minimum level
      if(level < m_MinLevel)
         return;
      
      //--- Create entry
      LogEntry entry;
      entry.time = TimeCurrent();
      entry.level = level;
      entry.category = category;
      entry.message = message;
      
      //--- Add to buffer
      m_Buffer[m_BufferIndex] = entry;
      m_BufferIndex = (m_BufferIndex + 1) % m_BufferSize;
      
      //--- Format output
      string output = entry.ToString();
      
      //--- Console output
      if(m_ConsoleOutput)
         Print(output);
      
      //--- File output
      if(m_FileOutput && m_FileHandle != INVALID_HANDLE)
      {
         FileWriteString(m_FileHandle, output + "\n");
         FileFlush(m_FileHandle);
      }
      
      //--- Alert on error
      if(m_AlertOnError && level >= LOG_ERROR)
         Alert(m_Name + ": " + message);
      
      //--- Push on critical
      if(m_PushOnCritical && level >= LOG_CRITICAL)
         SendNotification(m_Name + ": " + message);
   }
   
   //--- Convenience methods
   void Debug(string message, string category = "")
   {
      if(category == "") category = m_Name;
      Log(LOG_DEBUG, category, message);
   }
   
   void Info(string message, string category = "")
   {
      if(category == "") category = m_Name;
      Log(LOG_INFO, category, message);
   }
   
   void Warning(string message, string category = "")
   {
      if(category == "") category = m_Name;
      Log(LOG_WARNING, category, message);
   }
   
   void Error(string message, string category = "")
   {
      if(category == "") category = m_Name;
      Log(LOG_ERROR, category, message);
   }
   
   void Critical(string message, string category = "")
   {
      if(category == "") category = m_Name;
      Log(LOG_CRITICAL, category, message);
   }
   
   //--- Formatted logging
   void InfoF(string format, string arg1, string arg2 = "", string arg3 = "")
   {
      string message = StringFormat(format, arg1, arg2, arg3);
      Info(message);
   }
   
   void ErrorF(string format, string arg1, string arg2 = "", string arg3 = "")
   {
      string message = StringFormat(format, arg1, arg2, arg3);
      Error(message);
   }
   
   //+------------------------------------------------------------------+
   //| Trade Logging                                                     |
   //+------------------------------------------------------------------+
   
   //--- Log trade execution
   void LogTrade(string action, string symbol, double lots, double price, double sl, double tp)
   {
      string message = StringFormat("%s %s: %.2f lots @ %.5f, SL: %.5f, TP: %.5f",
                                    action, symbol, lots, price, sl, tp);
      Log(LOG_INFO, "TRADE", message);
   }
   
   //--- Log trade result
   void LogTradeResult(bool success, ulong ticket, uint retcode, string description)
   {
      if(success)
      {
         string message = StringFormat("Trade executed. Ticket: %d", ticket);
         Log(LOG_INFO, "TRADE", message);
      }
      else
      {
         string message = StringFormat("Trade failed. Code: %d - %s", retcode, description);
         Log(LOG_ERROR, "TRADE", message);
      }
   }
   
   //--- Log position close
   void LogPositionClose(ulong ticket, double profit)
   {
      string message = StringFormat("Position #%d closed. P/L: %.2f", ticket, profit);
      Log(LOG_INFO, "TRADE", message);
   }
   
   //+------------------------------------------------------------------+
   //| System Logging                                                    |
   //+------------------------------------------------------------------+
   
   //--- Log initialization
   void LogInit(string eaName, string symbol, string settings = "")
   {
      Info(StringFormat("=== %s Initialized ===", eaName), "SYSTEM");
      Info(StringFormat("Symbol: %s | Timeframe: %s", symbol, EnumToString(Period())), "SYSTEM");
      if(settings != "")
         Info(StringFormat("Settings: %s", settings), "SYSTEM");
   }
   
   //--- Log deinit
   void LogDeinit(int reason)
   {
      string reasons[] = {"Program removed", "Recompiled", "Chart symbol changed", 
                          "Chart period changed", "Parameters changed", "Account changed",
                          "Chart closed", "Template changed"};
      string reasonStr = (reason < ArraySize(reasons)) ? reasons[reason] : "Unknown";
      Info(StringFormat("=== Deinitialized. Reason: %s ===", reasonStr), "SYSTEM");
   }
   
   //+------------------------------------------------------------------+
   //| Buffer Access                                                     |
   //+------------------------------------------------------------------+
   
   //--- Get recent logs
   int GetRecentLogs(LogEntry &logs[], int count)
   {
      int actualCount = MathMin(count, m_BufferSize);
      ArrayResize(logs, actualCount);
      
      int startIndex = (m_BufferIndex - actualCount + m_BufferSize) % m_BufferSize;
      
      for(int i = 0; i < actualCount; i++)
      {
         logs[i] = m_Buffer[(startIndex + i) % m_BufferSize];
      }
      
      return actualCount;
   }
   
   //--- Get logs by level
   int GetLogsByLevel(LogEntry &logs[], ENUM_LOG_LEVEL level, int maxCount = 50)
   {
      ArrayResize(logs, 0);
      int count = 0;
      
      for(int i = 0; i < m_BufferSize && count < maxCount; i++)
      {
         int idx = (m_BufferIndex - 1 - i + m_BufferSize) % m_BufferSize;
         if(m_Buffer[idx].level == level)
         {
            ArrayResize(logs, count + 1);
            logs[count] = m_Buffer[idx];
            count++;
         }
      }
      
      return count;
   }
   
   //--- Clear buffer
   void ClearBuffer()
   {
      m_BufferIndex = 0;
      for(int i = 0; i < m_BufferSize; i++)
      {
         m_Buffer[i].time = 0;
         m_Buffer[i].level = LOG_DEBUG;
         m_Buffer[i].category = "";
         m_Buffer[i].message = "";
      }
   }
};

//+------------------------------------------------------------------+
//| Global Logger Instance                                            |
//+------------------------------------------------------------------+
CLogger g_Logger;

//+------------------------------------------------------------------+
//| Quick Logging Functions                                           |
//+------------------------------------------------------------------+
void LogDebug(string msg)    { g_Logger.Debug(msg); }
void LogInfo(string msg)     { g_Logger.Info(msg); }
void LogWarning(string msg)  { g_Logger.Warning(msg); }
void LogError(string msg)    { g_Logger.Error(msg); }
void LogCritical(string msg) { g_Logger.Critical(msg); }

//+------------------------------------------------------------------+
