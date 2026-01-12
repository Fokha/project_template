//+------------------------------------------------------------------+
//|                                               Strategy_Base.mqh  |
//|                                       Strategy Base Class v1.0   |
//|                        Abstract base for trading strategies      |
//+------------------------------------------------------------------+
#property copyright "Your Name"
#property link      "https://www.example.com"
#property version   "1.00"
#property strict

#include <Trade\SymbolInfo.mqh>

//+------------------------------------------------------------------+
//| Signal Types                                                      |
//+------------------------------------------------------------------+
enum ENUM_SIGNAL
{
   SIGNAL_NONE = 0,     // No Signal
   SIGNAL_BUY,          // Buy Signal
   SIGNAL_SELL,         // Sell Signal
   SIGNAL_CLOSE_BUY,    // Close Buy
   SIGNAL_CLOSE_SELL    // Close Sell
};

//+------------------------------------------------------------------+
//| Signal Strength                                                   |
//+------------------------------------------------------------------+
enum ENUM_SIGNAL_STRENGTH
{
   STRENGTH_WEAK = 1,      // Weak
   STRENGTH_MODERATE = 2,  // Moderate  
   STRENGTH_STRONG = 3     // Strong
};

//+------------------------------------------------------------------+
//| Signal Structure                                                  |
//+------------------------------------------------------------------+
struct Signal
{
   ENUM_SIGNAL        type;
   ENUM_SIGNAL_STRENGTH strength;
   double             confidence;    // 0-100
   double             stopLoss;
   double             takeProfit;
   string             reason;
   datetime           time;
   
   void Clear()
   {
      type = SIGNAL_NONE;
      strength = STRENGTH_WEAK;
      confidence = 0;
      stopLoss = 0;
      takeProfit = 0;
      reason = "";
      time = 0;
   }
   
   void SetBuy(double conf, ENUM_SIGNAL_STRENGTH str, string rsn)
   {
      type = SIGNAL_BUY;
      strength = str;
      confidence = conf;
      reason = rsn;
      time = TimeCurrent();
   }
   
   void SetSell(double conf, ENUM_SIGNAL_STRENGTH str, string rsn)
   {
      type = SIGNAL_SELL;
      strength = str;
      confidence = conf;
      reason = rsn;
      time = TimeCurrent();
   }
   
   bool IsValid()
   {
      return type != SIGNAL_NONE && confidence >= 50;
   }
   
   string ToString()
   {
      string typeStr = "NONE";
      switch(type)
      {
         case SIGNAL_BUY:        typeStr = "BUY"; break;
         case SIGNAL_SELL:       typeStr = "SELL"; break;
         case SIGNAL_CLOSE_BUY:  typeStr = "CLOSE_BUY"; break;
         case SIGNAL_CLOSE_SELL: typeStr = "CLOSE_SELL"; break;
      }
      return StringFormat("%s (%.0f%%) - %s", typeStr, confidence, reason);
   }
};

//+------------------------------------------------------------------+
//| Strategy Parameters Structure                                     |
//+------------------------------------------------------------------+
struct StrategyParams
{
   //--- General
   string   name;
   string   symbol;
   ENUM_TIMEFRAMES timeframe;
   
   //--- Risk
   double   riskPercent;
   double   slMultiplier;
   double   tpMultiplier;
   
   //--- Filters
   double   minConfidence;
   int      minStrength;
   bool     requireTrendAlignment;
   
   void SetDefaults()
   {
      name = "Strategy";
      symbol = _Symbol;
      timeframe = PERIOD_CURRENT;
      riskPercent = 1.0;
      slMultiplier = 1.5;
      tpMultiplier = 2.0;
      minConfidence = 60;
      minStrength = STRENGTH_MODERATE;
      requireTrendAlignment = true;
   }
};

//+------------------------------------------------------------------+
//| Strategy Base Class (Abstract)                                    |
//+------------------------------------------------------------------+
class CStrategyBase
{
protected:
   StrategyParams  m_Params;
   CSymbolInfo     m_Symbol;
   bool            m_Initialized;
   Signal          m_LastSignal;
   
   //--- Indicator handles (override in derived class)
   int             m_HandleATR;
   
   //--- State
   int             m_CurrentTrend;    // 1 = Up, -1 = Down, 0 = Neutral
   double          m_CurrentATR;
   
public:
   //--- Constructor
   CStrategyBase()
   {
      m_Params.SetDefaults();
      m_Initialized = false;
      m_HandleATR = INVALID_HANDLE;
      m_CurrentTrend = 0;
      m_CurrentATR = 0;
      m_LastSignal.Clear();
   }
   
   //--- Destructor
   virtual ~CStrategyBase()
   {
      Deinit();
   }
   
   //--- Initialize (must be called)
   virtual bool Init(StrategyParams &params)
   {
      m_Params = params;
      
      if(!m_Symbol.Name(params.symbol))
      {
         Print("Strategy: Failed to initialize symbol");
         return false;
      }
      
      //--- Create ATR handle for stop calculation
      m_HandleATR = iATR(params.symbol, params.timeframe, 14);
      if(m_HandleATR == INVALID_HANDLE)
      {
         Print("Strategy: Failed to create ATR handle");
         return false;
      }
      
      //--- Call derived class initialization
      if(!OnInit())
         return false;
      
      m_Initialized = true;
      Print("Strategy initialized: ", params.name);
      return true;
   }
   
   //--- Deinitialize
   virtual void Deinit()
   {
      if(m_HandleATR != INVALID_HANDLE)
      {
         IndicatorRelease(m_HandleATR);
         m_HandleATR = INVALID_HANDLE;
      }
      
      OnDeinit();
      m_Initialized = false;
   }
   
   //--- Main signal generation (call each tick/bar)
   Signal GetSignal()
   {
      Signal signal;
      signal.Clear();
      
      if(!m_Initialized)
         return signal;
      
      //--- Refresh symbol
      m_Symbol.Refresh();
      m_Symbol.RefreshRates();
      
      //--- Update ATR
      double atr[];
      ArraySetAsSeries(atr, true);
      if(CopyBuffer(m_HandleATR, 0, 0, 1, atr) > 0)
         m_CurrentATR = atr[0];
      
      //--- Call derived class signal generation
      signal = GenerateSignal();
      
      //--- Apply filters
      if(signal.type != SIGNAL_NONE)
      {
         //--- Check confidence
         if(signal.confidence < m_Params.minConfidence)
         {
            signal.Clear();
            return signal;
         }
         
         //--- Check strength
         if(signal.strength < m_Params.minStrength)
         {
            signal.Clear();
            return signal;
         }
         
         //--- Check trend alignment
         if(m_Params.requireTrendAlignment)
         {
            UpdateTrend();
            if((signal.type == SIGNAL_BUY && m_CurrentTrend < 0) ||
               (signal.type == SIGNAL_SELL && m_CurrentTrend > 0))
            {
               signal.Clear();
               return signal;
            }
         }
         
         //--- Calculate stops
         CalculateStops(signal);
      }
      
      m_LastSignal = signal;
      return signal;
   }
   
   //+------------------------------------------------------------------+
   //| Virtual methods to override                                       |
   //+------------------------------------------------------------------+
   
   //--- Called during initialization (create indicators here)
   virtual bool OnInit() { return true; }
   
   //--- Called during deinitialization (release resources)
   virtual void OnDeinit() { }
   
   //--- Main signal generation logic (must override)
   virtual Signal GenerateSignal()
   {
      Signal sig;
      sig.Clear();
      return sig;
   }
   
   //--- Trend detection (override for custom trend logic)
   virtual void UpdateTrend()
   {
      //--- Default: use price vs MA
      double ma[];
      ArraySetAsSeries(ma, true);
      
      int handle = iMA(m_Params.symbol, m_Params.timeframe, 50, 0, MODE_EMA, PRICE_CLOSE);
      if(handle != INVALID_HANDLE)
      {
         if(CopyBuffer(handle, 0, 0, 1, ma) > 0)
         {
            double price = m_Symbol.Last();
            if(price > ma[0])
               m_CurrentTrend = 1;
            else if(price < ma[0])
               m_CurrentTrend = -1;
            else
               m_CurrentTrend = 0;
         }
         IndicatorRelease(handle);
      }
   }
   
   //--- Stop calculation (override for custom stops)
   virtual void CalculateStops(Signal &signal)
   {
      if(m_CurrentATR == 0)
         return;
      
      double price = (signal.type == SIGNAL_BUY) ? m_Symbol.Ask() : m_Symbol.Bid();
      double slDistance = m_CurrentATR * m_Params.slMultiplier;
      double tpDistance = m_CurrentATR * m_Params.tpMultiplier;
      
      if(signal.type == SIGNAL_BUY)
      {
         signal.stopLoss = NormalizeDouble(price - slDistance, m_Symbol.Digits());
         signal.takeProfit = NormalizeDouble(price + tpDistance, m_Symbol.Digits());
      }
      else if(signal.type == SIGNAL_SELL)
      {
         signal.stopLoss = NormalizeDouble(price + slDistance, m_Symbol.Digits());
         signal.takeProfit = NormalizeDouble(price - tpDistance, m_Symbol.Digits());
      }
   }
   
   //+------------------------------------------------------------------+
   //| Getters                                                           |
   //+------------------------------------------------------------------+
   
   string GetName()             { return m_Params.name; }
   bool   IsInitialized()       { return m_Initialized; }
   int    GetTrend()            { return m_CurrentTrend; }
   double GetATR()              { return m_CurrentATR; }
   Signal GetLastSignal()       { return m_LastSignal; }
   StrategyParams GetParams()   { return m_Params; }
   
   //--- Calculate lot size
   double CalculateLotSize(double slPoints)
   {
      if(slPoints <= 0)
         return 0.01;
      
      double balance = AccountInfoDouble(ACCOUNT_BALANCE);
      double riskAmount = balance * m_Params.riskPercent / 100.0;
      
      double tickValue = m_Symbol.TickValue();
      double tickSize = m_Symbol.TickSize();
      
      if(tickValue == 0 || tickSize == 0)
         return 0.01;
      
      double lotSize = riskAmount / (slPoints * tickValue / tickSize);
      
      double lotStep = m_Symbol.LotsStep();
      lotSize = MathFloor(lotSize / lotStep) * lotStep;
      
      lotSize = MathMax(m_Symbol.LotsMin(), lotSize);
      lotSize = MathMin(m_Symbol.LotsMax(), lotSize);
      
      return NormalizeDouble(lotSize, 2);
   }
};

//+------------------------------------------------------------------+
