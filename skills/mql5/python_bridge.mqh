//+------------------------------------------------------------------+
//|                                                Python_Bridge.mqh |
//|                        ML API integration via HTTP/WebSocket      |
//|                        Based on Ultimate System v19.0             |
//+------------------------------------------------------------------+
#property copyright   "{{AUTHOR_NAME}}"
#property version     "1.00"

// ═══════════════════════════════════════════════════════════════════
// SIGNAL RESPONSE STRUCTURE
// ═══════════════════════════════════════════════════════════════════

struct MLSignalResponse
{
   bool     success;
   string   symbol;
   string   direction;    // "BUY", "SELL", "NEUTRAL"
   double   confidence;   // 0-100
   double   suggestedSL;
   double   suggestedTP;
   string   regime;       // "TRENDING", "RANGING", "VOLATILE"
   string   reason;
   datetime timestamp;

   void Clear()
   {
      success = false;
      symbol = "";
      direction = "NEUTRAL";
      confidence = 0;
      suggestedSL = 0;
      suggestedTP = 0;
      regime = "";
      reason = "";
      timestamp = 0;
   }

   bool IsBuy() { return direction == "BUY"; }
   bool IsSell() { return direction == "SELL"; }
   bool IsNeutral() { return direction == "NEUTRAL"; }
};

// ═══════════════════════════════════════════════════════════════════
// DYNAMIC PARAMS STRUCTURE
// ═══════════════════════════════════════════════════════════════════

struct DynamicParams
{
   double minSignalStrength;
   double slATRMultiplier;
   double tpATRMultiplier;
   double trailingStopATR;
   double breakEvenATR;
   double activationATR;
   string sessionFilter;  // "all", "london_ny", etc.
   bool   enabled;

   void SetDefaults()
   {
      minSignalStrength = 0.65;
      slATRMultiplier = 2.0;
      tpATRMultiplier = 3.0;
      trailingStopATR = 1.5;
      breakEvenATR = 1.0;
      activationATR = 1.0;
      sessionFilter = "all";
      enabled = true;
   }
};

// ═══════════════════════════════════════════════════════════════════
// PYTHON BRIDGE CLASS
// ═══════════════════════════════════════════════════════════════════

class CPythonBridge
{
private:
   string   m_BaseURL;
   int      m_Timeout;
   string   m_LastError;
   bool     m_Connected;
   datetime m_LastCheck;
   int      m_CheckInterval;

   // Cache
   MLSignalResponse m_CachedSignal;
   datetime         m_CacheTime;
   int              m_CacheTTL;  // Seconds

public:
   CPythonBridge()
   {
      m_BaseURL = "http://localhost:5050";
      m_Timeout = 5000;  // 5 seconds
      m_LastError = "";
      m_Connected = false;
      m_LastCheck = 0;
      m_CheckInterval = 60;  // Check connection every 60 seconds
      m_CacheTime = 0;
      m_CacheTTL = 30;  // Cache signal for 30 seconds
   }

   // ═══════════════════════════════════════════════════════════════
   // CONFIGURATION
   // ═══════════════════════════════════════════════════════════════

   void SetBaseURL(string url) { m_BaseURL = url; }
   void SetTimeout(int ms) { m_Timeout = ms; }
   void SetCacheTTL(int seconds) { m_CacheTTL = seconds; }

   string GetBaseURL() { return m_BaseURL; }
   string GetLastError() { return m_LastError; }
   bool IsConnected() { return m_Connected; }

   // ═══════════════════════════════════════════════════════════════
   // CONNECTION CHECK
   // ═══════════════════════════════════════════════════════════════

   bool CheckConnection(bool force = false)
   {
      datetime now = TimeCurrent();

      // Use cached result if not forcing and within check interval
      if(!force && (now - m_LastCheck) < m_CheckInterval)
      {
         return m_Connected;
      }

      m_LastCheck = now;

      // Try health endpoint
      string response = HttpGet("/health");
      if(response == "")
      {
         m_Connected = false;
         return false;
      }

      // Check for success in response
      if(StringFind(response, "healthy") >= 0 ||
         StringFind(response, "\"status\"") >= 0)
      {
         m_Connected = true;
         return true;
      }

      m_Connected = false;
      return false;
   }

   // ═══════════════════════════════════════════════════════════════
   // SIGNAL REQUESTS
   // ═══════════════════════════════════════════════════════════════

   bool GetMLSignal(string symbol, MLSignalResponse &signal)
   {
      signal.Clear();

      // Check cache first
      if(TimeCurrent() - m_CacheTime < m_CacheTTL &&
         m_CachedSignal.symbol == symbol)
      {
         signal = m_CachedSignal;
         return signal.success;
      }

      // Check connection
      if(!CheckConnection())
      {
         m_LastError = "Not connected to ML API";
         return false;
      }

      // Build request
      string endpoint = StringFormat("/v3/predict/signal/profitable?symbol=%s", symbol);
      string response = HttpGet(endpoint);

      if(response == "")
      {
         return false;
      }

      // Parse response
      if(!ParseSignalResponse(response, signal))
      {
         return false;
      }

      // Update cache
      m_CachedSignal = signal;
      m_CacheTime = TimeCurrent();

      return signal.success;
   }

   bool GetSignalWithTimeframe(string symbol, ENUM_TIMEFRAMES tf, MLSignalResponse &signal)
   {
      signal.Clear();

      if(!CheckConnection())
      {
         m_LastError = "Not connected to ML API";
         return false;
      }

      string tfStr = TimeframeToString(tf);
      string endpoint = StringFormat("/v2/predict/signal/mtf?symbol=%s&timeframe=%s", symbol, tfStr);
      string response = HttpGet(endpoint);

      if(response == "")
      {
         return false;
      }

      return ParseSignalResponse(response, signal);
   }

   // ═══════════════════════════════════════════════════════════════
   // DYNAMIC PARAMETERS
   // ═══════════════════════════════════════════════════════════════

   bool FetchDynamicParams(string symbol, DynamicParams &params)
   {
      params.SetDefaults();

      if(!CheckConnection())
      {
         return false;
      }

      string endpoint = StringFormat("/params/dynamic/%s", symbol);
      string response = HttpGet(endpoint);

      if(response == "")
      {
         return false;
      }

      return ParseDynamicParams(response, params);
   }

   bool FetchMLRecommendedParams(string symbol, DynamicParams &params)
   {
      params.SetDefaults();

      if(!CheckConnection())
      {
         return false;
      }

      string response = HttpGet("/params/ml-recommended");

      if(response == "")
      {
         return false;
      }

      // Parse and find symbol-specific params
      return ParseMLRecommendedParams(response, symbol, params);
   }

   // ═══════════════════════════════════════════════════════════════
   // TRADE NOTIFICATIONS
   // ═══════════════════════════════════════════════════════════════

   bool NotifyTradeOpen(string symbol, string direction, double volume,
                        double entry, double sl, double tp, ulong ticket,
                        double confidence = 0, string regime = "")
   {
      if(!CheckConnection())
      {
         return false;
      }

      // Build JSON payload
      string json = StringFormat(
         "{\"symbol\":\"%s\",\"direction\":\"%s\",\"volume\":%.2f,"
         "\"entry\":%.5f,\"sl\":%.5f,\"tp\":%.5f,\"ticket\":%I64u,"
         "\"confidence\":%.1f,\"regime\":\"%s\"}",
         symbol, direction, volume, entry, sl, tp, ticket, confidence, regime
      );

      string response = HttpPost("/mt5/trade-event", json);
      return (response != "" && StringFind(response, "error") < 0);
   }

   bool NotifyTradeClose(string symbol, string direction, double volume,
                         double profit, ulong ticket)
   {
      if(!CheckConnection())
      {
         return false;
      }

      string json = StringFormat(
         "{\"symbol\":\"%s\",\"direction\":\"%s\",\"volume\":%.2f,"
         "\"profit\":%.2f,\"ticket\":%I64u,\"event\":\"CLOSE\"}",
         symbol, direction, volume, profit, ticket
      );

      string response = HttpPost("/mt5/trade-event", json);
      return (response != "" && StringFind(response, "error") < 0);
   }

   // ═══════════════════════════════════════════════════════════════
   // HTTP HELPERS
   // ═══════════════════════════════════════════════════════════════

private:
   string HttpGet(string endpoint)
   {
      string url = m_BaseURL + endpoint;
      string headers = "Content-Type: application/json\r\n";
      char data[];
      char result[];
      string resultHeaders;

      int res = WebRequest("GET", url, headers, m_Timeout, data, result, resultHeaders);

      if(res == -1)
      {
         int error = GetLastError();
         m_LastError = StringFormat("WebRequest failed: %d", error);
         if(error == 4060)
         {
            m_LastError += " (URL not allowed - add to MT5 Options > Expert Advisors)";
         }
         return "";
      }

      if(res != 200)
      {
         m_LastError = StringFormat("HTTP %d: %s", res, CharArrayToString(result));
         return "";
      }

      return CharArrayToString(result);
   }

   string HttpPost(string endpoint, string jsonBody)
   {
      string url = m_BaseURL + endpoint;
      string headers = "Content-Type: application/json\r\n";
      char data[];
      char result[];
      string resultHeaders;

      StringToCharArray(jsonBody, data, 0, WHOLE_ARRAY, CP_UTF8);
      ArrayResize(data, ArraySize(data) - 1);  // Remove null terminator

      int res = WebRequest("POST", url, headers, m_Timeout, data, result, resultHeaders);

      if(res == -1)
      {
         m_LastError = StringFormat("WebRequest failed: %d", GetLastError());
         return "";
      }

      if(res != 200 && res != 201)
      {
         m_LastError = StringFormat("HTTP %d", res);
         return "";
      }

      return CharArrayToString(result);
   }

   // ═══════════════════════════════════════════════════════════════
   // JSON PARSING HELPERS
   // ═══════════════════════════════════════════════════════════════

   bool ParseSignalResponse(string json, MLSignalResponse &signal)
   {
      signal.Clear();

      // Check for success
      if(StringFind(json, "\"success\":true") < 0 &&
         StringFind(json, "\"success\": true") < 0)
      {
         signal.success = false;
         return false;
      }

      signal.success = true;
      signal.timestamp = TimeCurrent();

      // Parse direction
      if(StringFind(json, "\"BUY\"") >= 0 || StringFind(json, "\"direction\":\"BUY\"") >= 0)
         signal.direction = "BUY";
      else if(StringFind(json, "\"SELL\"") >= 0 || StringFind(json, "\"direction\":\"SELL\"") >= 0)
         signal.direction = "SELL";
      else
         signal.direction = "NEUTRAL";

      // Parse confidence
      signal.confidence = ExtractDouble(json, "confidence");
      if(signal.confidence == 0)
         signal.confidence = ExtractDouble(json, "signal_strength") * 100;

      // Parse SL/TP if present
      signal.suggestedSL = ExtractDouble(json, "sl");
      signal.suggestedTP = ExtractDouble(json, "tp");

      // Parse regime
      signal.regime = ExtractString(json, "regime");

      // Parse reason
      signal.reason = ExtractString(json, "reason");
      if(signal.reason == "")
         signal.reason = ExtractString(json, "message");

      return true;
   }

   bool ParseDynamicParams(string json, DynamicParams &params)
   {
      params.SetDefaults();

      double val = ExtractDouble(json, "minSignalStrength");
      if(val > 0) params.minSignalStrength = val;

      val = ExtractDouble(json, "slATRMultiplier");
      if(val > 0) params.slATRMultiplier = val;

      val = ExtractDouble(json, "tpATRMultiplier");
      if(val > 0) params.tpATRMultiplier = val;

      val = ExtractDouble(json, "trailingStopATR");
      if(val > 0) params.trailingStopATR = val;

      val = ExtractDouble(json, "breakEvenATR");
      if(val > 0) params.breakEvenATR = val;

      params.sessionFilter = ExtractString(json, "sessionFilter");
      if(params.sessionFilter == "") params.sessionFilter = "all";

      params.enabled = (StringFind(json, "\"enabled\":false") < 0);

      return true;
   }

   bool ParseMLRecommendedParams(string json, string symbol, DynamicParams &params)
   {
      // Find symbol section in JSON
      int symbolPos = StringFind(json, "\"" + symbol + "\"");
      if(symbolPos < 0)
      {
         return false;
      }

      // Extract symbol's JSON section
      int braceStart = StringFind(json, "{", symbolPos);
      if(braceStart < 0) return false;

      int braceEnd = StringFind(json, "}", braceStart);
      if(braceEnd < 0) return false;

      string symbolJson = StringSubstr(json, braceStart, braceEnd - braceStart + 1);

      return ParseDynamicParams(symbolJson, params);
   }

   // Simple JSON value extractors
   double ExtractDouble(string json, string key)
   {
      string searchKey = "\"" + key + "\":";
      int pos = StringFind(json, searchKey);
      if(pos < 0)
      {
         searchKey = "\"" + key + "\": ";
         pos = StringFind(json, searchKey);
      }
      if(pos < 0) return 0;

      pos += StringLen(searchKey);

      // Skip whitespace
      while(pos < StringLen(json) && StringGetCharacter(json, pos) == ' ')
         pos++;

      // Find end of number
      int endPos = pos;
      while(endPos < StringLen(json))
      {
         ushort ch = StringGetCharacter(json, endPos);
         if((ch >= '0' && ch <= '9') || ch == '.' || ch == '-')
            endPos++;
         else
            break;
      }

      string numStr = StringSubstr(json, pos, endPos - pos);
      return StringToDouble(numStr);
   }

   string ExtractString(string json, string key)
   {
      string searchKey = "\"" + key + "\":\"";
      int pos = StringFind(json, searchKey);
      if(pos < 0)
      {
         searchKey = "\"" + key + "\": \"";
         pos = StringFind(json, searchKey);
      }
      if(pos < 0) return "";

      pos += StringLen(searchKey);

      int endPos = StringFind(json, "\"", pos);
      if(endPos < 0) return "";

      return StringSubstr(json, pos, endPos - pos);
   }

   string TimeframeToString(ENUM_TIMEFRAMES tf)
   {
      switch(tf)
      {
         case PERIOD_M1:  return "M1";
         case PERIOD_M5:  return "M5";
         case PERIOD_M15: return "M15";
         case PERIOD_M30: return "M30";
         case PERIOD_H1:  return "H1";
         case PERIOD_H4:  return "H4";
         case PERIOD_D1:  return "D1";
         case PERIOD_W1:  return "W1";
         case PERIOD_MN1: return "MN1";
         default:         return "H1";
      }
   }
};

//+------------------------------------------------------------------+
