//+------------------------------------------------------------------+
//|                                                  News_Filter.mqh |
//|                        Economic event filtering                   |
//|                        Based on Ultimate System v19.0             |
//+------------------------------------------------------------------+
#property copyright   "{{AUTHOR_NAME}}"
#property version     "1.00"

// ═══════════════════════════════════════════════════════════════════
// NEWS IMPACT LEVELS
// ═══════════════════════════════════════════════════════════════════

enum ENUM_NEWS_IMPACT
{
   NEWS_IMPACT_LOW = 1,
   NEWS_IMPACT_MEDIUM = 2,
   NEWS_IMPACT_HIGH = 3
};

// ═══════════════════════════════════════════════════════════════════
// NEWS EVENT STRUCTURE
// ═══════════════════════════════════════════════════════════════════

struct NewsEvent
{
   string            name;
   datetime          time;
   string            currency;
   ENUM_NEWS_IMPACT  impact;
   string            actual;
   string            forecast;
   string            previous;

   void Clear()
   {
      name = "";
      time = 0;
      currency = "";
      impact = NEWS_IMPACT_LOW;
      actual = "";
      forecast = "";
      previous = "";
   }
};

// ═══════════════════════════════════════════════════════════════════
// NEWS FILTER CLASS
// ═══════════════════════════════════════════════════════════════════

class CNewsFilter
{
private:
   // Settings
   bool   m_Enabled;
   int    m_BlackoutBeforeMinutes;  // Minutes before high-impact news
   int    m_BlackoutAfterMinutes;   // Minutes after high-impact news
   int    m_MediumBlackoutBefore;   // Minutes before medium-impact news
   int    m_MediumBlackoutAfter;    // Minutes after medium-impact news
   bool   m_FilterLowImpact;

   // Event storage
   NewsEvent m_Events[];
   int       m_EventCount;
   datetime  m_LastUpdate;

   // High-impact event names
   string m_HighImpactEvents[];

public:
   CNewsFilter()
   {
      m_Enabled = true;
      m_BlackoutBeforeMinutes = 30;
      m_BlackoutAfterMinutes = 15;
      m_MediumBlackoutBefore = 15;
      m_MediumBlackoutAfter = 10;
      m_FilterLowImpact = false;
      m_EventCount = 0;
      m_LastUpdate = 0;

      InitializeHighImpactEvents();
   }

   // ═══════════════════════════════════════════════════════════════
   // CONFIGURATION
   // ═══════════════════════════════════════════════════════════════

   void Enable() { m_Enabled = true; }
   void Disable() { m_Enabled = false; }
   bool IsEnabled() { return m_Enabled; }

   void SetBlackoutPeriod(int beforeMinutes, int afterMinutes)
   {
      m_BlackoutBeforeMinutes = beforeMinutes;
      m_BlackoutAfterMinutes = afterMinutes;
   }

   void SetMediumBlackout(int beforeMinutes, int afterMinutes)
   {
      m_MediumBlackoutBefore = beforeMinutes;
      m_MediumBlackoutAfter = afterMinutes;
   }

   void SetFilterLowImpact(bool filter)
   {
      m_FilterLowImpact = filter;
   }

   // ═══════════════════════════════════════════════════════════════
   // HIGH IMPACT EVENTS
   // ═══════════════════════════════════════════════════════════════

   void InitializeHighImpactEvents()
   {
      ArrayResize(m_HighImpactEvents, 20);
      int i = 0;

      // US Events
      m_HighImpactEvents[i++] = "Non-Farm Payrolls";
      m_HighImpactEvents[i++] = "NFP";
      m_HighImpactEvents[i++] = "FOMC";
      m_HighImpactEvents[i++] = "Fed Interest Rate";
      m_HighImpactEvents[i++] = "CPI";
      m_HighImpactEvents[i++] = "GDP";
      m_HighImpactEvents[i++] = "Retail Sales";
      m_HighImpactEvents[i++] = "ISM Manufacturing";

      // Europe
      m_HighImpactEvents[i++] = "ECB Interest Rate";
      m_HighImpactEvents[i++] = "ECB Press Conference";
      m_HighImpactEvents[i++] = "BOE Interest Rate";

      // Japan
      m_HighImpactEvents[i++] = "BOJ Interest Rate";

      // Australia
      m_HighImpactEvents[i++] = "RBA Interest Rate";

      // Other
      m_HighImpactEvents[i++] = "Central Bank Rate";
      m_HighImpactEvents[i++] = "Employment Change";

      ArrayResize(m_HighImpactEvents, i);
   }

   bool IsHighImpactEvent(string eventName)
   {
      for(int i = 0; i < ArraySize(m_HighImpactEvents); i++)
      {
         if(StringFind(eventName, m_HighImpactEvents[i]) >= 0)
         {
            return true;
         }
      }
      return false;
   }

   // ═══════════════════════════════════════════════════════════════
   // EVENT MANAGEMENT
   // ═══════════════════════════════════════════════════════════════

   void AddEvent(NewsEvent &event)
   {
      int newSize = m_EventCount + 1;
      ArrayResize(m_Events, newSize);
      m_Events[m_EventCount] = event;
      m_EventCount++;
   }

   void ClearEvents()
   {
      ArrayFree(m_Events);
      m_EventCount = 0;
   }

   int GetEventCount() { return m_EventCount; }

   NewsEvent GetEvent(int index)
   {
      NewsEvent empty;
      empty.Clear();

      if(index >= 0 && index < m_EventCount)
      {
         return m_Events[index];
      }
      return empty;
   }

   // Add events for testing/manual input
   void AddManualEvent(string name, datetime time, string currency, ENUM_NEWS_IMPACT impact)
   {
      NewsEvent event;
      event.name = name;
      event.time = time;
      event.currency = currency;
      event.impact = impact;
      AddEvent(event);
   }

   // ═══════════════════════════════════════════════════════════════
   // MAIN FILTER FUNCTIONS
   // ═══════════════════════════════════════════════════════════════

   bool CanTrade(string symbol = "")
   {
      if(!m_Enabled) return true;

      return !IsInBlackoutPeriod(symbol);
   }

   bool IsInBlackoutPeriod(string symbol = "")
   {
      if(!m_Enabled) return false;

      datetime currentTime = TimeCurrent();
      string symbolCurrencies = GetSymbolCurrencies(symbol);

      for(int i = 0; i < m_EventCount; i++)
      {
         NewsEvent event = m_Events[i];

         // Check if event affects the symbol
         if(symbol != "" && StringFind(symbolCurrencies, event.currency) < 0)
         {
            continue;
         }

         // Determine blackout period based on impact
         int beforeMins = 0;
         int afterMins = 0;

         if(event.impact == NEWS_IMPACT_HIGH || IsHighImpactEvent(event.name))
         {
            beforeMins = m_BlackoutBeforeMinutes;
            afterMins = m_BlackoutAfterMinutes;
         }
         else if(event.impact == NEWS_IMPACT_MEDIUM)
         {
            beforeMins = m_MediumBlackoutBefore;
            afterMins = m_MediumBlackoutAfter;
         }
         else if(m_FilterLowImpact)
         {
            beforeMins = 5;
            afterMins = 5;
         }
         else
         {
            continue; // Skip low impact if not filtering
         }

         // Check if currently in blackout
         datetime blackoutStart = event.time - beforeMins * 60;
         datetime blackoutEnd = event.time + afterMins * 60;

         if(currentTime >= blackoutStart && currentTime <= blackoutEnd)
         {
            return true;
         }
      }

      return false;
   }

   // ═══════════════════════════════════════════════════════════════
   // EVENT QUERIES
   // ═══════════════════════════════════════════════════════════════

   bool GetNextEvent(string symbol, NewsEvent &nextEvent)
   {
      datetime currentTime = TimeCurrent();
      datetime nearestTime = D'2099.01.01';
      int nearestIndex = -1;
      string symbolCurrencies = GetSymbolCurrencies(symbol);

      for(int i = 0; i < m_EventCount; i++)
      {
         NewsEvent event = m_Events[i];

         // Must be in the future
         if(event.time <= currentTime) continue;

         // Check if affects symbol
         if(symbol != "" && StringFind(symbolCurrencies, event.currency) < 0)
         {
            continue;
         }

         // Check if nearer
         if(event.time < nearestTime)
         {
            nearestTime = event.time;
            nearestIndex = i;
         }
      }

      if(nearestIndex >= 0)
      {
         nextEvent = m_Events[nearestIndex];
         return true;
      }

      nextEvent.Clear();
      return false;
   }

   int GetMinutesToNextEvent(string symbol = "")
   {
      NewsEvent nextEvent;
      if(GetNextEvent(symbol, nextEvent))
      {
         return (int)((nextEvent.time - TimeCurrent()) / 60);
      }
      return -1;
   }

   bool HasHighImpactWithinMinutes(int minutes, string symbol = "")
   {
      datetime cutoffTime = TimeCurrent() + minutes * 60;
      string symbolCurrencies = GetSymbolCurrencies(symbol);

      for(int i = 0; i < m_EventCount; i++)
      {
         NewsEvent event = m_Events[i];

         if(event.time <= TimeCurrent() || event.time > cutoffTime)
         {
            continue;
         }

         if(symbol != "" && StringFind(symbolCurrencies, event.currency) < 0)
         {
            continue;
         }

         if(event.impact == NEWS_IMPACT_HIGH || IsHighImpactEvent(event.name))
         {
            return true;
         }
      }

      return false;
   }

   // ═══════════════════════════════════════════════════════════════
   // RISK ADJUSTMENT
   // ═══════════════════════════════════════════════════════════════

   double GetRiskMultiplier(string symbol = "")
   {
      if(!m_Enabled) return 1.0;

      int minutesToNews = GetMinutesToNextEvent(symbol);

      // No upcoming news
      if(minutesToNews < 0) return 1.0;

      // Very close to news - reduce risk significantly
      if(minutesToNews <= 30)
      {
         NewsEvent nextEvent;
         if(GetNextEvent(symbol, nextEvent))
         {
            if(nextEvent.impact == NEWS_IMPACT_HIGH || IsHighImpactEvent(nextEvent.name))
            {
               return 0.5;  // 50% risk reduction
            }
            else if(nextEvent.impact == NEWS_IMPACT_MEDIUM)
            {
               return 0.75; // 25% risk reduction
            }
         }
      }
      // Somewhat close to news
      else if(minutesToNews <= 60)
      {
         NewsEvent nextEvent;
         if(GetNextEvent(symbol, nextEvent))
         {
            if(nextEvent.impact == NEWS_IMPACT_HIGH || IsHighImpactEvent(nextEvent.name))
            {
               return 0.75; // 25% risk reduction
            }
         }
      }

      return 1.0;
   }

   // ═══════════════════════════════════════════════════════════════
   // UTILITY FUNCTIONS
   // ═══════════════════════════════════════════════════════════════

   string GetSymbolCurrencies(string symbol)
   {
      if(StringLen(symbol) < 6) return symbol;

      string base = StringSubstr(symbol, 0, 3);
      string quote = StringSubstr(symbol, 3, 3);

      return base + "," + quote;
   }

   string GetBlackoutStatus(string symbol = "")
   {
      if(!m_Enabled) return "Disabled";

      if(IsInBlackoutPeriod(symbol))
      {
         NewsEvent nextEvent;
         if(GetNextEvent(symbol, nextEvent))
         {
            int mins = GetMinutesToNextEvent(symbol);
            if(mins < 0)
            {
               return "BLACKOUT (post-event)";
            }
            return StringFormat("BLACKOUT: %s in %d min", nextEvent.name, mins);
         }
         return "BLACKOUT";
      }

      int minsToNews = GetMinutesToNextEvent(symbol);
      if(minsToNews > 0 && minsToNews <= 60)
      {
         NewsEvent nextEvent;
         GetNextEvent(symbol, nextEvent);
         return StringFormat("CAUTION: %s in %d min", nextEvent.name, minsToNews);
      }

      return "Clear";
   }

   void PrintEvents()
   {
      Print("=== News Events (", m_EventCount, " total) ===");
      for(int i = 0; i < m_EventCount; i++)
      {
         NewsEvent event = m_Events[i];
         string impactStr = (event.impact == NEWS_IMPACT_HIGH) ? "HIGH" :
                           (event.impact == NEWS_IMPACT_MEDIUM) ? "MED" : "LOW";

         Print(TimeToString(event.time), " | ", event.currency, " | ",
               impactStr, " | ", event.name);
      }
   }
};

// ═══════════════════════════════════════════════════════════════════
// CALENDAR LOADER (For MQL5 Calendar API)
// ═══════════════════════════════════════════════════════════════════

class CCalendarLoader
{
private:
   CNewsFilter* m_Filter;

public:
   CCalendarLoader(CNewsFilter* filter)
   {
      m_Filter = filter;
   }

   bool LoadEventsFromCalendar(datetime fromDate, datetime toDate)
   {
      if(m_Filter == NULL) return false;

      m_Filter.ClearEvents();

      // Use MQL5 Calendar API
      MqlCalendarValue values[];
      int count = CalendarValueHistory(values, fromDate, toDate);

      if(count <= 0) return false;

      for(int i = 0; i < count; i++)
      {
         MqlCalendarEvent event;
         if(!CalendarEventById(values[i].event_id, event)) continue;

         MqlCalendarCountry country;
         if(!CalendarCountryById(event.country_id, country)) continue;

         NewsEvent newsEvent;
         newsEvent.name = event.name;
         newsEvent.time = values[i].time;
         newsEvent.currency = country.currency;

         // Convert importance
         if(event.importance == CALENDAR_IMPORTANCE_HIGH)
            newsEvent.impact = NEWS_IMPACT_HIGH;
         else if(event.importance == CALENDAR_IMPORTANCE_MODERATE)
            newsEvent.impact = NEWS_IMPACT_MEDIUM;
         else
            newsEvent.impact = NEWS_IMPACT_LOW;

         // Get values if available
         if(values[i].actual_value != LONG_MIN)
            newsEvent.actual = DoubleToString(values[i].actual_value / 1000000.0, 2);
         if(values[i].forecast_value != LONG_MIN)
            newsEvent.forecast = DoubleToString(values[i].forecast_value / 1000000.0, 2);
         if(values[i].prev_value != LONG_MIN)
            newsEvent.previous = DoubleToString(values[i].prev_value / 1000000.0, 2);

         m_Filter.AddEvent(newsEvent);
      }

      Print("Loaded ", m_Filter.GetEventCount(), " calendar events");
      return true;
   }

   bool LoadTodaysEvents()
   {
      datetime today = StringToTime(TimeToString(TimeCurrent(), TIME_DATE));
      datetime tomorrow = today + 86400;
      return LoadEventsFromCalendar(today, tomorrow);
   }

   bool LoadWeekEvents()
   {
      datetime today = StringToTime(TimeToString(TimeCurrent(), TIME_DATE));
      datetime weekEnd = today + 7 * 86400;
      return LoadEventsFromCalendar(today, weekEnd);
   }
};

//+------------------------------------------------------------------+
