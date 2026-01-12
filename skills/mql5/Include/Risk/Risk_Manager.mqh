//+------------------------------------------------------------------+
//|                                               Risk_Manager.mqh   |
//|                                  Risk Management Utility v1.0    |
//|                       Position sizing, drawdown, and limits      |
//+------------------------------------------------------------------+
#property copyright "Your Name"
#property link      "https://www.example.com"
#property version   "1.00"
#property strict

#include <Trade\AccountInfo.mqh>
#include <Trade\SymbolInfo.mqh>

//+------------------------------------------------------------------+
//| PropFirm Profiles                                                 |
//+------------------------------------------------------------------+
enum ENUM_PROPFIRM_PROFILE
{
   PROPFIRM_NONE = 0,      // No PropFirm Limits
   PROPFIRM_FTMO,          // FTMO
   PROPFIRM_FUNDEDNEXT,    // FundedNext
   PROPFIRM_MFF,           // My Forex Funds
   PROPFIRM_E8,            // E8 Funding
   PROPFIRM_CUSTOM         // Custom Limits
};

//+------------------------------------------------------------------+
//| PropFirm Limits Structure                                         |
//+------------------------------------------------------------------+
struct PropFirmLimits
{
   double   maxDailyLossPercent;
   double   maxTotalDrawdownPercent;
   double   maxPositionSizePercent;
   int      maxOpenPositions;
   bool     allowWeekendHolding;
   bool     allowNewsTrading;
   
   void SetForFTMO()
   {
      maxDailyLossPercent = 5.0;
      maxTotalDrawdownPercent = 10.0;
      maxPositionSizePercent = 100.0;
      maxOpenPositions = 100;
      allowWeekendHolding = true;
      allowNewsTrading = true;
   }
   
   void SetForFundedNext()
   {
      maxDailyLossPercent = 5.0;
      maxTotalDrawdownPercent = 10.0;
      maxPositionSizePercent = 100.0;
      maxOpenPositions = 100;
      allowWeekendHolding = true;
      allowNewsTrading = true;
   }
   
   void SetForMFF()
   {
      maxDailyLossPercent = 5.0;
      maxTotalDrawdownPercent = 12.0;
      maxPositionSizePercent = 100.0;
      maxOpenPositions = 100;
      allowWeekendHolding = false;
      allowNewsTrading = false;
   }
   
   void SetForE8()
   {
      maxDailyLossPercent = 5.0;
      maxTotalDrawdownPercent = 8.0;
      maxPositionSizePercent = 100.0;
      maxOpenPositions = 100;
      allowWeekendHolding = true;
      allowNewsTrading = true;
   }
   
   void SetDefault()
   {
      maxDailyLossPercent = 5.0;
      maxTotalDrawdownPercent = 10.0;
      maxPositionSizePercent = 100.0;
      maxOpenPositions = 10;
      allowWeekendHolding = true;
      allowNewsTrading = true;
   }
};

//+------------------------------------------------------------------+
//| Risk Check Result                                                 |
//+------------------------------------------------------------------+
struct RiskCheckResult
{
   bool     passed;
   string   reason;
   double   currentValue;
   double   limitValue;
   
   void Pass()
   {
      passed = true;
      reason = "";
   }
   
   void Fail(string msg, double current, double limit)
   {
      passed = false;
      reason = msg;
      currentValue = current;
      limitValue = limit;
   }
};

//+------------------------------------------------------------------+
//| Risk Manager Class                                                |
//+------------------------------------------------------------------+
class CRiskManager
{
private:
   CAccountInfo      m_Account;
   CSymbolInfo       m_Symbol;
   PropFirmLimits    m_Limits;
   
   //--- Daily tracking
   double            m_DayStartBalance;
   double            m_DayStartEquity;
   datetime          m_LastDayChecked;
   int               m_TradesToday;
   
   //--- Drawdown tracking
   double            m_HighWaterMark;
   double            m_MaxDrawdownSeen;
   
   //--- Settings
   double            m_RiskPerTrade;      // Percent
   double            m_MaxLotSize;
   double            m_MinLotSize;
   
public:
   //--- Constructor
   CRiskManager()
   {
      m_Limits.SetDefault();
      m_RiskPerTrade = 1.0;
      m_MaxLotSize = 10.0;
      m_MinLotSize = 0.01;
      m_DayStartBalance = 0;
      m_DayStartEquity = 0;
      m_LastDayChecked = 0;
      m_TradesToday = 0;
      m_HighWaterMark = 0;
      m_MaxDrawdownSeen = 0;
   }
   
   //--- Initialize
   bool Init(string symbol, ENUM_PROPFIRM_PROFILE profile = PROPFIRM_NONE)
   {
      if(!m_Symbol.Name(symbol))
         return false;
      
      SetPropFirmProfile(profile);
      ResetDailyTracking();
      
      m_HighWaterMark = m_Account.Equity();
      
      return true;
   }
   
   //--- Set PropFirm Profile
   void SetPropFirmProfile(ENUM_PROPFIRM_PROFILE profile)
   {
      switch(profile)
      {
         case PROPFIRM_FTMO:
            m_Limits.SetForFTMO();
            break;
         case PROPFIRM_FUNDEDNEXT:
            m_Limits.SetForFundedNext();
            break;
         case PROPFIRM_MFF:
            m_Limits.SetForMFF();
            break;
         case PROPFIRM_E8:
            m_Limits.SetForE8();
            break;
         default:
            m_Limits.SetDefault();
            break;
      }
   }
   
   //--- Set custom limits
   void SetLimits(double dailyLoss, double totalDrawdown, int maxPositions)
   {
      m_Limits.maxDailyLossPercent = dailyLoss;
      m_Limits.maxTotalDrawdownPercent = totalDrawdown;
      m_Limits.maxOpenPositions = maxPositions;
   }
   
   //--- Set risk per trade
   void SetRiskPerTrade(double riskPercent) { m_RiskPerTrade = riskPercent; }
   void SetLotLimits(double minLot, double maxLot) { m_MinLotSize = minLot; m_MaxLotSize = maxLot; }
   
   //--- Check new day and reset counters
   void CheckNewDay()
   {
      datetime currentDay = iTime(m_Symbol.Name(), PERIOD_D1, 0);
      
      if(currentDay != m_LastDayChecked)
      {
         m_LastDayChecked = currentDay;
         ResetDailyTracking();
      }
   }
   
   //--- Reset daily tracking
   void ResetDailyTracking()
   {
      m_DayStartBalance = m_Account.Balance();
      m_DayStartEquity = m_Account.Equity();
      m_TradesToday = 0;
   }
   
   //--- Update high water mark
   void UpdateHighWaterMark()
   {
      double equity = m_Account.Equity();
      if(equity > m_HighWaterMark)
         m_HighWaterMark = equity;
      
      double drawdown = (m_HighWaterMark - equity) / m_HighWaterMark * 100;
      if(drawdown > m_MaxDrawdownSeen)
         m_MaxDrawdownSeen = drawdown;
   }
   
   //--- Increment trade counter
   void RecordTrade() { m_TradesToday++; }
   
   //+------------------------------------------------------------------+
   //| Risk Checks                                                       |
   //+------------------------------------------------------------------+
   
   //--- Full risk check
   RiskCheckResult CanTrade()
   {
      RiskCheckResult result;
      
      //--- Check daily loss
      result = CheckDailyLoss();
      if(!result.passed) return result;
      
      //--- Check total drawdown
      result = CheckTotalDrawdown();
      if(!result.passed) return result;
      
      //--- Check position count
      result = CheckPositionCount();
      if(!result.passed) return result;
      
      //--- Check weekend
      result = CheckWeekend();
      if(!result.passed) return result;
      
      result.Pass();
      return result;
   }
   
   //--- Check daily loss limit
   RiskCheckResult CheckDailyLoss()
   {
      RiskCheckResult result;
      
      double currentBalance = m_Account.Balance();
      double dailyLoss = (m_DayStartBalance - currentBalance) / m_DayStartBalance * 100;
      
      if(dailyLoss >= m_Limits.maxDailyLossPercent * 0.9)  // 90% of limit as warning
      {
         result.Fail("Daily loss limit approaching", dailyLoss, m_Limits.maxDailyLossPercent);
         return result;
      }
      
      result.Pass();
      return result;
   }
   
   //--- Check total drawdown
   RiskCheckResult CheckTotalDrawdown()
   {
      RiskCheckResult result;
      
      UpdateHighWaterMark();
      double equity = m_Account.Equity();
      double drawdown = (m_HighWaterMark - equity) / m_HighWaterMark * 100;
      
      if(drawdown >= m_Limits.maxTotalDrawdownPercent * 0.9)
      {
         result.Fail("Total drawdown limit approaching", drawdown, m_Limits.maxTotalDrawdownPercent);
         return result;
      }
      
      result.Pass();
      return result;
   }
   
   //--- Check position count
   RiskCheckResult CheckPositionCount()
   {
      RiskCheckResult result;
      
      int positions = PositionsTotal();
      
      if(positions >= m_Limits.maxOpenPositions)
      {
         result.Fail("Max positions reached", positions, m_Limits.maxOpenPositions);
         return result;
      }
      
      result.Pass();
      return result;
   }
   
   //--- Check weekend holding
   RiskCheckResult CheckWeekend()
   {
      RiskCheckResult result;
      
      if(!m_Limits.allowWeekendHolding)
      {
         MqlDateTime dt;
         TimeToStruct(TimeCurrent(), dt);
         
         if(dt.day_of_week == 5 && dt.hour >= 20)
         {
            result.Fail("Weekend holding not allowed", dt.hour, 20);
            return result;
         }
      }
      
      result.Pass();
      return result;
   }
   
   //+------------------------------------------------------------------+
   //| Position Sizing                                                   |
   //+------------------------------------------------------------------+
   
   //--- Calculate lot size based on risk
   double CalculateLotSize(double slPoints)
   {
      if(slPoints <= 0)
         return m_MinLotSize;
      
      m_Symbol.Refresh();
      
      double balance = m_Account.Balance();
      double riskAmount = balance * m_RiskPerTrade / 100.0;
      
      double tickValue = m_Symbol.TickValue();
      double tickSize = m_Symbol.TickSize();
      double point = m_Symbol.Point();
      
      if(tickValue == 0 || tickSize == 0)
         return m_MinLotSize;
      
      //--- Calculate lot size
      double lotSize = riskAmount / (slPoints * tickValue / tickSize);
      
      //--- Normalize
      double lotStep = m_Symbol.LotsStep();
      lotSize = MathFloor(lotSize / lotStep) * lotStep;
      
      //--- Apply limits
      lotSize = MathMax(m_MinLotSize, lotSize);
      lotSize = MathMin(m_MaxLotSize, lotSize);
      lotSize = MathMin(m_Symbol.LotsMax(), lotSize);
      
      return NormalizeDouble(lotSize, 2);
   }
   
   //--- Calculate lot size with ATR-based stop
   double CalculateLotSizeATR(int atrHandle, double atrMultiplier)
   {
      double atr[];
      ArraySetAsSeries(atr, true);
      
      if(CopyBuffer(atrHandle, 0, 0, 1, atr) <= 0)
         return m_MinLotSize;
      
      double slDistance = atr[0] * atrMultiplier / m_Symbol.Point();
      return CalculateLotSize(slDistance);
   }
   
   //+------------------------------------------------------------------+
   //| Getters                                                           |
   //+------------------------------------------------------------------+
   
   double GetDailyLossPercent()
   {
      double balance = m_Account.Balance();
      return (m_DayStartBalance - balance) / m_DayStartBalance * 100;
   }
   
   double GetCurrentDrawdown()
   {
      UpdateHighWaterMark();
      double equity = m_Account.Equity();
      return (m_HighWaterMark - equity) / m_HighWaterMark * 100;
   }
   
   double GetMaxDrawdownSeen() { return m_MaxDrawdownSeen; }
   double GetHighWaterMark()   { return m_HighWaterMark; }
   int    GetTradesToday()     { return m_TradesToday; }
   
   double GetDailyLossLimit()      { return m_Limits.maxDailyLossPercent; }
   double GetTotalDrawdownLimit()  { return m_Limits.maxTotalDrawdownPercent; }
   int    GetMaxPositions()        { return m_Limits.maxOpenPositions; }
};

//+------------------------------------------------------------------+
