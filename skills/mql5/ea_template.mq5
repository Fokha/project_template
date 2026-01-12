//+------------------------------------------------------------------+
//|                                            {{EA_NAME}}.mq5        |
//|                                         {{AUTHOR_NAME}}           |
//|                                         {{AUTHOR_URL}}            |
//+------------------------------------------------------------------+
#property copyright "{{AUTHOR_NAME}}"
#property link      "{{AUTHOR_URL}}"
#property version   "1.00"
#property description "{{EA_DESCRIPTION}}"
#property strict

// ═══════════════════════════════════════════════════════════════
// INCLUDES
// ═══════════════════════════════════════════════════════════════

#include <Trade/Trade.mqh>
#include <Trade/PositionInfo.mqh>
#include <Trade/SymbolInfo.mqh>

// Include your custom modules
// #include "Include/Risk/Risk_Manager.mqh"
// #include "Include/Indicators/Indicators.mqh"
// #include "Include/Strategies/Strategy_Base.mqh"

// ═══════════════════════════════════════════════════════════════
// CONSTANTS
// ═══════════════════════════════════════════════════════════════

#define EA_VERSION "1.0.0"
#define EA_MAGIC   {{MAGIC_NUMBER}}

// ═══════════════════════════════════════════════════════════════
// INPUT PARAMETERS
// ═══════════════════════════════════════════════════════════════

// --- General Settings ---
input group "=== General Settings ==="
input int         InpMagicNumber    = EA_MAGIC;    // Magic Number
input string      InpComment        = "{{EA_NAME}}"; // Trade Comment
input bool        InpEnableTrading  = true;        // Enable Trading

// --- Risk Management ---
input group "=== Risk Management ==="
input double      InpRiskPercent    = 1.0;         // Risk per Trade (%)
input double      InpMaxDailyLoss   = 5.0;         // Max Daily Loss (%)
input int         InpMaxOpenTrades  = 3;           // Max Open Trades
input double      InpMinLotSize     = 0.01;        // Minimum Lot Size
input double      InpMaxLotSize     = 10.0;        // Maximum Lot Size

// --- Stop Loss & Take Profit ---
input group "=== SL/TP Settings ==="
input double      InpSLMultiplier   = 2.0;         // SL ATR Multiplier
input double      InpTPMultiplier   = 3.0;         // TP ATR Multiplier
input int         InpATRPeriod      = 14;          // ATR Period
input bool        InpUseTrailingStop = true;       // Use Trailing Stop
input double      InpTrailMultiplier = 1.5;        // Trailing ATR Multiplier

// --- Strategy Settings ---
input group "=== Strategy Settings ==="
input int         InpFastMA         = 9;           // Fast MA Period
input int         InpSlowMA         = 21;          // Slow MA Period
input int         InpRSIPeriod      = 14;          // RSI Period
input double      InpRSIOverbought  = 70;          // RSI Overbought
input double      InpRSIOversold    = 30;          // RSI Oversold

// --- Session Filter ---
input group "=== Session Filter ==="
input bool        InpUseSessionFilter = true;      // Enable Session Filter
input int         InpSessionStart   = 8;           // Session Start Hour (Server)
input int         InpSessionEnd     = 20;          // Session End Hour (Server)

// ═══════════════════════════════════════════════════════════════
// GLOBAL VARIABLES
// ═══════════════════════════════════════════════════════════════

// Trading objects
CTrade            g_Trade;
CPositionInfo     g_Position;
CSymbolInfo       g_Symbol;

// Indicator handles
int               g_HandleATR;
int               g_HandleFastMA;
int               g_HandleSlowMA;
int               g_HandleRSI;

// Indicator buffers
double            g_BufferATR[];
double            g_BufferFastMA[];
double            g_BufferSlowMA[];
double            g_BufferRSI[];

// State tracking
datetime          g_LastBarTime = 0;
double            g_DailyStartBalance = 0;
int               g_TodayTrades = 0;

// ═══════════════════════════════════════════════════════════════
// INITIALIZATION
// ═══════════════════════════════════════════════════════════════

int OnInit()
{
    // Log version
    Print("═══════════════════════════════════════════════════════");
    Print("{{EA_NAME}} v", EA_VERSION, " initializing...");
    Print("═══════════════════════════════════════════════════════");

    // Initialize symbol info
    if (!g_Symbol.Name(_Symbol))
    {
        Print("ERROR: Failed to initialize symbol info");
        return INIT_FAILED;
    }

    // Initialize trade object
    g_Trade.SetExpertMagicNumber(InpMagicNumber);
    g_Trade.SetDeviationInPoints(10);
    g_Trade.SetTypeFilling(ORDER_FILLING_IOC);

    // Create indicator handles
    g_HandleATR = iATR(_Symbol, PERIOD_CURRENT, InpATRPeriod);
    g_HandleFastMA = iMA(_Symbol, PERIOD_CURRENT, InpFastMA, 0, MODE_EMA, PRICE_CLOSE);
    g_HandleSlowMA = iMA(_Symbol, PERIOD_CURRENT, InpSlowMA, 0, MODE_EMA, PRICE_CLOSE);
    g_HandleRSI = iRSI(_Symbol, PERIOD_CURRENT, InpRSIPeriod, PRICE_CLOSE);

    // Validate handles
    if (g_HandleATR == INVALID_HANDLE ||
        g_HandleFastMA == INVALID_HANDLE ||
        g_HandleSlowMA == INVALID_HANDLE ||
        g_HandleRSI == INVALID_HANDLE)
    {
        Print("ERROR: Failed to create indicator handles");
        return INIT_FAILED;
    }

    // Set array direction
    ArraySetAsSeries(g_BufferATR, true);
    ArraySetAsSeries(g_BufferFastMA, true);
    ArraySetAsSeries(g_BufferSlowMA, true);
    ArraySetAsSeries(g_BufferRSI, true);

    // Initialize daily tracking
    g_DailyStartBalance = AccountInfoDouble(ACCOUNT_BALANCE);

    Print("{{EA_NAME}} initialized successfully!");
    return INIT_SUCCEEDED;
}

// ═══════════════════════════════════════════════════════════════
// DEINITIALIZATION
// ═══════════════════════════════════════════════════════════════

void OnDeinit(const int reason)
{
    // Release indicator handles
    if (g_HandleATR != INVALID_HANDLE) IndicatorRelease(g_HandleATR);
    if (g_HandleFastMA != INVALID_HANDLE) IndicatorRelease(g_HandleFastMA);
    if (g_HandleSlowMA != INVALID_HANDLE) IndicatorRelease(g_HandleSlowMA);
    if (g_HandleRSI != INVALID_HANDLE) IndicatorRelease(g_HandleRSI);

    Print("{{EA_NAME}} deinitialized. Reason: ", GetDeinitReasonText(reason));
}

// ═══════════════════════════════════════════════════════════════
// MAIN TICK HANDLER
// ═══════════════════════════════════════════════════════════════

void OnTick()
{
    // Check if trading is enabled
    if (!InpEnableTrading) return;

    // Check for new bar (optional: trade only on new bars)
    if (!IsNewBar()) return;

    // Update indicator values
    if (!UpdateIndicators()) return;

    // Check session filter
    if (InpUseSessionFilter && !IsWithinSession()) return;

    // Check daily loss limit
    if (IsDailyLossLimitReached()) return;

    // Manage existing positions
    ManagePositions();

    // Check for new signals
    int signal = GetSignal();

    // Execute trade if signal and conditions met
    if (signal != 0 && CanOpenNewTrade())
    {
        ExecuteTrade(signal);
    }
}

// ═══════════════════════════════════════════════════════════════
// SIGNAL GENERATION
// ═══════════════════════════════════════════════════════════════

int GetSignal()
{
    // Simple EMA crossover + RSI confirmation
    // Returns: 1 = BUY, -1 = SELL, 0 = NO SIGNAL

    double fastMA_curr = g_BufferFastMA[0];
    double fastMA_prev = g_BufferFastMA[1];
    double slowMA_curr = g_BufferSlowMA[0];
    double slowMA_prev = g_BufferSlowMA[1];
    double rsi = g_BufferRSI[0];

    // BUY Signal: Fast MA crosses above Slow MA + RSI not overbought
    if (fastMA_prev <= slowMA_prev && fastMA_curr > slowMA_curr)
    {
        if (rsi < InpRSIOverbought)
        {
            return 1;  // BUY
        }
    }

    // SELL Signal: Fast MA crosses below Slow MA + RSI not oversold
    if (fastMA_prev >= slowMA_prev && fastMA_curr < slowMA_curr)
    {
        if (rsi > InpRSIOversold)
        {
            return -1;  // SELL
        }
    }

    return 0;  // NO SIGNAL
}

// ═══════════════════════════════════════════════════════════════
// TRADE EXECUTION
// ═══════════════════════════════════════════════════════════════

bool ExecuteTrade(int signal)
{
    g_Symbol.RefreshRates();

    double atr = g_BufferATR[0];
    double slPoints = atr * InpSLMultiplier / _Point;
    double tpPoints = atr * InpTPMultiplier / _Point;

    // Calculate lot size
    double lots = CalculateLotSize(InpRiskPercent, slPoints);

    // Get prices
    double price, sl, tp;

    if (signal > 0)  // BUY
    {
        price = g_Symbol.Ask();
        sl = price - (slPoints * _Point);
        tp = price + (tpPoints * _Point);

        if (g_Trade.Buy(lots, _Symbol, price, sl, tp, InpComment))
        {
            Print("BUY order opened: ", lots, " lots at ", price);
            g_TodayTrades++;
            return true;
        }
    }
    else if (signal < 0)  // SELL
    {
        price = g_Symbol.Bid();
        sl = price + (slPoints * _Point);
        tp = price - (tpPoints * _Point);

        if (g_Trade.Sell(lots, _Symbol, price, sl, tp, InpComment))
        {
            Print("SELL order opened: ", lots, " lots at ", price);
            g_TodayTrades++;
            return true;
        }
    }

    Print("ERROR: Trade execution failed. Error: ", GetLastError());
    return false;
}

// ═══════════════════════════════════════════════════════════════
// POSITION MANAGEMENT
// ═══════════════════════════════════════════════════════════════

void ManagePositions()
{
    if (!InpUseTrailingStop) return;

    for (int i = PositionsTotal() - 1; i >= 0; i--)
    {
        if (!g_Position.SelectByIndex(i)) continue;
        if (g_Position.Magic() != InpMagicNumber) continue;
        if (g_Position.Symbol() != _Symbol) continue;

        TrailPosition();
    }
}

void TrailPosition()
{
    double atr = g_BufferATR[0];
    double trailDistance = atr * InpTrailMultiplier;

    double currentSL = g_Position.StopLoss();
    double openPrice = g_Position.PriceOpen();
    double currentPrice = g_Position.PriceCurrent();

    double newSL = 0;

    if (g_Position.PositionType() == POSITION_TYPE_BUY)
    {
        newSL = currentPrice - trailDistance;
        if (newSL > currentSL && newSL > openPrice)
        {
            g_Trade.PositionModify(g_Position.Ticket(), newSL, g_Position.TakeProfit());
        }
    }
    else if (g_Position.PositionType() == POSITION_TYPE_SELL)
    {
        newSL = currentPrice + trailDistance;
        if ((newSL < currentSL || currentSL == 0) && newSL < openPrice)
        {
            g_Trade.PositionModify(g_Position.Ticket(), newSL, g_Position.TakeProfit());
        }
    }
}

// ═══════════════════════════════════════════════════════════════
// RISK MANAGEMENT
// ═══════════════════════════════════════════════════════════════

double CalculateLotSize(double riskPercent, double slPoints)
{
    double accountRisk = AccountInfoDouble(ACCOUNT_BALANCE) * riskPercent / 100.0;
    double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
    double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
    double pointValue = tickValue / tickSize * _Point;

    if (pointValue <= 0) return InpMinLotSize;

    double lots = accountRisk / (slPoints * pointValue);

    // Normalize to symbol constraints
    double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
    double maxLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
    double stepLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);

    lots = MathFloor(lots / stepLot) * stepLot;
    lots = MathMax(minLot, MathMin(maxLot, lots));
    lots = MathMax(InpMinLotSize, MathMin(InpMaxLotSize, lots));

    return lots;
}

bool CanOpenNewTrade()
{
    int openTrades = CountOpenTrades();
    return openTrades < InpMaxOpenTrades;
}

int CountOpenTrades()
{
    int count = 0;
    for (int i = PositionsTotal() - 1; i >= 0; i--)
    {
        if (g_Position.SelectByIndex(i))
        {
            if (g_Position.Magic() == InpMagicNumber && g_Position.Symbol() == _Symbol)
            {
                count++;
            }
        }
    }
    return count;
}

bool IsDailyLossLimitReached()
{
    double currentBalance = AccountInfoDouble(ACCOUNT_BALANCE);
    double dailyLoss = g_DailyStartBalance - currentBalance;
    double maxLoss = g_DailyStartBalance * InpMaxDailyLoss / 100.0;

    if (dailyLoss >= maxLoss)
    {
        Print("Daily loss limit reached: ", dailyLoss, " / ", maxLoss);
        return true;
    }
    return false;
}

// ═══════════════════════════════════════════════════════════════
// HELPER FUNCTIONS
// ═══════════════════════════════════════════════════════════════

bool IsNewBar()
{
    datetime currentBarTime = iTime(_Symbol, PERIOD_CURRENT, 0);
    if (currentBarTime != g_LastBarTime)
    {
        g_LastBarTime = currentBarTime;
        return true;
    }
    return false;
}

bool UpdateIndicators()
{
    if (CopyBuffer(g_HandleATR, 0, 0, 3, g_BufferATR) < 3) return false;
    if (CopyBuffer(g_HandleFastMA, 0, 0, 3, g_BufferFastMA) < 3) return false;
    if (CopyBuffer(g_HandleSlowMA, 0, 0, 3, g_BufferSlowMA) < 3) return false;
    if (CopyBuffer(g_HandleRSI, 0, 0, 3, g_BufferRSI) < 3) return false;
    return true;
}

bool IsWithinSession()
{
    MqlDateTime dt;
    TimeToStruct(TimeCurrent(), dt);
    int hour = dt.hour;

    return (hour >= InpSessionStart && hour < InpSessionEnd);
}

string GetDeinitReasonText(int reason)
{
    switch (reason)
    {
        case REASON_PROGRAM:     return "Program ended";
        case REASON_REMOVE:      return "Removed from chart";
        case REASON_RECOMPILE:   return "Recompiled";
        case REASON_CHARTCHANGE: return "Chart changed";
        case REASON_CHARTCLOSE:  return "Chart closed";
        case REASON_PARAMETERS:  return "Parameters changed";
        case REASON_ACCOUNT:     return "Account changed";
        case REASON_TEMPLATE:    return "Template applied";
        case REASON_INITFAILED:  return "Init failed";
        case REASON_CLOSE:       return "Terminal closed";
        default:                 return "Unknown reason";
    }
}
//+------------------------------------------------------------------+
