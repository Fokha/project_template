//+------------------------------------------------------------------+
//|                                                  EA_Template.mq5 |
//|                                    Expert Advisor Template v1.0  |
//|                             Comprehensive trading EA framework   |
//+------------------------------------------------------------------+
#property copyright "Your Name"
#property link      "https://www.example.com"
#property version   "1.00"
#property strict

//--- Include standard library
#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>
#include <Trade\SymbolInfo.mqh>
#include <Trade\AccountInfo.mqh>

//+------------------------------------------------------------------+
//| Input Parameters                                                  |
//+------------------------------------------------------------------+

//--- General Settings
input group "=== General Settings ==="
input ulong    InpMagicNumber      = 123456;        // Magic Number
input string   InpComment          = "EA_Template"; // Trade Comment
input bool     InpDebugMode        = false;         // Debug Mode

//--- Trading Settings
input group "=== Trading Settings ==="
input double   InpRiskPercent      = 1.0;           // Risk Per Trade (%)
input double   InpMaxLotSize       = 10.0;          // Maximum Lot Size
input double   InpMinLotSize       = 0.01;          // Minimum Lot Size
input int      InpMaxPositions     = 1;             // Max Positions Per Symbol
input int      InpSlippage         = 30;            // Max Slippage (points)

//--- Stop Loss / Take Profit
input group "=== Stop Loss / Take Profit ==="
input bool     InpUseATRStops      = true;          // Use ATR-Based Stops
input double   InpSLMultiplier     = 1.5;           // SL ATR Multiplier
input double   InpTPMultiplier     = 2.0;           // TP ATR Multiplier
input int      InpFixedSLPips      = 50;            // Fixed SL (pips) - if not ATR
input int      InpFixedTPPips      = 100;           // Fixed TP (pips) - if not ATR

//--- Strategy Parameters
input group "=== Strategy Parameters ==="
input int      InpFastMA           = 10;            // Fast MA Period
input int      InpSlowMA           = 20;            // Slow MA Period
input ENUM_MA_METHOD InpMAMethod   = MODE_EMA;      // MA Method
input int      InpRSIPeriod        = 14;            // RSI Period
input int      InpRSIOverbought    = 70;            // RSI Overbought Level
input int      InpRSIOversold      = 30;            // RSI Oversold Level
input int      InpATRPeriod        = 14;            // ATR Period

//--- Risk Management
input group "=== Risk Management ==="
input double   InpMaxDailyLoss     = 5.0;           // Max Daily Loss (%)
input double   InpMaxDrawdown      = 10.0;          // Max Drawdown (%)
input int      InpMaxTradesPerDay  = 5;             // Max Trades Per Day
input int      InpCooldownMinutes  = 30;            // Cooldown Between Trades (min)

//--- Session Filter
input group "=== Session Filter ==="
input bool     InpUseSessionFilter = true;          // Use Session Filter
input int      InpSessionStartHour = 8;             // Session Start Hour (Server Time)
input int      InpSessionEndHour   = 20;            // Session End Hour (Server Time)
input bool     InpTradeFriday      = true;          // Trade on Friday
input bool     InpCloseOnFriday    = false;         // Close Positions Friday EOD

//--- Notifications
input group "=== Notifications ==="
input bool     InpPushNotify       = false;         // Push Notifications
input bool     InpEmailNotify      = false;         // Email Notifications
input bool     InpAlertNotify      = true;          // Alert Notifications

//+------------------------------------------------------------------+
//| Global Variables                                                  |
//+------------------------------------------------------------------+

//--- Trading objects
CTrade         g_Trade;
CPositionInfo  g_Position;
CSymbolInfo    g_SymbolInfo;
CAccountInfo   g_AccountInfo;

//--- Indicator handles
int            g_HandleFastMA;
int            g_HandleSlowMA;
int            g_HandleRSI;
int            g_HandleATR;

//--- Indicator buffers
double         g_FastMA[];
double         g_SlowMA[];
double         g_RSI[];
double         g_ATR[];

//--- State tracking
datetime       g_LastTradeTime     = 0;
int            g_TradesToday       = 0;
datetime       g_LastDayChecked    = 0;
double         g_DayStartBalance   = 0;
double         g_HighWaterMark     = 0;

//--- Price info
double         g_Point;
int            g_Digits;

//+------------------------------------------------------------------+
//| Expert initialization function                                    |
//+------------------------------------------------------------------+
int OnInit()
{
   //--- Initialize symbol info
   if(!g_SymbolInfo.Name(_Symbol))
   {
      Print("Failed to initialize symbol info");
      return INIT_FAILED;
   }
   g_SymbolInfo.Refresh();
   
   //--- Store point and digits
   g_Point = g_SymbolInfo.Point();
   g_Digits = (int)g_SymbolInfo.Digits();
   
   //--- Initialize trade object
   g_Trade.SetExpertMagicNumber(InpMagicNumber);
   g_Trade.SetDeviationInPoints(InpSlippage);
   g_Trade.SetTypeFilling(ORDER_FILLING_IOC);
   g_Trade.SetAsyncMode(false);
   
   //--- Create indicator handles
   g_HandleFastMA = iMA(_Symbol, PERIOD_CURRENT, InpFastMA, 0, InpMAMethod, PRICE_CLOSE);
   g_HandleSlowMA = iMA(_Symbol, PERIOD_CURRENT, InpSlowMA, 0, InpMAMethod, PRICE_CLOSE);
   g_HandleRSI    = iRSI(_Symbol, PERIOD_CURRENT, InpRSIPeriod, PRICE_CLOSE);
   g_HandleATR    = iATR(_Symbol, PERIOD_CURRENT, InpATRPeriod);
   
   //--- Validate handles
   if(g_HandleFastMA == INVALID_HANDLE || g_HandleSlowMA == INVALID_HANDLE ||
      g_HandleRSI == INVALID_HANDLE || g_HandleATR == INVALID_HANDLE)
   {
      Print("Failed to create indicator handles");
      return INIT_FAILED;
   }
   
   //--- Set arrays as series
   ArraySetAsSeries(g_FastMA, true);
   ArraySetAsSeries(g_SlowMA, true);
   ArraySetAsSeries(g_RSI, true);
   ArraySetAsSeries(g_ATR, true);
   
   //--- Initialize state
   g_DayStartBalance = g_AccountInfo.Balance();
   g_HighWaterMark = g_AccountInfo.Equity();
   g_LastDayChecked = iTime(_Symbol, PERIOD_D1, 0);
   
   Print("EA initialized successfully");
   Print("Symbol: ", _Symbol, " | Point: ", g_Point, " | Digits: ", g_Digits);
   
   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                  |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   //--- Release indicator handles
   if(g_HandleFastMA != INVALID_HANDLE) IndicatorRelease(g_HandleFastMA);
   if(g_HandleSlowMA != INVALID_HANDLE) IndicatorRelease(g_HandleSlowMA);
   if(g_HandleRSI != INVALID_HANDLE)    IndicatorRelease(g_HandleRSI);
   if(g_HandleATR != INVALID_HANDLE)    IndicatorRelease(g_HandleATR);
   
   Print("EA deinitialized. Reason: ", reason);
}

//+------------------------------------------------------------------+
//| Expert tick function                                              |
//+------------------------------------------------------------------+
void OnTick()
{
   //--- Refresh symbol info
   g_SymbolInfo.Refresh();
   g_SymbolInfo.RefreshRates();
   
   //--- Check for new day
   CheckNewDay();
   
   //--- Risk checks
   if(!PassesRiskChecks())
      return;
   
   //--- Session filter
   if(!IsWithinTradingSession())
      return;
   
   //--- Cooldown check
   if(!PassesCooldownCheck())
      return;
   
   //--- Update indicators
   if(!UpdateIndicators())
      return;
   
   //--- Check for new bar (optional - for bar-based strategies)
   static datetime lastBarTime = 0;
   datetime currentBarTime = iTime(_Symbol, PERIOD_CURRENT, 0);
   if(currentBarTime == lastBarTime)
      return;  // Only trade on new bar
   lastBarTime = currentBarTime;
   
   //--- Generate signal
   int signal = GenerateSignal();
   
   //--- Execute signal
   if(signal != 0)
      ExecuteSignal(signal);
   
   //--- Manage open positions
   ManagePositions();
}

//+------------------------------------------------------------------+
//| Check for new trading day                                         |
//+------------------------------------------------------------------+
void CheckNewDay()
{
   datetime currentDay = iTime(_Symbol, PERIOD_D1, 0);
   
   if(currentDay != g_LastDayChecked)
   {
      g_LastDayChecked = currentDay;
      g_TradesToday = 0;
      g_DayStartBalance = g_AccountInfo.Balance();
      
      if(InpDebugMode)
         Print("New day detected. Daily counters reset.");
   }
}

//+------------------------------------------------------------------+
//| Risk management checks                                            |
//+------------------------------------------------------------------+
bool PassesRiskChecks()
{
   //--- Check max trades per day
   if(g_TradesToday >= InpMaxTradesPerDay)
   {
      if(InpDebugMode)
         Print("Max trades per day reached: ", g_TradesToday);
      return false;
   }
   
   //--- Check daily loss limit
   double currentBalance = g_AccountInfo.Balance();
   double dailyLossPercent = (g_DayStartBalance - currentBalance) / g_DayStartBalance * 100;
   
   if(dailyLossPercent >= InpMaxDailyLoss)
   {
      if(InpDebugMode)
         Print("Daily loss limit reached: ", DoubleToString(dailyLossPercent, 2), "%");
      return false;
   }
   
   //--- Check drawdown limit
   double equity = g_AccountInfo.Equity();
   if(equity > g_HighWaterMark)
      g_HighWaterMark = equity;
   
   double drawdownPercent = (g_HighWaterMark - equity) / g_HighWaterMark * 100;
   
   if(drawdownPercent >= InpMaxDrawdown)
   {
      if(InpDebugMode)
         Print("Max drawdown reached: ", DoubleToString(drawdownPercent, 2), "%");
      return false;
   }
   
   //--- Check max positions
   if(CountPositions() >= InpMaxPositions)
   {
      if(InpDebugMode)
         Print("Max positions reached: ", CountPositions());
      return false;
   }
   
   return true;
}

//+------------------------------------------------------------------+
//| Session filter check                                              |
//+------------------------------------------------------------------+
bool IsWithinTradingSession()
{
   if(!InpUseSessionFilter)
      return true;
   
   MqlDateTime dt;
   TimeToStruct(TimeCurrent(), dt);
   
   //--- Check Friday trading
   if(dt.day_of_week == 5 && !InpTradeFriday)
      return false;
   
   //--- Check trading hours
   if(dt.hour < InpSessionStartHour || dt.hour >= InpSessionEndHour)
      return false;
   
   return true;
}

//+------------------------------------------------------------------+
//| Cooldown period check                                             |
//+------------------------------------------------------------------+
bool PassesCooldownCheck()
{
   if(InpCooldownMinutes <= 0)
      return true;
   
   if(g_LastTradeTime == 0)
      return true;
   
   datetime cooldownEnd = g_LastTradeTime + InpCooldownMinutes * 60;
   
   if(TimeCurrent() < cooldownEnd)
   {
      if(InpDebugMode)
         Print("In cooldown period. Next trade allowed at: ", TimeToString(cooldownEnd));
      return false;
   }
   
   return true;
}

//+------------------------------------------------------------------+
//| Update indicator buffers                                          |
//+------------------------------------------------------------------+
bool UpdateIndicators()
{
   if(CopyBuffer(g_HandleFastMA, 0, 0, 3, g_FastMA) < 3) return false;
   if(CopyBuffer(g_HandleSlowMA, 0, 0, 3, g_SlowMA) < 3) return false;
   if(CopyBuffer(g_HandleRSI, 0, 0, 3, g_RSI) < 3)       return false;
   if(CopyBuffer(g_HandleATR, 0, 0, 3, g_ATR) < 3)       return false;
   
   return true;
}

//+------------------------------------------------------------------+
//| Generate trading signal                                           |
//|  Returns: 1 = Buy, -1 = Sell, 0 = No signal                      |
//+------------------------------------------------------------------+
int GenerateSignal()
{
   //--- MA Crossover + RSI Confirmation Strategy
   
   //--- Check for bullish signal
   bool maCrossUp = g_FastMA[1] <= g_SlowMA[1] && g_FastMA[0] > g_SlowMA[0];
   bool rsiOversold = g_RSI[1] < InpRSIOversold;
   
   if(maCrossUp && rsiOversold)
   {
      if(InpDebugMode)
         Print("BUY signal generated. FastMA: ", g_FastMA[0], " SlowMA: ", g_SlowMA[0], " RSI: ", g_RSI[1]);
      return 1;
   }
   
   //--- Check for bearish signal
   bool maCrossDown = g_FastMA[1] >= g_SlowMA[1] && g_FastMA[0] < g_SlowMA[0];
   bool rsiOverbought = g_RSI[1] > InpRSIOverbought;
   
   if(maCrossDown && rsiOverbought)
   {
      if(InpDebugMode)
         Print("SELL signal generated. FastMA: ", g_FastMA[0], " SlowMA: ", g_SlowMA[0], " RSI: ", g_RSI[1]);
      return -1;
   }
   
   return 0;
}

//+------------------------------------------------------------------+
//| Execute trading signal                                            |
//+------------------------------------------------------------------+
void ExecuteSignal(int signal)
{
   if(signal == 0)
      return;
   
   //--- Calculate lot size
   double lotSize = CalculateLotSize();
   if(lotSize < InpMinLotSize)
   {
      Print("Calculated lot size too small: ", lotSize);
      return;
   }
   
   //--- Calculate stop levels
   double sl, tp;
   CalculateStopLevels(signal, sl, tp);
   
   //--- Get current price
   double price = (signal > 0) ? g_SymbolInfo.Ask() : g_SymbolInfo.Bid();
   
   //--- Execute trade
   bool success = false;
   
   if(signal > 0)
   {
      success = g_Trade.Buy(lotSize, _Symbol, price, sl, tp, InpComment);
   }
   else
   {
      success = g_Trade.Sell(lotSize, _Symbol, price, sl, tp, InpComment);
   }
   
   //--- Handle result
   if(success)
   {
      g_LastTradeTime = TimeCurrent();
      g_TradesToday++;
      
      string direction = (signal > 0) ? "BUY" : "SELL";
      string message = StringFormat("%s executed. Lots: %.2f, Price: %.5f, SL: %.5f, TP: %.5f",
                                    direction, lotSize, price, sl, tp);
      
      SendNotification(message);
      
      if(InpDebugMode)
         Print(message);
   }
   else
   {
      Print("Trade failed. Error: ", g_Trade.ResultRetcode(), " - ", g_Trade.ResultRetcodeDescription());
   }
}

//+------------------------------------------------------------------+
//| Calculate position size based on risk                             |
//+------------------------------------------------------------------+
double CalculateLotSize()
{
   double balance = g_AccountInfo.Balance();
   double riskAmount = balance * InpRiskPercent / 100.0;
   
   //--- Get stop loss distance in points
   double slDistance;
   if(InpUseATRStops)
   {
      slDistance = g_ATR[0] * InpSLMultiplier / g_Point;
   }
   else
   {
      slDistance = InpFixedSLPips * 10;  // Convert pips to points
   }
   
   //--- Calculate lot size
   double tickValue = g_SymbolInfo.TickValue();
   double tickSize = g_SymbolInfo.TickSize();
   
   if(tickValue == 0 || tickSize == 0 || slDistance == 0)
      return InpMinLotSize;
   
   double lotSize = riskAmount / (slDistance * tickValue / tickSize);
   
   //--- Normalize lot size
   double lotStep = g_SymbolInfo.LotsStep();
   lotSize = MathFloor(lotSize / lotStep) * lotStep;
   
   //--- Apply limits
   lotSize = MathMax(InpMinLotSize, lotSize);
   lotSize = MathMin(InpMaxLotSize, lotSize);
   lotSize = MathMin(g_SymbolInfo.LotsMax(), lotSize);
   
   return NormalizeDouble(lotSize, 2);
}

//+------------------------------------------------------------------+
//| Calculate stop loss and take profit levels                        |
//+------------------------------------------------------------------+
void CalculateStopLevels(int signal, double &sl, double &tp)
{
   double price = (signal > 0) ? g_SymbolInfo.Ask() : g_SymbolInfo.Bid();
   double slDistance, tpDistance;
   
   if(InpUseATRStops)
   {
      slDistance = g_ATR[0] * InpSLMultiplier;
      tpDistance = g_ATR[0] * InpTPMultiplier;
   }
   else
   {
      slDistance = InpFixedSLPips * g_Point * 10;
      tpDistance = InpFixedTPPips * g_Point * 10;
   }
   
   if(signal > 0)  // Buy
   {
      sl = NormalizeDouble(price - slDistance, g_Digits);
      tp = NormalizeDouble(price + tpDistance, g_Digits);
   }
   else  // Sell
   {
      sl = NormalizeDouble(price + slDistance, g_Digits);
      tp = NormalizeDouble(price - tpDistance, g_Digits);
   }
}

//+------------------------------------------------------------------+
//| Count open positions for this EA                                  |
//+------------------------------------------------------------------+
int CountPositions()
{
   int count = 0;
   
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if(g_Position.SelectByIndex(i))
      {
         if(g_Position.Symbol() == _Symbol && g_Position.Magic() == InpMagicNumber)
            count++;
      }
   }
   
   return count;
}

//+------------------------------------------------------------------+
//| Manage open positions (trailing stop, breakeven, etc.)            |
//+------------------------------------------------------------------+
void ManagePositions()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if(!g_Position.SelectByIndex(i))
         continue;
      
      if(g_Position.Symbol() != _Symbol || g_Position.Magic() != InpMagicNumber)
         continue;
      
      //--- Add position management logic here
      //--- Examples: trailing stop, breakeven, partial close
      
      //--- Friday close logic
      if(InpCloseOnFriday)
      {
         MqlDateTime dt;
         TimeToStruct(TimeCurrent(), dt);
         
         if(dt.day_of_week == 5 && dt.hour >= 20)
         {
            g_Trade.PositionClose(g_Position.Ticket());
            SendNotification("Position closed for Friday EOD");
         }
      }
   }
}

//+------------------------------------------------------------------+
//| Send notification through configured channels                     |
//+------------------------------------------------------------------+
void SendNotification(string message)
{
   string fullMessage = StringFormat("[%s] %s: %s", _Symbol, InpComment, message);
   
   if(InpAlertNotify)
      Alert(fullMessage);
   
   if(InpPushNotify)
      SendNotification(fullMessage);
   
   if(InpEmailNotify)
      SendMail(InpComment + " Alert", fullMessage);
}

//+------------------------------------------------------------------+
//| Tester event handler                                              |
//+------------------------------------------------------------------+
double OnTester()
{
   //--- Custom optimization criterion
   //--- Return value used for optimization in Strategy Tester
   
   double profit = TesterStatistics(STAT_PROFIT);
   double drawdown = TesterStatistics(STAT_EQUITY_DDREL_PERCENT);
   double trades = TesterStatistics(STAT_TRADES);
   double winRate = TesterStatistics(STAT_TRADES) > 0 ? 
                    TesterStatistics(STAT_PROFIT_TRADES) / TesterStatistics(STAT_TRADES) * 100 : 0;
   
   //--- Avoid division by zero and penalize low trade count
   if(trades < 10 || drawdown <= 0)
      return 0;
   
   //--- Calculate custom criterion (profit factor adjusted by drawdown)
   double criterion = profit / drawdown * MathSqrt(trades);
   
   return criterion;
}

//+------------------------------------------------------------------+
//| Trade event handler                                               |
//+------------------------------------------------------------------+
void OnTrade()
{
   //--- Called when trade events occur
   //--- Can be used for additional trade tracking
}

//+------------------------------------------------------------------+
