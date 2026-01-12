//+------------------------------------------------------------------+
//|                                                Strategy_Base.mqh |
//|                        Abstract strategy interface                |
//|                        Based on Ultimate System v19.0             |
//+------------------------------------------------------------------+
#property copyright   "{{AUTHOR_NAME}}"
#property version     "1.00"

// ═══════════════════════════════════════════════════════════════════
// SIGNAL TYPES
// ═══════════════════════════════════════════════════════════════════

enum ENUM_SIGNAL_TYPE
{
   SIGNAL_NONE = 0,
   SIGNAL_BUY = 1,
   SIGNAL_SELL = -1,
   SIGNAL_CLOSE_BUY = 2,
   SIGNAL_CLOSE_SELL = -2
};

enum ENUM_SIGNAL_STRENGTH
{
   STRENGTH_WEAK = 1,
   STRENGTH_MODERATE = 2,
   STRENGTH_STRONG = 3
};

// ═══════════════════════════════════════════════════════════════════
// SIGNAL RESULT STRUCTURE
// ═══════════════════════════════════════════════════════════════════

struct SignalResult
{
   ENUM_SIGNAL_TYPE     signal;
   ENUM_SIGNAL_STRENGTH strength;
   double               confidence;     // 0-100
   double               suggestedSL;    // 0 = use default
   double               suggestedTP;    // 0 = use default
   double               suggestedLots;  // 0 = use risk calc
   string               reason;

   void Clear()
   {
      signal = SIGNAL_NONE;
      strength = STRENGTH_MODERATE;
      confidence = 0;
      suggestedSL = 0;
      suggestedTP = 0;
      suggestedLots = 0;
      reason = "";
   }

   bool IsBuy()  { return signal == SIGNAL_BUY; }
   bool IsSell() { return signal == SIGNAL_SELL; }
   bool HasSignal() { return signal != SIGNAL_NONE; }
};

// ═══════════════════════════════════════════════════════════════════
// STRATEGY PARAMETERS
// ═══════════════════════════════════════════════════════════════════

struct StrategyParams
{
   // General
   bool     enabled;
   string   name;
   double   weight;           // For strategy voting (0-1)

   // Risk
   double   riskPercent;
   double   maxPositions;

   // Signal filters
   double   minConfidence;    // Minimum confidence to trade
   double   minADX;           // Minimum ADX for trend strategies

   // Time filters
   bool     useTimeFilter;
   int      startHour;
   int      endHour;

   void SetDefaults()
   {
      enabled = true;
      name = "Strategy";
      weight = 1.0;
      riskPercent = 1.0;
      maxPositions = 1;
      minConfidence = 50;
      minADX = 20;
      useTimeFilter = false;
      startHour = 8;
      endHour = 20;
   }
};

// ═══════════════════════════════════════════════════════════════════
// ABSTRACT STRATEGY BASE CLASS
// ═══════════════════════════════════════════════════════════════════

class CStrategyBase
{
protected:
   string           m_Symbol;
   ENUM_TIMEFRAMES  m_Timeframe;
   StrategyParams   m_Params;
   bool             m_Initialized;

   // Performance tracking
   int              m_TotalSignals;
   int              m_WinningSignals;
   double           m_LastSignalPrice;
   datetime         m_LastSignalTime;

public:
   CStrategyBase()
   {
      m_Symbol = "";
      m_Timeframe = PERIOD_CURRENT;
      m_Initialized = false;
      m_TotalSignals = 0;
      m_WinningSignals = 0;
      m_LastSignalPrice = 0;
      m_LastSignalTime = 0;
      m_Params.SetDefaults();
   }

   virtual ~CStrategyBase() {}

   // ═══════════════════════════════════════════════════════════════
   // ABSTRACT METHODS (Must implement in derived class)
   // ═══════════════════════════════════════════════════════════════

   // Return strategy name
   virtual string GetName() { return m_Params.name; }

   // Return strategy description
   virtual string GetDescription() { return "Base strategy"; }

   // Initialize strategy resources
   virtual bool OnInit() { return true; }

   // Cleanup strategy resources
   virtual void OnDeinit() {}

   // Generate trading signal
   virtual SignalResult GenerateSignal() = 0;

   // ═══════════════════════════════════════════════════════════════
   // INITIALIZATION
   // ═══════════════════════════════════════════════════════════════

   bool Init(string symbol, ENUM_TIMEFRAMES tf, StrategyParams &params)
   {
      m_Symbol = symbol;
      m_Timeframe = tf;
      m_Params = params;

      m_Initialized = OnInit();
      if(m_Initialized)
      {
         Print("Strategy initialized: ", m_Params.name, " on ", symbol, " ", EnumToString(tf));
      }

      return m_Initialized;
   }

   void Deinit()
   {
      OnDeinit();
      m_Initialized = false;
   }

   // ═══════════════════════════════════════════════════════════════
   // GETTERS/SETTERS
   // ═══════════════════════════════════════════════════════════════

   bool IsInitialized() { return m_Initialized; }
   bool IsEnabled() { return m_Params.enabled && m_Initialized; }
   void Enable() { m_Params.enabled = true; }
   void Disable() { m_Params.enabled = false; }

   string GetSymbol() { return m_Symbol; }
   ENUM_TIMEFRAMES GetTimeframe() { return m_Timeframe; }
   double GetWeight() { return m_Params.weight; }
   void SetWeight(double w) { m_Params.weight = w; }

   StrategyParams GetParams() { return m_Params; }
   void SetParams(StrategyParams &params) { m_Params = params; }

   // ═══════════════════════════════════════════════════════════════
   // SIGNAL GENERATION WITH FILTERS
   // ═══════════════════════════════════════════════════════════════

   SignalResult GetSignal()
   {
      SignalResult result;
      result.Clear();

      if(!IsEnabled())
      {
         return result;
      }

      // Time filter
      if(m_Params.useTimeFilter && !IsWithinTradingHours())
      {
         return result;
      }

      // Generate signal from derived class
      result = GenerateSignal();

      // Apply confidence filter
      if(result.HasSignal() && result.confidence < m_Params.minConfidence)
      {
         result.Clear();
         return result;
      }

      // Record signal
      if(result.HasSignal())
      {
         m_TotalSignals++;
         m_LastSignalTime = TimeCurrent();
         m_LastSignalPrice = SymbolInfoDouble(m_Symbol, SYMBOL_BID);
      }

      return result;
   }

   // ═══════════════════════════════════════════════════════════════
   // PERFORMANCE TRACKING
   // ═══════════════════════════════════════════════════════════════

   void RecordWin() { m_WinningSignals++; }
   void RecordLoss() {}

   double GetWinRate()
   {
      if(m_TotalSignals == 0) return 0;
      return (double)m_WinningSignals / m_TotalSignals * 100.0;
   }

   int GetTotalSignals() { return m_TotalSignals; }
   int GetWinningSignals() { return m_WinningSignals; }

   void ResetStats()
   {
      m_TotalSignals = 0;
      m_WinningSignals = 0;
   }

   // ═══════════════════════════════════════════════════════════════
   // UTILITY METHODS
   // ═══════════════════════════════════════════════════════════════

protected:
   bool IsWithinTradingHours()
   {
      MqlDateTime dt;
      TimeCurrent(dt);

      if(dt.hour >= m_Params.startHour && dt.hour < m_Params.endHour)
      {
         return true;
      }
      return false;
   }

   bool IsNewBar()
   {
      static datetime lastBar = 0;
      datetime currentBar = iTime(m_Symbol, m_Timeframe, 0);
      if(currentBar != lastBar)
      {
         lastBar = currentBar;
         return true;
      }
      return false;
   }

   double GetATR(int period, int shift = 1)
   {
      int handle = iATR(m_Symbol, m_Timeframe, period);
      if(handle == INVALID_HANDLE) return 0;

      double buffer[];
      ArraySetAsSeries(buffer, true);
      if(CopyBuffer(handle, 0, shift, 1, buffer) != 1)
      {
         IndicatorRelease(handle);
         return 0;
      }

      IndicatorRelease(handle);
      return buffer[0];
   }
};

// ═══════════════════════════════════════════════════════════════════
// STRATEGY MANAGER (Multi-strategy voting)
// ═══════════════════════════════════════════════════════════════════

class CStrategyManager
{
private:
   CStrategyBase* m_Strategies[];
   int            m_StrategyCount;
   double         m_VoteThreshold;  // 0-1, required consensus

public:
   CStrategyManager()
   {
      m_StrategyCount = 0;
      m_VoteThreshold = 0.5;  // 50% consensus required
   }

   ~CStrategyManager()
   {
      RemoveAll();
   }

   void SetVoteThreshold(double threshold)
   {
      m_VoteThreshold = MathMax(0, MathMin(1, threshold));
   }

   bool AddStrategy(CStrategyBase* strategy)
   {
      if(strategy == NULL) return false;

      int newSize = m_StrategyCount + 1;
      if(ArrayResize(m_Strategies, newSize) != newSize)
      {
         return false;
      }

      m_Strategies[m_StrategyCount] = strategy;
      m_StrategyCount++;

      Print("Strategy added: ", strategy.GetName(), " (total: ", m_StrategyCount, ")");
      return true;
   }

   void RemoveAll()
   {
      for(int i = 0; i < m_StrategyCount; i++)
      {
         if(m_Strategies[i] != NULL)
         {
            m_Strategies[i].Deinit();
            delete m_Strategies[i];
            m_Strategies[i] = NULL;
         }
      }
      ArrayResize(m_Strategies, 0);
      m_StrategyCount = 0;
   }

   int GetStrategyCount() { return m_StrategyCount; }

   CStrategyBase* GetStrategy(int index)
   {
      if(index >= 0 && index < m_StrategyCount)
         return m_Strategies[index];
      return NULL;
   }

   // ═══════════════════════════════════════════════════════════════
   // VOTING SYSTEM
   // ═══════════════════════════════════════════════════════════════

   SignalResult GetConsensusSignal()
   {
      SignalResult consensus;
      consensus.Clear();

      if(m_StrategyCount == 0) return consensus;

      double buyVotes = 0;
      double sellVotes = 0;
      double totalWeight = 0;
      double avgConfidence = 0;
      int signalCount = 0;

      for(int i = 0; i < m_StrategyCount; i++)
      {
         if(m_Strategies[i] == NULL) continue;
         if(!m_Strategies[i].IsEnabled()) continue;

         SignalResult sig = m_Strategies[i].GetSignal();
         double weight = m_Strategies[i].GetWeight();
         totalWeight += weight;

         if(sig.signal == SIGNAL_BUY)
         {
            buyVotes += weight;
            avgConfidence += sig.confidence;
            signalCount++;
         }
         else if(sig.signal == SIGNAL_SELL)
         {
            sellVotes += weight;
            avgConfidence += sig.confidence;
            signalCount++;
         }
      }

      if(totalWeight == 0) return consensus;

      // Calculate vote ratios
      double buyRatio = buyVotes / totalWeight;
      double sellRatio = sellVotes / totalWeight;

      // Check for consensus
      if(buyRatio >= m_VoteThreshold)
      {
         consensus.signal = SIGNAL_BUY;
         consensus.confidence = (signalCount > 0) ? avgConfidence / signalCount : 50;
         consensus.reason = StringFormat("Buy consensus: %.1f%%", buyRatio * 100);
      }
      else if(sellRatio >= m_VoteThreshold)
      {
         consensus.signal = SIGNAL_SELL;
         consensus.confidence = (signalCount > 0) ? avgConfidence / signalCount : 50;
         consensus.reason = StringFormat("Sell consensus: %.1f%%", sellRatio * 100);
      }

      return consensus;
   }

   // Get individual strategy signals for debugging
   void PrintSignals()
   {
      Print("=== Strategy Signals ===");
      for(int i = 0; i < m_StrategyCount; i++)
      {
         if(m_Strategies[i] == NULL) continue;

         SignalResult sig = m_Strategies[i].GetSignal();
         string signalStr = "NONE";
         if(sig.signal == SIGNAL_BUY) signalStr = "BUY";
         else if(sig.signal == SIGNAL_SELL) signalStr = "SELL";

         Print(m_Strategies[i].GetName(), ": ", signalStr,
               " (conf: ", DoubleToString(sig.confidence, 1), "%)");
      }
   }
};

// ═══════════════════════════════════════════════════════════════════
// EXAMPLE: EMA CROSSOVER STRATEGY
// ═══════════════════════════════════════════════════════════════════

class CEMACrossStrategy : public CStrategyBase
{
private:
   int m_HandleFast;
   int m_HandleSlow;
   int m_FastPeriod;
   int m_SlowPeriod;

public:
   CEMACrossStrategy() : CStrategyBase()
   {
      m_Params.name = "EMA Crossover";
      m_FastPeriod = 9;
      m_SlowPeriod = 21;
      m_HandleFast = INVALID_HANDLE;
      m_HandleSlow = INVALID_HANDLE;
   }

   void SetPeriods(int fast, int slow)
   {
      m_FastPeriod = fast;
      m_SlowPeriod = slow;
   }

   virtual string GetDescription() override
   {
      return StringFormat("EMA Crossover (%d/%d)", m_FastPeriod, m_SlowPeriod);
   }

   virtual bool OnInit() override
   {
      m_HandleFast = iMA(m_Symbol, m_Timeframe, m_FastPeriod, 0, MODE_EMA, PRICE_CLOSE);
      m_HandleSlow = iMA(m_Symbol, m_Timeframe, m_SlowPeriod, 0, MODE_EMA, PRICE_CLOSE);

      return (m_HandleFast != INVALID_HANDLE && m_HandleSlow != INVALID_HANDLE);
   }

   virtual void OnDeinit() override
   {
      if(m_HandleFast != INVALID_HANDLE) IndicatorRelease(m_HandleFast);
      if(m_HandleSlow != INVALID_HANDLE) IndicatorRelease(m_HandleSlow);
   }

   virtual SignalResult GenerateSignal() override
   {
      SignalResult result;
      result.Clear();

      double fast[], slow[];
      ArraySetAsSeries(fast, true);
      ArraySetAsSeries(slow, true);

      if(CopyBuffer(m_HandleFast, 0, 0, 3, fast) != 3) return result;
      if(CopyBuffer(m_HandleSlow, 0, 0, 3, slow) != 3) return result;

      // Golden cross (fast crosses above slow)
      if(fast[1] > slow[1] && fast[2] <= slow[2])
      {
         result.signal = SIGNAL_BUY;
         result.confidence = 70;
         result.reason = "Golden cross";
      }
      // Death cross (fast crosses below slow)
      else if(fast[1] < slow[1] && fast[2] >= slow[2])
      {
         result.signal = SIGNAL_SELL;
         result.confidence = 70;
         result.reason = "Death cross";
      }

      return result;
   }
};

//+------------------------------------------------------------------+
