//+------------------------------------------------------------------+
//|                                               Session_Filter.mqh |
//|                        Trading session time management            |
//|                        Based on Ultimate System v19.0             |
//+------------------------------------------------------------------+
#property copyright   "{{AUTHOR_NAME}}"
#property version     "1.00"

// ═══════════════════════════════════════════════════════════════════
// SESSION TYPES
// ═══════════════════════════════════════════════════════════════════

enum ENUM_TRADING_SESSION
{
   SESSION_SYDNEY = 0,
   SESSION_TOKYO = 1,
   SESSION_LONDON = 2,
   SESSION_NEW_YORK = 3,
   SESSION_OVERLAP_LONDON_NY = 4,
   SESSION_OVERLAP_TOKYO_LONDON = 5
};

// ═══════════════════════════════════════════════════════════════════
// SESSION INFO STRUCTURE
// ═══════════════════════════════════════════════════════════════════

struct SessionInfo
{
   string name;
   int    startHour;   // GMT
   int    endHour;     // GMT
   double volatilityMultiplier;
   string bestPairs[];

   void Clear()
   {
      name = "";
      startHour = 0;
      endHour = 0;
      volatilityMultiplier = 1.0;
      ArrayFree(bestPairs);
   }
};

// ═══════════════════════════════════════════════════════════════════
// SESSION FILTER CLASS
// ═══════════════════════════════════════════════════════════════════

class CSessionFilter
{
private:
   // Session settings
   bool m_TradeSydney;
   bool m_TradeTokyo;
   bool m_TradeLondon;
   bool m_TradeNewYork;
   bool m_TradeSunday;
   bool m_TradeFriday;

   // Custom hours
   int  m_CustomStartHour;
   int  m_CustomEndHour;
   bool m_UseCustomHours;

   // Broker time offset from GMT
   int  m_BrokerGMTOffset;

   // Session definitions (GMT)
   SessionInfo m_Sessions[];

public:
   CSessionFilter()
   {
      m_TradeSydney = false;
      m_TradeTokyo = true;
      m_TradeLondon = true;
      m_TradeNewYork = true;
      m_TradeSunday = false;
      m_TradeFriday = true;
      m_CustomStartHour = 0;
      m_CustomEndHour = 24;
      m_UseCustomHours = false;
      m_BrokerGMTOffset = 0;

      InitializeSessions();
   }

   // ═══════════════════════════════════════════════════════════════
   // INITIALIZATION
   // ═══════════════════════════════════════════════════════════════

   void InitializeSessions()
   {
      ArrayResize(m_Sessions, 6);

      // Sydney Session (22:00 - 07:00 GMT)
      m_Sessions[SESSION_SYDNEY].name = "Sydney";
      m_Sessions[SESSION_SYDNEY].startHour = 22;
      m_Sessions[SESSION_SYDNEY].endHour = 7;
      m_Sessions[SESSION_SYDNEY].volatilityMultiplier = 0.7;

      // Tokyo Session (00:00 - 09:00 GMT)
      m_Sessions[SESSION_TOKYO].name = "Tokyo";
      m_Sessions[SESSION_TOKYO].startHour = 0;
      m_Sessions[SESSION_TOKYO].endHour = 9;
      m_Sessions[SESSION_TOKYO].volatilityMultiplier = 0.8;

      // London Session (08:00 - 17:00 GMT)
      m_Sessions[SESSION_LONDON].name = "London";
      m_Sessions[SESSION_LONDON].startHour = 8;
      m_Sessions[SESSION_LONDON].endHour = 17;
      m_Sessions[SESSION_LONDON].volatilityMultiplier = 1.0;

      // New York Session (13:00 - 22:00 GMT)
      m_Sessions[SESSION_NEW_YORK].name = "New York";
      m_Sessions[SESSION_NEW_YORK].startHour = 13;
      m_Sessions[SESSION_NEW_YORK].endHour = 22;
      m_Sessions[SESSION_NEW_YORK].volatilityMultiplier = 1.0;

      // London-NY Overlap (13:00 - 17:00 GMT)
      m_Sessions[SESSION_OVERLAP_LONDON_NY].name = "London-NY Overlap";
      m_Sessions[SESSION_OVERLAP_LONDON_NY].startHour = 13;
      m_Sessions[SESSION_OVERLAP_LONDON_NY].endHour = 17;
      m_Sessions[SESSION_OVERLAP_LONDON_NY].volatilityMultiplier = 1.3;

      // Tokyo-London Overlap (08:00 - 09:00 GMT)
      m_Sessions[SESSION_OVERLAP_TOKYO_LONDON].name = "Tokyo-London Overlap";
      m_Sessions[SESSION_OVERLAP_TOKYO_LONDON].startHour = 8;
      m_Sessions[SESSION_OVERLAP_TOKYO_LONDON].endHour = 9;
      m_Sessions[SESSION_OVERLAP_TOKYO_LONDON].volatilityMultiplier = 1.1;
   }

   // ═══════════════════════════════════════════════════════════════
   // CONFIGURATION
   // ═══════════════════════════════════════════════════════════════

   void SetSessionTrading(bool sydney, bool tokyo, bool london, bool newyork)
   {
      m_TradeSydney = sydney;
      m_TradeTokyo = tokyo;
      m_TradeLondon = london;
      m_TradeNewYork = newyork;
   }

   void SetDayTrading(bool sunday, bool friday)
   {
      m_TradeSunday = sunday;
      m_TradeFriday = friday;
   }

   void SetCustomHours(int startHour, int endHour)
   {
      m_CustomStartHour = startHour;
      m_CustomEndHour = endHour;
      m_UseCustomHours = true;
   }

   void DisableCustomHours()
   {
      m_UseCustomHours = false;
   }

   void SetBrokerGMTOffset(int offset)
   {
      m_BrokerGMTOffset = offset;
   }

   // Auto-detect broker GMT offset
   void DetectBrokerOffset()
   {
      // This is a simplified detection - may need adjustment
      datetime serverTime = TimeCurrent();
      datetime gmtTime = TimeGMT();

      m_BrokerGMTOffset = (int)((serverTime - gmtTime) / 3600);
   }

   // ═══════════════════════════════════════════════════════════════
   // MAIN FILTER FUNCTION
   // ═══════════════════════════════════════════════════════════════

   bool CanTradeNow()
   {
      // Check day of week
      if(!IsTradingDay())
      {
         return false;
      }

      // Check custom hours if enabled
      if(m_UseCustomHours)
      {
         return IsWithinCustomHours();
      }

      // Check session hours
      return IsWithinAllowedSessions();
   }

   // ═══════════════════════════════════════════════════════════════
   // DAY CHECKS
   // ═══════════════════════════════════════════════════════════════

   bool IsTradingDay()
   {
      MqlDateTime dt;
      TimeCurrent(dt);

      // Saturday - never trade
      if(dt.day_of_week == 6) return false;

      // Sunday
      if(dt.day_of_week == 0 && !m_TradeSunday) return false;

      // Friday (with possible early close)
      if(dt.day_of_week == 5 && !m_TradeFriday) return false;

      return true;
   }

   bool IsFridayLateClose()
   {
      MqlDateTime dt;
      TimeCurrent(dt);

      // Friday after 21:00 GMT - market closing
      if(dt.day_of_week == 5)
      {
         int gmtHour = GetCurrentGMTHour();
         return (gmtHour >= 21);
      }
      return false;
   }

   bool IsSundayEarlyOpen()
   {
      MqlDateTime dt;
      TimeCurrent(dt);

      // Sunday before 22:00 GMT - market not fully open
      if(dt.day_of_week == 0)
      {
         int gmtHour = GetCurrentGMTHour();
         return (gmtHour < 22);
      }
      return false;
   }

   // ═══════════════════════════════════════════════════════════════
   // SESSION CHECKS
   // ═══════════════════════════════════════════════════════════════

   bool IsWithinAllowedSessions()
   {
      if(m_TradeSydney && IsSessionActive(SESSION_SYDNEY)) return true;
      if(m_TradeTokyo && IsSessionActive(SESSION_TOKYO)) return true;
      if(m_TradeLondon && IsSessionActive(SESSION_LONDON)) return true;
      if(m_TradeNewYork && IsSessionActive(SESSION_NEW_YORK)) return true;

      return false;
   }

   bool IsSessionActive(ENUM_TRADING_SESSION session)
   {
      if(session < 0 || session >= ArraySize(m_Sessions)) return false;

      int gmtHour = GetCurrentGMTHour();
      int start = m_Sessions[session].startHour;
      int end = m_Sessions[session].endHour;

      // Handle sessions that cross midnight
      if(start > end)
      {
         return (gmtHour >= start || gmtHour < end);
      }
      else
      {
         return (gmtHour >= start && gmtHour < end);
      }
   }

   ENUM_TRADING_SESSION GetCurrentSession()
   {
      // Check overlaps first
      if(IsSessionActive(SESSION_OVERLAP_LONDON_NY))
         return SESSION_OVERLAP_LONDON_NY;
      if(IsSessionActive(SESSION_OVERLAP_TOKYO_LONDON))
         return SESSION_OVERLAP_TOKYO_LONDON;

      // Then main sessions
      if(IsSessionActive(SESSION_LONDON)) return SESSION_LONDON;
      if(IsSessionActive(SESSION_NEW_YORK)) return SESSION_NEW_YORK;
      if(IsSessionActive(SESSION_TOKYO)) return SESSION_TOKYO;
      if(IsSessionActive(SESSION_SYDNEY)) return SESSION_SYDNEY;

      return SESSION_SYDNEY; // Default
   }

   string GetCurrentSessionName()
   {
      ENUM_TRADING_SESSION session = GetCurrentSession();
      return m_Sessions[session].name;
   }

   double GetSessionVolatilityMultiplier()
   {
      ENUM_TRADING_SESSION session = GetCurrentSession();
      return m_Sessions[session].volatilityMultiplier;
   }

   bool IsHighVolatilityPeriod()
   {
      return IsSessionActive(SESSION_OVERLAP_LONDON_NY) ||
             (IsSessionActive(SESSION_LONDON) && IsSessionActive(SESSION_NEW_YORK));
   }

   // ═══════════════════════════════════════════════════════════════
   // CUSTOM HOURS
   // ═══════════════════════════════════════════════════════════════

   bool IsWithinCustomHours()
   {
      int gmtHour = GetCurrentGMTHour();

      if(m_CustomStartHour < m_CustomEndHour)
      {
         return (gmtHour >= m_CustomStartHour && gmtHour < m_CustomEndHour);
      }
      else // Crosses midnight
      {
         return (gmtHour >= m_CustomStartHour || gmtHour < m_CustomEndHour);
      }
   }

   // ═══════════════════════════════════════════════════════════════
   // TIME HELPERS
   // ═══════════════════════════════════════════════════════════════

   int GetCurrentGMTHour()
   {
      MqlDateTime dt;
      TimeCurrent(dt);
      int gmtHour = dt.hour - m_BrokerGMTOffset;

      // Normalize to 0-23
      if(gmtHour < 0) gmtHour += 24;
      if(gmtHour >= 24) gmtHour -= 24;

      return gmtHour;
   }

   datetime GetNextSessionStart(ENUM_TRADING_SESSION session)
   {
      if(session < 0 || session >= ArraySize(m_Sessions)) return 0;

      int targetHour = m_Sessions[session].startHour + m_BrokerGMTOffset;
      if(targetHour >= 24) targetHour -= 24;
      if(targetHour < 0) targetHour += 24;

      MqlDateTime dt;
      TimeCurrent(dt);

      if(dt.hour >= targetHour)
      {
         // Next day
         dt.day++;
      }
      dt.hour = targetHour;
      dt.min = 0;
      dt.sec = 0;

      return StructToTime(dt);
   }

   int GetMinutesToSessionStart(ENUM_TRADING_SESSION session)
   {
      datetime nextStart = GetNextSessionStart(session);
      if(nextStart == 0) return -1;

      return (int)((nextStart - TimeCurrent()) / 60);
   }

   // ═══════════════════════════════════════════════════════════════
   // INFO
   // ═══════════════════════════════════════════════════════════════

   string GetStatusString()
   {
      string status = "Session: " + GetCurrentSessionName();
      status += " | Can Trade: " + (CanTradeNow() ? "YES" : "NO");
      status += " | Volatility: " + DoubleToString(GetSessionVolatilityMultiplier(), 1) + "x";
      return status;
   }

   void PrintSessionInfo()
   {
      Print("=== Session Information ===");
      Print("Current GMT Hour: ", GetCurrentGMTHour());
      Print("Current Session: ", GetCurrentSessionName());
      Print("Can Trade Now: ", CanTradeNow() ? "YES" : "NO");
      Print("Volatility Multiplier: ", GetSessionVolatilityMultiplier());
      Print("High Volatility Period: ", IsHighVolatilityPeriod() ? "YES" : "NO");

      Print("Session Status:");
      Print("  Sydney:   ", IsSessionActive(SESSION_SYDNEY) ? "ACTIVE" : "closed");
      Print("  Tokyo:    ", IsSessionActive(SESSION_TOKYO) ? "ACTIVE" : "closed");
      Print("  London:   ", IsSessionActive(SESSION_LONDON) ? "ACTIVE" : "closed");
      Print("  New York: ", IsSessionActive(SESSION_NEW_YORK) ? "ACTIVE" : "closed");
   }
};

//+------------------------------------------------------------------+
