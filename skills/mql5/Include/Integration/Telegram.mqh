//+------------------------------------------------------------------+
//|                                                    Telegram.mqh  |
//|                             Telegram Integration Utility v1.0    |
//|                                  Send alerts to Telegram bot     |
//+------------------------------------------------------------------+
#property copyright "Your Name"
#property link      "https://www.example.com"
#property version   "1.00"
#property strict

//+------------------------------------------------------------------+
//| Message Types                                                     |
//+------------------------------------------------------------------+
enum ENUM_TELEGRAM_MSG_TYPE
{
   MSG_INFO = 0,      // Information
   MSG_SIGNAL,        // Trading Signal
   MSG_TRADE,         // Trade Execution
   MSG_ALERT,         // Alert
   MSG_ERROR,         // Error
   MSG_DAILY_REPORT   // Daily Report
};

//+------------------------------------------------------------------+
//| Telegram Message Structure                                        |
//+------------------------------------------------------------------+
struct TelegramMessage
{
   string   text;
   string   parseMode;     // "HTML" or "MarkdownV2"
   bool     disablePreview;
   bool     silent;
   
   void Init()
   {
      text = "";
      parseMode = "HTML";
      disablePreview = true;
      silent = false;
   }
};

//+------------------------------------------------------------------+
//| Telegram Class                                                    |
//+------------------------------------------------------------------+
class CTelegram
{
private:
   string   m_BotToken;
   string   m_ChatId;
   string   m_BaseUrl;
   bool     m_Enabled;
   string   m_EAName;
   
   //--- Rate limiting
   datetime m_LastSentTime;
   int      m_MinIntervalSeconds;
   int      m_MessagesSentToday;
   int      m_MaxMessagesPerDay;
   datetime m_LastDayReset;
   
   //--- Queue for rate-limited messages
   TelegramMessage m_Queue[];
   int      m_QueueSize;
   
public:
   //--- Constructor
   CTelegram()
   {
      m_BotToken = "";
      m_ChatId = "";
      m_BaseUrl = "https://api.telegram.org/bot";
      m_Enabled = false;
      m_EAName = "EA";
      m_LastSentTime = 0;
      m_MinIntervalSeconds = 1;
      m_MessagesSentToday = 0;
      m_MaxMessagesPerDay = 100;
      m_LastDayReset = 0;
      m_QueueSize = 50;
      ArrayResize(m_Queue, 0);
   }
   
   //--- Initialize
   bool Init(string botToken, string chatId, string eaName = "EA")
   {
      if(StringLen(botToken) == 0 || StringLen(chatId) == 0)
      {
         Print("Telegram: Bot token or chat ID not provided");
         m_Enabled = false;
         return false;
      }
      
      m_BotToken = botToken;
      m_ChatId = chatId;
      m_EAName = eaName;
      m_Enabled = true;
      
      //--- Test connection
      if(!TestConnection())
      {
         Print("Telegram: Connection test failed");
         m_Enabled = false;
         return false;
      }
      
      Print("Telegram: Initialized successfully");
      return true;
   }
   
   //--- Settings
   void SetEnabled(bool enabled)           { m_Enabled = enabled; }
   void SetMinInterval(int seconds)        { m_MinIntervalSeconds = seconds; }
   void SetMaxMessagesPerDay(int max)      { m_MaxMessagesPerDay = max; }
   bool IsEnabled()                        { return m_Enabled; }
   
   //+------------------------------------------------------------------+
   //| Message Sending                                                   |
   //+------------------------------------------------------------------+
   
   //--- Send raw message
   bool SendMessage(TelegramMessage &msg)
   {
      if(!m_Enabled)
         return false;
      
      //--- Check rate limits
      if(!CheckRateLimits())
      {
         //--- Add to queue
         AddToQueue(msg);
         return false;
      }
      
      //--- Build URL
      string url = m_BaseUrl + m_BotToken + "/sendMessage";
      
      //--- Build JSON body
      string body = "{";
      body += "\"chat_id\":\"" + m_ChatId + "\",";
      body += "\"text\":\"" + EscapeJson(msg.text) + "\",";
      body += "\"parse_mode\":\"" + msg.parseMode + "\",";
      body += "\"disable_web_page_preview\":" + (msg.disablePreview ? "true" : "false") + ",";
      body += "\"disable_notification\":" + (msg.silent ? "true" : "false");
      body += "}";
      
      //--- Send request
      char data[];
      char result[];
      string headers = "Content-Type: application/json\r\n";
      
      StringToCharArray(body, data, 0, StringLen(body), CP_UTF8);
      ArrayResize(data, ArraySize(data) - 1);  // Remove null terminator
      
      int timeout = 5000;
      string resultHeaders;
      
      int res = WebRequest("POST", url, headers, timeout, data, result, resultHeaders);
      
      if(res == -1)
      {
         int error = GetLastError();
         Print("Telegram: WebRequest error: ", error);
         
         if(error == 4014)
            Print("Telegram: Add URL to allowed list in Tools -> Options -> Expert Advisors");
         
         return false;
      }
      
      //--- Check response
      string response = CharArrayToString(result, 0, WHOLE_ARRAY, CP_UTF8);
      
      if(StringFind(response, "\"ok\":true") >= 0)
      {
         m_LastSentTime = TimeCurrent();
         m_MessagesSentToday++;
         return true;
      }
      
      Print("Telegram: Send failed. Response: ", response);
      return false;
   }
   
   //--- Send simple text
   bool Send(string text, bool silent = false)
   {
      TelegramMessage msg;
      msg.Init();
      msg.text = text;
      msg.silent = silent;
      return SendMessage(msg);
   }
   
   //--- Send formatted message
   bool SendFormatted(ENUM_TELEGRAM_MSG_TYPE type, string content)
   {
      string emoji = GetEmoji(type);
      string header = GetHeader(type);
      
      string text = emoji + " <b>" + header + "</b>\n\n" + content;
      text += "\n\n<i>" + m_EAName + " | " + TimeToString(TimeCurrent()) + "</i>";
      
      return Send(text);
   }
   
   //+------------------------------------------------------------------+
   //| Predefined Messages                                               |
   //+------------------------------------------------------------------+
   
   //--- Send trade alert
   bool SendTradeAlert(string action, string symbol, double lots, double price, double sl, double tp)
   {
      string content = StringFormat(
         "<b>%s %s</b>\n"
         "Lots: %.2f\n"
         "Price: %.5f\n"
         "SL: %.5f\n"
         "TP: %.5f",
         action, symbol, lots, price, sl, tp
      );
      
      return SendFormatted(MSG_TRADE, content);
   }
   
   //--- Send signal alert
   bool SendSignalAlert(string symbol, string direction, string reason)
   {
      string content = StringFormat(
         "<b>%s Signal on %s</b>\n\n"
         "Reason: %s\n"
         "Time: %s",
         direction, symbol, reason, TimeToString(TimeCurrent())
      );
      
      return SendFormatted(MSG_SIGNAL, content);
   }
   
   //--- Send error alert
   bool SendErrorAlert(string message)
   {
      return SendFormatted(MSG_ERROR, message);
   }
   
   //--- Send daily report
   bool SendDailyReport(double profit, int trades, double winRate, double drawdown)
   {
      string emoji = (profit >= 0) ? "📈" : "📉";
      
      string content = StringFormat(
         "%s <b>Daily Report</b>\n\n"
         "P/L: %.2f\n"
         "Trades: %d\n"
         "Win Rate: %.1f%%\n"
         "Drawdown: %.2f%%",
         emoji, profit, trades, winRate, drawdown
      );
      
      return SendFormatted(MSG_DAILY_REPORT, content);
   }
   
   //--- Send position update
   bool SendPositionUpdate(string symbol, double profit, string status)
   {
      string emoji = (profit >= 0) ? "✅" : "❌";
      
      string content = StringFormat(
         "%s <b>%s</b>\n"
         "Symbol: %s\n"
         "P/L: %.2f\n"
         "Status: %s",
         emoji, "Position Update", symbol, profit, status
      );
      
      return Send(content);
   }
   
   //+------------------------------------------------------------------+
   //| Utilities                                                         |
   //+------------------------------------------------------------------+
   
   //--- Test connection
   bool TestConnection()
   {
      string url = m_BaseUrl + m_BotToken + "/getMe";
      
      char data[];
      char result[];
      string headers = "";
      string resultHeaders;
      
      int res = WebRequest("GET", url, headers, 5000, data, result, resultHeaders);
      
      if(res == -1)
         return false;
      
      string response = CharArrayToString(result, 0, WHOLE_ARRAY, CP_UTF8);
      return StringFind(response, "\"ok\":true") >= 0;
   }
   
   //--- Check rate limits
   bool CheckRateLimits()
   {
      //--- Reset daily counter
      MqlDateTime dt;
      TimeToStruct(TimeCurrent(), dt);
      datetime today = StringToTime(StringFormat("%d.%d.%d", dt.year, dt.mon, dt.day));
      
      if(today != m_LastDayReset)
      {
         m_LastDayReset = today;
         m_MessagesSentToday = 0;
      }
      
      //--- Check daily limit
      if(m_MessagesSentToday >= m_MaxMessagesPerDay)
         return false;
      
      //--- Check interval
      if(TimeCurrent() - m_LastSentTime < m_MinIntervalSeconds)
         return false;
      
      return true;
   }
   
   //--- Process queue
   void ProcessQueue()
   {
      if(ArraySize(m_Queue) == 0)
         return;
      
      if(!CheckRateLimits())
         return;
      
      //--- Send first message in queue
      TelegramMessage msg = m_Queue[0];
      
      //--- Remove from queue
      for(int i = 0; i < ArraySize(m_Queue) - 1; i++)
         m_Queue[i] = m_Queue[i + 1];
      ArrayResize(m_Queue, ArraySize(m_Queue) - 1);
      
      SendMessage(msg);
   }
   
   //--- Add to queue
   void AddToQueue(TelegramMessage &msg)
   {
      if(ArraySize(m_Queue) >= m_QueueSize)
         return;  // Queue full
      
      int size = ArraySize(m_Queue);
      ArrayResize(m_Queue, size + 1);
      m_Queue[size] = msg;
   }
   
   //--- Get queue size
   int GetQueueSize() { return ArraySize(m_Queue); }
   
private:
   //--- Get emoji for message type
   string GetEmoji(ENUM_TELEGRAM_MSG_TYPE type)
   {
      switch(type)
      {
         case MSG_INFO:         return "ℹ️";
         case MSG_SIGNAL:       return "🔔";
         case MSG_TRADE:        return "💰";
         case MSG_ALERT:        return "⚠️";
         case MSG_ERROR:        return "🚨";
         case MSG_DAILY_REPORT: return "📊";
         default:               return "📌";
      }
   }
   
   //--- Get header for message type
   string GetHeader(ENUM_TELEGRAM_MSG_TYPE type)
   {
      switch(type)
      {
         case MSG_INFO:         return "Information";
         case MSG_SIGNAL:       return "Trading Signal";
         case MSG_TRADE:        return "Trade Execution";
         case MSG_ALERT:        return "Alert";
         case MSG_ERROR:        return "Error";
         case MSG_DAILY_REPORT: return "Daily Report";
         default:               return "Message";
      }
   }
   
   //--- Escape JSON special characters
   string EscapeJson(string text)
   {
      string result = text;
      StringReplace(result, "\\", "\\\\");
      StringReplace(result, "\"", "\\\"");
      StringReplace(result, "\n", "\\n");
      StringReplace(result, "\r", "\\r");
      StringReplace(result, "\t", "\\t");
      return result;
   }
};

//+------------------------------------------------------------------+
//| Global Telegram Instance                                          |
//+------------------------------------------------------------------+
CTelegram g_Telegram;

//+------------------------------------------------------------------+
