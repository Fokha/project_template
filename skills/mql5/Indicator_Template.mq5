//+------------------------------------------------------------------+
//|                                          Indicator_Template.mq5  |
//|                                     Custom Indicator Template    |
//|                               Multi-timeframe signal indicator   |
//+------------------------------------------------------------------+
#property copyright "Your Name"
#property link      "https://www.example.com"
#property version   "1.00"
#property strict

#property indicator_chart_window
#property indicator_buffers 4
#property indicator_plots   2

//--- Plot settings for arrows
#property indicator_label1  "Buy Signal"
#property indicator_type1   DRAW_ARROW
#property indicator_color1  clrLime
#property indicator_style1  STYLE_SOLID
#property indicator_width1  2

#property indicator_label2  "Sell Signal"
#property indicator_type2   DRAW_ARROW
#property indicator_color2  clrRed
#property indicator_style2  STYLE_SOLID
#property indicator_width2  2

//+------------------------------------------------------------------+
//| Input Parameters                                                  |
//+------------------------------------------------------------------+
input group "=== Indicator Settings ==="
input int      InpFastMA           = 10;            // Fast MA Period
input int      InpSlowMA           = 20;            // Slow MA Period
input ENUM_MA_METHOD InpMAMethod   = MODE_EMA;      // MA Method
input int      InpRSIPeriod        = 14;            // RSI Period
input int      InpRSIOverbought    = 70;            // RSI Overbought
input int      InpRSIOversold      = 30;            // RSI Oversold

input group "=== Signal Settings ==="
input bool     InpShowArrows       = true;          // Show Signal Arrows
input bool     InpShowAlerts       = true;          // Show Alerts
input bool     InpPushNotify       = false;         // Push Notifications
input int      InpArrowOffset      = 10;            // Arrow Offset (points)

input group "=== Multi-Timeframe ==="
input bool     InpUseMTF           = true;          // Use Multi-Timeframe Filter
input ENUM_TIMEFRAMES InpHTF       = PERIOD_H4;     // Higher Timeframe

//+------------------------------------------------------------------+
//| Indicator Buffers                                                 |
//+------------------------------------------------------------------+
double g_BuyBuffer[];
double g_SellBuffer[];
double g_TrendBuffer[];    // Internal - trend direction
double g_StrengthBuffer[]; // Internal - signal strength

//+------------------------------------------------------------------+
//| Indicator Handles                                                 |
//+------------------------------------------------------------------+
int g_HandleFastMA;
int g_HandleSlowMA;
int g_HandleRSI;
int g_HandleHTF_MA;  // Higher timeframe MA

//+------------------------------------------------------------------+
//| Global Variables                                                  |
//+------------------------------------------------------------------+
datetime g_LastAlertTime = 0;
string   g_IndicatorName;

//+------------------------------------------------------------------+
//| Custom indicator initialization function                          |
//+------------------------------------------------------------------+
int OnInit()
{
   //--- Validate inputs
   if(InpFastMA >= InpSlowMA)
   {
      Print("Error: Fast MA period must be less than Slow MA period");
      return INIT_PARAMETERS_INCORRECT;
   }
   
   //--- Set indicator buffers
   SetIndexBuffer(0, g_BuyBuffer, INDICATOR_DATA);
   SetIndexBuffer(1, g_SellBuffer, INDICATOR_DATA);
   SetIndexBuffer(2, g_TrendBuffer, INDICATOR_CALCULATIONS);
   SetIndexBuffer(3, g_StrengthBuffer, INDICATOR_CALCULATIONS);
   
   //--- Set arrow codes
   PlotIndexSetInteger(0, PLOT_ARROW, 233);  // Up arrow
   PlotIndexSetInteger(1, PLOT_ARROW, 234);  // Down arrow
   
   //--- Set empty value
   PlotIndexSetDouble(0, PLOT_EMPTY_VALUE, EMPTY_VALUE);
   PlotIndexSetDouble(1, PLOT_EMPTY_VALUE, EMPTY_VALUE);
   
   //--- Create indicator handles
   g_HandleFastMA = iMA(_Symbol, PERIOD_CURRENT, InpFastMA, 0, InpMAMethod, PRICE_CLOSE);
   g_HandleSlowMA = iMA(_Symbol, PERIOD_CURRENT, InpSlowMA, 0, InpMAMethod, PRICE_CLOSE);
   g_HandleRSI    = iRSI(_Symbol, PERIOD_CURRENT, InpRSIPeriod, PRICE_CLOSE);
   
   if(InpUseMTF)
      g_HandleHTF_MA = iMA(_Symbol, InpHTF, InpSlowMA, 0, InpMAMethod, PRICE_CLOSE);
   
   //--- Validate handles
   if(g_HandleFastMA == INVALID_HANDLE || g_HandleSlowMA == INVALID_HANDLE || 
      g_HandleRSI == INVALID_HANDLE)
   {
      Print("Failed to create indicator handles");
      return INIT_FAILED;
   }
   
   //--- Set indicator name
   g_IndicatorName = StringFormat("Signal(%d,%d)", InpFastMA, InpSlowMA);
   IndicatorSetString(INDICATOR_SHORTNAME, g_IndicatorName);
   
   //--- Set accuracy
   IndicatorSetInteger(INDICATOR_DIGITS, _Digits);
   
   Print("Indicator initialized: ", g_IndicatorName);
   
   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Custom indicator deinitialization function                        |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   //--- Release handles
   if(g_HandleFastMA != INVALID_HANDLE) IndicatorRelease(g_HandleFastMA);
   if(g_HandleSlowMA != INVALID_HANDLE) IndicatorRelease(g_HandleSlowMA);
   if(g_HandleRSI != INVALID_HANDLE)    IndicatorRelease(g_HandleRSI);
   if(g_HandleHTF_MA != INVALID_HANDLE) IndicatorRelease(g_HandleHTF_MA);
   
   //--- Remove objects
   ObjectsDeleteAll(0, "Signal_");
   
   Print("Indicator deinitialized. Reason: ", reason);
}

//+------------------------------------------------------------------+
//| Custom indicator iteration function                               |
//+------------------------------------------------------------------+
int OnCalculate(const int rates_total,
                const int prev_calculated,
                const datetime &time[],
                const double &open[],
                const double &high[],
                const double &low[],
                const double &close[],
                const long &tick_volume[],
                const long &volume[],
                const int &spread[])
{
   //--- Check for minimum bars
   if(rates_total < InpSlowMA + 10)
      return 0;
   
   //--- Get indicator data
   double fastMA[], slowMA[], rsi[], htfMA[];
   ArraySetAsSeries(fastMA, true);
   ArraySetAsSeries(slowMA, true);
   ArraySetAsSeries(rsi, true);
   ArraySetAsSeries(htfMA, true);
   
   //--- Copy indicator buffers
   int toCopy = rates_total - prev_calculated + 1;
   if(prev_calculated == 0)
      toCopy = rates_total;
   
   if(CopyBuffer(g_HandleFastMA, 0, 0, toCopy, fastMA) <= 0) return 0;
   if(CopyBuffer(g_HandleSlowMA, 0, 0, toCopy, slowMA) <= 0) return 0;
   if(CopyBuffer(g_HandleRSI, 0, 0, toCopy, rsi) <= 0)       return 0;
   
   if(InpUseMTF && g_HandleHTF_MA != INVALID_HANDLE)
      CopyBuffer(g_HandleHTF_MA, 0, 0, toCopy, htfMA);
   
   //--- Set arrays as series
   ArraySetAsSeries(g_BuyBuffer, true);
   ArraySetAsSeries(g_SellBuffer, true);
   ArraySetAsSeries(g_TrendBuffer, true);
   ArraySetAsSeries(g_StrengthBuffer, true);
   ArraySetAsSeries(time, true);
   ArraySetAsSeries(high, true);
   ArraySetAsSeries(low, true);
   ArraySetAsSeries(close, true);
   
   //--- Calculate start position
   int start;
   if(prev_calculated == 0)
   {
      start = rates_total - InpSlowMA - 2;
      
      //--- Initialize buffers
      for(int i = rates_total - 1; i >= 0; i--)
      {
         g_BuyBuffer[i] = EMPTY_VALUE;
         g_SellBuffer[i] = EMPTY_VALUE;
         g_TrendBuffer[i] = 0;
         g_StrengthBuffer[i] = 0;
      }
   }
   else
   {
      start = rates_total - prev_calculated;
   }
   
   //--- Main calculation loop
   for(int i = start; i >= 0; i--)
   {
      //--- Initialize current bar
      g_BuyBuffer[i] = EMPTY_VALUE;
      g_SellBuffer[i] = EMPTY_VALUE;
      
      //--- Skip if not enough data
      if(i + 1 >= ArraySize(fastMA) || i + 1 >= ArraySize(slowMA))
         continue;
      
      //--- Determine trend direction
      if(fastMA[i] > slowMA[i])
         g_TrendBuffer[i] = 1;  // Bullish
      else if(fastMA[i] < slowMA[i])
         g_TrendBuffer[i] = -1; // Bearish
      else
         g_TrendBuffer[i] = 0;  // Neutral
      
      //--- Calculate signal strength (0-100)
      double maDiff = MathAbs(fastMA[i] - slowMA[i]) / slowMA[i] * 1000;
      double rsiStrength = (rsi[i] > 50) ? (rsi[i] - 50) * 2 : (50 - rsi[i]) * 2;
      g_StrengthBuffer[i] = (maDiff + rsiStrength) / 2;
      
      //--- Check for crossover signals
      bool maCrossUp = fastMA[i+1] <= slowMA[i+1] && fastMA[i] > slowMA[i];
      bool maCrossDown = fastMA[i+1] >= slowMA[i+1] && fastMA[i] < slowMA[i];
      
      //--- RSI confirmation
      bool rsiOversold = rsi[i+1] < InpRSIOversold;
      bool rsiOverbought = rsi[i+1] > InpRSIOverbought;
      
      //--- HTF filter
      bool htfBullish = true;
      bool htfBearish = true;
      
      if(InpUseMTF && ArraySize(htfMA) > i)
      {
         htfBullish = close[i] > htfMA[i];
         htfBearish = close[i] < htfMA[i];
      }
      
      //--- Generate buy signal
      if(maCrossUp && rsiOversold && htfBullish && InpShowArrows)
      {
         double offset = InpArrowOffset * _Point;
         g_BuyBuffer[i] = low[i] - offset;
         
         //--- Alert on bar 0 only
         if(i == 0)
            TriggerAlert("BUY", time[i], close[i]);
      }
      
      //--- Generate sell signal
      if(maCrossDown && rsiOverbought && htfBearish && InpShowArrows)
      {
         double offset = InpArrowOffset * _Point;
         g_SellBuffer[i] = high[i] + offset;
         
         //--- Alert on bar 0 only
         if(i == 0)
            TriggerAlert("SELL", time[i], close[i]);
      }
   }
   
   return rates_total;
}

//+------------------------------------------------------------------+
//| Trigger alert and notifications                                   |
//+------------------------------------------------------------------+
void TriggerAlert(string signal, datetime time, double price)
{
   //--- Prevent duplicate alerts
   if(time == g_LastAlertTime)
      return;
   
   g_LastAlertTime = time;
   
   string message = StringFormat("%s Signal on %s at %.5f", signal, _Symbol, price);
   
   if(InpShowAlerts)
      Alert(message);
   
   if(InpPushNotify)
      SendNotification(message);
   
   Print(message);
}

//+------------------------------------------------------------------+
//| Get current trend direction                                       |
//+------------------------------------------------------------------+
int GetTrend(int shift = 0)
{
   if(shift >= ArraySize(g_TrendBuffer))
      return 0;
   
   return (int)g_TrendBuffer[shift];
}

//+------------------------------------------------------------------+
//| Get signal strength                                               |
//+------------------------------------------------------------------+
double GetStrength(int shift = 0)
{
   if(shift >= ArraySize(g_StrengthBuffer))
      return 0;
   
   return g_StrengthBuffer[shift];
}

//+------------------------------------------------------------------+
//| Check if buy signal exists at bar                                 |
//+------------------------------------------------------------------+
bool HasBuySignal(int shift = 1)
{
   if(shift >= ArraySize(g_BuyBuffer))
      return false;
   
   return g_BuyBuffer[shift] != EMPTY_VALUE;
}

//+------------------------------------------------------------------+
//| Check if sell signal exists at bar                                |
//+------------------------------------------------------------------+
bool HasSellSignal(int shift = 1)
{
   if(shift >= ArraySize(g_SellBuffer))
      return false;
   
   return g_SellBuffer[shift] != EMPTY_VALUE;
}
//+------------------------------------------------------------------+
