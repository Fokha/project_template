//+------------------------------------------------------------------+
//|                                            Indicator_Wrapper.mqh |
//|                        Indicator caching and access patterns      |
//|                        Based on Ultimate System v19.0             |
//+------------------------------------------------------------------+
#property copyright   "{{AUTHOR_NAME}}"
#property version     "1.00"

// ═══════════════════════════════════════════════════════════════════
// INDICATOR TYPES
// ═══════════════════════════════════════════════════════════════════

enum ENUM_INDICATOR_TYPE
{
   IND_EMA,
   IND_SMA,
   IND_RSI,
   IND_ATR,
   IND_ADX,
   IND_MACD,
   IND_BB,
   IND_STOCH,
   IND_CCI,
   IND_WILLIAMS,
   IND_MFI,
   IND_OBV,
   IND_SAR,
   IND_ICHIMOKU
};

// ═══════════════════════════════════════════════════════════════════
// INDICATOR DATA STRUCTURE
// ═══════════════════════════════════════════════════════════════════

struct IndicatorData
{
   // Trend indicators
   double ema_fast;
   double ema_slow;
   double ema_fast_prev;
   double ema_slow_prev;

   // Momentum
   double rsi;
   double rsi_prev;
   double cci;
   double williams;

   // Volatility
   double atr;
   double bb_upper;
   double bb_middle;
   double bb_lower;

   // Trend strength
   double adx;
   double plus_di;
   double minus_di;

   // MACD
   double macd_main;
   double macd_signal;
   double macd_hist;

   // Stochastic
   double stoch_k;
   double stoch_d;

   // Volume
   double mfi;
   double obv;

   // Other
   double sar;
   double ichimoku_tenkan;
   double ichimoku_kijun;
   double ichimoku_span_a;
   double ichimoku_span_b;

   void Clear()
   {
      ema_fast = 0; ema_slow = 0;
      ema_fast_prev = 0; ema_slow_prev = 0;
      rsi = 0; rsi_prev = 0;
      cci = 0; williams = 0;
      atr = 0;
      bb_upper = 0; bb_middle = 0; bb_lower = 0;
      adx = 0; plus_di = 0; minus_di = 0;
      macd_main = 0; macd_signal = 0; macd_hist = 0;
      stoch_k = 0; stoch_d = 0;
      mfi = 0; obv = 0;
      sar = 0;
      ichimoku_tenkan = 0; ichimoku_kijun = 0;
      ichimoku_span_a = 0; ichimoku_span_b = 0;
   }
};

// ═══════════════════════════════════════════════════════════════════
// INDICATOR CACHE ENTRY
// ═══════════════════════════════════════════════════════════════════

class CIndicatorCache
{
private:
   string   m_Symbol;
   ENUM_TIMEFRAMES m_Timeframe;
   datetime m_LastUpdate;
   double   m_Values[];
   int      m_Size;

public:
   CIndicatorCache()
   {
      m_Symbol = "";
      m_Timeframe = PERIOD_CURRENT;
      m_LastUpdate = 0;
      m_Size = 3;
      ArrayResize(m_Values, m_Size);
   }

   void Init(string symbol, ENUM_TIMEFRAMES tf, int size = 3)
   {
      m_Symbol = symbol;
      m_Timeframe = tf;
      m_Size = size;
      ArrayResize(m_Values, m_Size);
      ArrayInitialize(m_Values, 0);
   }

   bool NeedsUpdate()
   {
      datetime barTime = iTime(m_Symbol, m_Timeframe, 0);
      return (barTime != m_LastUpdate);
   }

   void SetUpdated()
   {
      m_LastUpdate = iTime(m_Symbol, m_Timeframe, 0);
   }

   double Get(int index)
   {
      if(index >= 0 && index < m_Size)
         return m_Values[index];
      return 0;
   }

   void Set(int index, double value)
   {
      if(index >= 0 && index < m_Size)
         m_Values[index] = value;
   }

   bool CopyFrom(int handle, int bufferIndex, int startPos, int count)
   {
      if(ArrayResize(m_Values, count) < count) return false;
      return (CopyBuffer(handle, bufferIndex, startPos, count, m_Values) == count);
   }
};

// ═══════════════════════════════════════════════════════════════════
// INDICATOR MANAGER CLASS
// ═══════════════════════════════════════════════════════════════════

class CIndicatorManager
{
private:
   string   m_Symbol;
   ENUM_TIMEFRAMES m_Timeframe;

   // Indicator handles
   int m_HandleEMA_Fast;
   int m_HandleEMA_Slow;
   int m_HandleRSI;
   int m_HandleATR;
   int m_HandleADX;
   int m_HandleMACD;
   int m_HandleBB;
   int m_HandleStoch;
   int m_HandleCCI;
   int m_HandleWilliams;
   int m_HandleMFI;
   int m_HandleOBV;
   int m_HandleSAR;
   int m_HandleIchimoku;

   // Cache data
   datetime m_LastUpdateTime;
   IndicatorData m_Data;

   // Buffers for copying
   double m_Buffer1[];
   double m_Buffer2[];
   double m_Buffer3[];

   // Parameters
   int m_EMA_Fast_Period;
   int m_EMA_Slow_Period;
   int m_RSI_Period;
   int m_ATR_Period;
   int m_ADX_Period;
   int m_MACD_Fast;
   int m_MACD_Slow;
   int m_MACD_Signal;
   int m_BB_Period;
   double m_BB_Deviation;
   int m_Stoch_K;
   int m_Stoch_D;
   int m_Stoch_Slow;
   int m_CCI_Period;
   int m_Williams_Period;
   int m_MFI_Period;
   double m_SAR_Step;
   double m_SAR_Max;

public:
   CIndicatorManager()
   {
      m_Symbol = "";
      m_Timeframe = PERIOD_CURRENT;
      m_LastUpdateTime = 0;

      // Default parameters
      m_EMA_Fast_Period = 9;
      m_EMA_Slow_Period = 21;
      m_RSI_Period = 14;
      m_ATR_Period = 14;
      m_ADX_Period = 14;
      m_MACD_Fast = 12;
      m_MACD_Slow = 26;
      m_MACD_Signal = 9;
      m_BB_Period = 20;
      m_BB_Deviation = 2.0;
      m_Stoch_K = 14;
      m_Stoch_D = 3;
      m_Stoch_Slow = 3;
      m_CCI_Period = 14;
      m_Williams_Period = 14;
      m_MFI_Period = 14;
      m_SAR_Step = 0.02;
      m_SAR_Max = 0.2;

      // Initialize handles to invalid
      m_HandleEMA_Fast = INVALID_HANDLE;
      m_HandleEMA_Slow = INVALID_HANDLE;
      m_HandleRSI = INVALID_HANDLE;
      m_HandleATR = INVALID_HANDLE;
      m_HandleADX = INVALID_HANDLE;
      m_HandleMACD = INVALID_HANDLE;
      m_HandleBB = INVALID_HANDLE;
      m_HandleStoch = INVALID_HANDLE;
      m_HandleCCI = INVALID_HANDLE;
      m_HandleWilliams = INVALID_HANDLE;
      m_HandleMFI = INVALID_HANDLE;
      m_HandleOBV = INVALID_HANDLE;
      m_HandleSAR = INVALID_HANDLE;
      m_HandleIchimoku = INVALID_HANDLE;

      ArraySetAsSeries(m_Buffer1, true);
      ArraySetAsSeries(m_Buffer2, true);
      ArraySetAsSeries(m_Buffer3, true);
   }

   ~CIndicatorManager()
   {
      Release();
   }

   // ═══════════════════════════════════════════════════════════════
   // INITIALIZATION
   // ═══════════════════════════════════════════════════════════════

   bool Init(string symbol, ENUM_TIMEFRAMES tf)
   {
      m_Symbol = symbol;
      m_Timeframe = tf;
      m_Data.Clear();

      return CreateHandles();
   }

   void SetParameters(int emaFast, int emaSlow, int rsi, int atr,
                      int adx = 14, int macdFast = 12, int macdSlow = 26,
                      int macdSignal = 9, int bbPeriod = 20, double bbDev = 2.0)
   {
      m_EMA_Fast_Period = emaFast;
      m_EMA_Slow_Period = emaSlow;
      m_RSI_Period = rsi;
      m_ATR_Period = atr;
      m_ADX_Period = adx;
      m_MACD_Fast = macdFast;
      m_MACD_Slow = macdSlow;
      m_MACD_Signal = macdSignal;
      m_BB_Period = bbPeriod;
      m_BB_Deviation = bbDev;
   }

   bool CreateHandles()
   {
      // Create essential indicators
      m_HandleEMA_Fast = iMA(m_Symbol, m_Timeframe, m_EMA_Fast_Period, 0, MODE_EMA, PRICE_CLOSE);
      m_HandleEMA_Slow = iMA(m_Symbol, m_Timeframe, m_EMA_Slow_Period, 0, MODE_EMA, PRICE_CLOSE);
      m_HandleRSI = iRSI(m_Symbol, m_Timeframe, m_RSI_Period, PRICE_CLOSE);
      m_HandleATR = iATR(m_Symbol, m_Timeframe, m_ATR_Period);

      if(m_HandleEMA_Fast == INVALID_HANDLE ||
         m_HandleEMA_Slow == INVALID_HANDLE ||
         m_HandleRSI == INVALID_HANDLE ||
         m_HandleATR == INVALID_HANDLE)
      {
         Print("Error creating essential indicator handles");
         return false;
      }

      // Create optional indicators
      m_HandleADX = iADX(m_Symbol, m_Timeframe, m_ADX_Period);
      m_HandleMACD = iMACD(m_Symbol, m_Timeframe, m_MACD_Fast, m_MACD_Slow, m_MACD_Signal, PRICE_CLOSE);
      m_HandleBB = iBands(m_Symbol, m_Timeframe, m_BB_Period, 0, m_BB_Deviation, PRICE_CLOSE);
      m_HandleStoch = iStochastic(m_Symbol, m_Timeframe, m_Stoch_K, m_Stoch_D, m_Stoch_Slow, MODE_SMA, STO_LOWHIGH);
      m_HandleCCI = iCCI(m_Symbol, m_Timeframe, m_CCI_Period, PRICE_TYPICAL);
      m_HandleWilliams = iWPR(m_Symbol, m_Timeframe, m_Williams_Period);
      m_HandleMFI = iMFI(m_Symbol, m_Timeframe, m_MFI_Period, VOLUME_TICK);
      m_HandleOBV = iOBV(m_Symbol, m_Timeframe, VOLUME_TICK);
      m_HandleSAR = iSAR(m_Symbol, m_Timeframe, m_SAR_Step, m_SAR_Max);
      m_HandleIchimoku = iIchimoku(m_Symbol, m_Timeframe, 9, 26, 52);

      return true;
   }

   void Release()
   {
      if(m_HandleEMA_Fast != INVALID_HANDLE) { IndicatorRelease(m_HandleEMA_Fast); m_HandleEMA_Fast = INVALID_HANDLE; }
      if(m_HandleEMA_Slow != INVALID_HANDLE) { IndicatorRelease(m_HandleEMA_Slow); m_HandleEMA_Slow = INVALID_HANDLE; }
      if(m_HandleRSI != INVALID_HANDLE) { IndicatorRelease(m_HandleRSI); m_HandleRSI = INVALID_HANDLE; }
      if(m_HandleATR != INVALID_HANDLE) { IndicatorRelease(m_HandleATR); m_HandleATR = INVALID_HANDLE; }
      if(m_HandleADX != INVALID_HANDLE) { IndicatorRelease(m_HandleADX); m_HandleADX = INVALID_HANDLE; }
      if(m_HandleMACD != INVALID_HANDLE) { IndicatorRelease(m_HandleMACD); m_HandleMACD = INVALID_HANDLE; }
      if(m_HandleBB != INVALID_HANDLE) { IndicatorRelease(m_HandleBB); m_HandleBB = INVALID_HANDLE; }
      if(m_HandleStoch != INVALID_HANDLE) { IndicatorRelease(m_HandleStoch); m_HandleStoch = INVALID_HANDLE; }
      if(m_HandleCCI != INVALID_HANDLE) { IndicatorRelease(m_HandleCCI); m_HandleCCI = INVALID_HANDLE; }
      if(m_HandleWilliams != INVALID_HANDLE) { IndicatorRelease(m_HandleWilliams); m_HandleWilliams = INVALID_HANDLE; }
      if(m_HandleMFI != INVALID_HANDLE) { IndicatorRelease(m_HandleMFI); m_HandleMFI = INVALID_HANDLE; }
      if(m_HandleOBV != INVALID_HANDLE) { IndicatorRelease(m_HandleOBV); m_HandleOBV = INVALID_HANDLE; }
      if(m_HandleSAR != INVALID_HANDLE) { IndicatorRelease(m_HandleSAR); m_HandleSAR = INVALID_HANDLE; }
      if(m_HandleIchimoku != INVALID_HANDLE) { IndicatorRelease(m_HandleIchimoku); m_HandleIchimoku = INVALID_HANDLE; }
   }

   // ═══════════════════════════════════════════════════════════════
   // UPDATE ALL INDICATORS
   // ═══════════════════════════════════════════════════════════════

   bool Update()
   {
      datetime barTime = iTime(m_Symbol, m_Timeframe, 0);
      if(barTime == m_LastUpdateTime) return true; // Already updated

      m_Data.Clear();

      // EMA
      if(CopyBuffer(m_HandleEMA_Fast, 0, 0, 3, m_Buffer1) == 3)
      {
         m_Data.ema_fast = m_Buffer1[0];
         m_Data.ema_fast_prev = m_Buffer1[1];
      }
      if(CopyBuffer(m_HandleEMA_Slow, 0, 0, 3, m_Buffer1) == 3)
      {
         m_Data.ema_slow = m_Buffer1[0];
         m_Data.ema_slow_prev = m_Buffer1[1];
      }

      // RSI
      if(CopyBuffer(m_HandleRSI, 0, 0, 3, m_Buffer1) == 3)
      {
         m_Data.rsi = m_Buffer1[0];
         m_Data.rsi_prev = m_Buffer1[1];
      }

      // ATR
      if(CopyBuffer(m_HandleATR, 0, 0, 1, m_Buffer1) == 1)
      {
         m_Data.atr = m_Buffer1[0];
      }

      // ADX
      if(m_HandleADX != INVALID_HANDLE)
      {
         if(CopyBuffer(m_HandleADX, 0, 0, 1, m_Buffer1) == 1) m_Data.adx = m_Buffer1[0];
         if(CopyBuffer(m_HandleADX, 1, 0, 1, m_Buffer1) == 1) m_Data.plus_di = m_Buffer1[0];
         if(CopyBuffer(m_HandleADX, 2, 0, 1, m_Buffer1) == 1) m_Data.minus_di = m_Buffer1[0];
      }

      // MACD
      if(m_HandleMACD != INVALID_HANDLE)
      {
         if(CopyBuffer(m_HandleMACD, 0, 0, 1, m_Buffer1) == 1) m_Data.macd_main = m_Buffer1[0];
         if(CopyBuffer(m_HandleMACD, 1, 0, 1, m_Buffer1) == 1) m_Data.macd_signal = m_Buffer1[0];
         m_Data.macd_hist = m_Data.macd_main - m_Data.macd_signal;
      }

      // Bollinger Bands
      if(m_HandleBB != INVALID_HANDLE)
      {
         if(CopyBuffer(m_HandleBB, 0, 0, 1, m_Buffer1) == 1) m_Data.bb_middle = m_Buffer1[0];
         if(CopyBuffer(m_HandleBB, 1, 0, 1, m_Buffer1) == 1) m_Data.bb_upper = m_Buffer1[0];
         if(CopyBuffer(m_HandleBB, 2, 0, 1, m_Buffer1) == 1) m_Data.bb_lower = m_Buffer1[0];
      }

      // Stochastic
      if(m_HandleStoch != INVALID_HANDLE)
      {
         if(CopyBuffer(m_HandleStoch, 0, 0, 1, m_Buffer1) == 1) m_Data.stoch_k = m_Buffer1[0];
         if(CopyBuffer(m_HandleStoch, 1, 0, 1, m_Buffer1) == 1) m_Data.stoch_d = m_Buffer1[0];
      }

      // CCI
      if(m_HandleCCI != INVALID_HANDLE)
      {
         if(CopyBuffer(m_HandleCCI, 0, 0, 1, m_Buffer1) == 1) m_Data.cci = m_Buffer1[0];
      }

      // Williams %R
      if(m_HandleWilliams != INVALID_HANDLE)
      {
         if(CopyBuffer(m_HandleWilliams, 0, 0, 1, m_Buffer1) == 1) m_Data.williams = m_Buffer1[0];
      }

      // MFI
      if(m_HandleMFI != INVALID_HANDLE)
      {
         if(CopyBuffer(m_HandleMFI, 0, 0, 1, m_Buffer1) == 1) m_Data.mfi = m_Buffer1[0];
      }

      // OBV
      if(m_HandleOBV != INVALID_HANDLE)
      {
         if(CopyBuffer(m_HandleOBV, 0, 0, 1, m_Buffer1) == 1) m_Data.obv = m_Buffer1[0];
      }

      // SAR
      if(m_HandleSAR != INVALID_HANDLE)
      {
         if(CopyBuffer(m_HandleSAR, 0, 0, 1, m_Buffer1) == 1) m_Data.sar = m_Buffer1[0];
      }

      // Ichimoku
      if(m_HandleIchimoku != INVALID_HANDLE)
      {
         if(CopyBuffer(m_HandleIchimoku, 0, 0, 1, m_Buffer1) == 1) m_Data.ichimoku_tenkan = m_Buffer1[0];
         if(CopyBuffer(m_HandleIchimoku, 1, 0, 1, m_Buffer1) == 1) m_Data.ichimoku_kijun = m_Buffer1[0];
         if(CopyBuffer(m_HandleIchimoku, 2, 0, 1, m_Buffer1) == 1) m_Data.ichimoku_span_a = m_Buffer1[0];
         if(CopyBuffer(m_HandleIchimoku, 3, 0, 1, m_Buffer1) == 1) m_Data.ichimoku_span_b = m_Buffer1[0];
      }

      m_LastUpdateTime = barTime;
      return true;
   }

   // ═══════════════════════════════════════════════════════════════
   // GETTERS
   // ═══════════════════════════════════════════════════════════════

   IndicatorData GetData() { return m_Data; }

   double GetEMAFast() { return m_Data.ema_fast; }
   double GetEMASlow() { return m_Data.ema_slow; }
   double GetRSI() { return m_Data.rsi; }
   double GetATR() { return m_Data.atr; }
   double GetADX() { return m_Data.adx; }
   double GetPlusDI() { return m_Data.plus_di; }
   double GetMinusDI() { return m_Data.minus_di; }
   double GetMACD() { return m_Data.macd_main; }
   double GetMACDSignal() { return m_Data.macd_signal; }
   double GetMACDHist() { return m_Data.macd_hist; }
   double GetBBUpper() { return m_Data.bb_upper; }
   double GetBBMiddle() { return m_Data.bb_middle; }
   double GetBBLower() { return m_Data.bb_lower; }
   double GetStochK() { return m_Data.stoch_k; }
   double GetStochD() { return m_Data.stoch_d; }
   double GetCCI() { return m_Data.cci; }
   double GetWilliams() { return m_Data.williams; }
   double GetMFI() { return m_Data.mfi; }
   double GetOBV() { return m_Data.obv; }
   double GetSAR() { return m_Data.sar; }

   // ═══════════════════════════════════════════════════════════════
   // SIGNAL HELPERS
   // ═══════════════════════════════════════════════════════════════

   bool IsEMABullishCross()
   {
      return (m_Data.ema_fast > m_Data.ema_slow && m_Data.ema_fast_prev <= m_Data.ema_slow_prev);
   }

   bool IsEMABearishCross()
   {
      return (m_Data.ema_fast < m_Data.ema_slow && m_Data.ema_fast_prev >= m_Data.ema_slow_prev);
   }

   bool IsTrendUp() { return (m_Data.ema_fast > m_Data.ema_slow); }
   bool IsTrendDown() { return (m_Data.ema_fast < m_Data.ema_slow); }

   bool IsRSIOversold(double level = 30) { return (m_Data.rsi < level); }
   bool IsRSIOverbought(double level = 70) { return (m_Data.rsi > level); }

   bool IsStrongTrend(double adxLevel = 25) { return (m_Data.adx > adxLevel); }

   bool IsSARBullish(double price) { return (m_Data.sar < price); }
   bool IsSARBearish(double price) { return (m_Data.sar > price); }
};

//+------------------------------------------------------------------+
