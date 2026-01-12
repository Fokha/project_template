//+------------------------------------------------------------------+
//|                                              Risk_Manager.mqh    |
//|                                         {{AUTHOR_NAME}}           |
//|                                         {{AUTHOR_URL}}            |
//+------------------------------------------------------------------+
#property copyright "{{AUTHOR_NAME}}"
#property link      "{{AUTHOR_URL}}"
#property version   "1.00"

// ═══════════════════════════════════════════════════════════════
// RISK MANAGER - Position Sizing & Exposure Control
// ═══════════════════════════════════════════════════════════════
//
// Features:
// - Position sizing based on risk percentage
// - Daily loss limit tracking
// - Currency exposure limits
// - Maximum position limits
// - Prop firm compliance
//
// ═══════════════════════════════════════════════════════════════

#include <Trade/Trade.mqh>
#include <Trade/PositionInfo.mqh>

// ═══════════════════════════════════════════════════════════════
// ENUMS
// ═══════════════════════════════════════════════════════════════

enum ENUM_RISK_LEVEL
{
    RISK_LOW = 0,        // Low risk (conservative)
    RISK_MEDIUM = 1,     // Medium risk (balanced)
    RISK_HIGH = 2,       // High risk (aggressive)
    RISK_EXTREME = 3     // Extreme (not recommended)
};

enum ENUM_CAPITAL_STATUS
{
    CAPITAL_NORMAL = 0,    // Normal trading
    CAPITAL_WARNING = 1,   // Approaching limits
    CAPITAL_CRITICAL = 2,  // Near daily limit
    CAPITAL_EMERGENCY = 3  // Trading suspended
};

// ═══════════════════════════════════════════════════════════════
// CLASS: CRiskManager
// ═══════════════════════════════════════════════════════════════

class CRiskManager
{
private:
    // Configuration
    double            m_RiskPercent;        // Risk per trade (%)
    double            m_MaxDailyLoss;       // Max daily loss (%)
    double            m_MaxCurrencyExposure; // Max per currency (%)
    int               m_MaxOpenTrades;      // Max concurrent trades
    double            m_MinLotSize;         // Minimum lot size
    double            m_MaxLotSize;         // Maximum lot size
    int               m_MagicNumber;        // EA magic number

    // State tracking
    double            m_DailyStartBalance;
    double            m_DailyStartEquity;
    datetime          m_LastDayCheck;
    int               m_TodayTrades;
    double            m_TodayPnL;

    // Objects
    CPositionInfo     m_Position;

public:
    // Constructor/Destructor
                      CRiskManager();
                     ~CRiskManager();

    // Initialization
    bool              Init(double riskPercent, double maxDailyLoss,
                          double maxExposure, int maxTrades, int magic);

    // Position sizing
    double            CalculateLotSize(string symbol, double slPoints);
    double            CalculateLotSizeByRisk(string symbol, double riskAmount, double slPoints);

    // Trade validation
    bool              CanOpenTrade(string symbol, ENUM_ORDER_TYPE orderType);
    bool              ValidateStopLoss(string symbol, double slPoints);
    bool              IsDailyLossReached();
    bool              IsMaxTradesReached();
    bool              IsExposureLimitReached(string currency);

    // Exposure tracking
    double            GetCurrencyExposure(string currency);
    double            GetTotalExposure();
    int               CountOpenTrades(string symbol = "");

    // Status
    ENUM_CAPITAL_STATUS GetCapitalStatus();
    ENUM_RISK_LEVEL   GetCurrentRiskLevel();
    double            GetRemainingDailyRisk();
    double            GetTodayPnL();

    // Utilities
    void              ResetDaily();
    void              UpdateDailyTracking();
    string            GetStatusReport();

private:
    // Internal methods
    string            GetBaseCurrency(string symbol);
    string            GetQuoteCurrency(string symbol);
    double            NormalizeLots(string symbol, double lots);
};

// ═══════════════════════════════════════════════════════════════
// IMPLEMENTATION
// ═══════════════════════════════════════════════════════════════

CRiskManager::CRiskManager()
{
    m_RiskPercent = 1.0;
    m_MaxDailyLoss = 5.0;
    m_MaxCurrencyExposure = 30.0;
    m_MaxOpenTrades = 3;
    m_MinLotSize = 0.01;
    m_MaxLotSize = 10.0;
    m_MagicNumber = 0;

    m_DailyStartBalance = 0;
    m_DailyStartEquity = 0;
    m_LastDayCheck = 0;
    m_TodayTrades = 0;
    m_TodayPnL = 0;
}

CRiskManager::~CRiskManager()
{
}

bool CRiskManager::Init(double riskPercent, double maxDailyLoss,
                       double maxExposure, int maxTrades, int magic)
{
    m_RiskPercent = MathMax(0.1, MathMin(10.0, riskPercent));
    m_MaxDailyLoss = MathMax(1.0, MathMin(20.0, maxDailyLoss));
    m_MaxCurrencyExposure = MathMax(10.0, MathMin(50.0, maxExposure));
    m_MaxOpenTrades = MathMax(1, MathMin(20, maxTrades));
    m_MagicNumber = magic;

    ResetDaily();

    Print("RiskManager initialized:");
    Print("  Risk/Trade: ", m_RiskPercent, "%");
    Print("  Max Daily Loss: ", m_MaxDailyLoss, "%");
    Print("  Max Exposure: ", m_MaxCurrencyExposure, "%");
    Print("  Max Trades: ", m_MaxOpenTrades);

    return true;
}

// ═══════════════════════════════════════════════════════════════
// POSITION SIZING
// ═══════════════════════════════════════════════════════════════

double CRiskManager::CalculateLotSize(string symbol, double slPoints)
{
    double balance = AccountInfoDouble(ACCOUNT_BALANCE);
    double riskAmount = balance * m_RiskPercent / 100.0;

    return CalculateLotSizeByRisk(symbol, riskAmount, slPoints);
}

double CRiskManager::CalculateLotSizeByRisk(string symbol, double riskAmount, double slPoints)
{
    if (slPoints <= 0) return m_MinLotSize;

    double tickValue = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE);
    double tickSize = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_SIZE);
    double point = SymbolInfoDouble(symbol, SYMBOL_POINT);

    if (tickSize <= 0 || point <= 0) return m_MinLotSize;

    double pointValue = tickValue / tickSize * point;
    if (pointValue <= 0) return m_MinLotSize;

    double lots = riskAmount / (slPoints * pointValue);

    return NormalizeLots(symbol, lots);
}

double CRiskManager::NormalizeLots(string symbol, double lots)
{
    double minLot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
    double maxLot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MAX);
    double stepLot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_STEP);

    lots = MathFloor(lots / stepLot) * stepLot;
    lots = MathMax(minLot, MathMin(maxLot, lots));
    lots = MathMax(m_MinLotSize, MathMin(m_MaxLotSize, lots));

    return NormalizeDouble(lots, 2);
}

// ═══════════════════════════════════════════════════════════════
// TRADE VALIDATION
// ═══════════════════════════════════════════════════════════════

bool CRiskManager::CanOpenTrade(string symbol, ENUM_ORDER_TYPE orderType)
{
    UpdateDailyTracking();

    // Check daily loss
    if (IsDailyLossReached())
    {
        Print("Trade blocked: Daily loss limit reached");
        return false;
    }

    // Check max trades
    if (IsMaxTradesReached())
    {
        Print("Trade blocked: Max trades limit reached");
        return false;
    }

    // Check currency exposure
    string baseCurrency = GetBaseCurrency(symbol);
    if (IsExposureLimitReached(baseCurrency))
    {
        Print("Trade blocked: ", baseCurrency, " exposure limit reached");
        return false;
    }

    return true;
}

bool CRiskManager::ValidateStopLoss(string symbol, double slPoints)
{
    double minSL = SymbolInfoInteger(symbol, SYMBOL_TRADE_STOPS_LEVEL) * _Point;
    return slPoints >= minSL;
}

bool CRiskManager::IsDailyLossReached()
{
    double balance = AccountInfoDouble(ACCOUNT_BALANCE);
    double dailyLoss = m_DailyStartBalance - balance;
    double maxLoss = m_DailyStartBalance * m_MaxDailyLoss / 100.0;

    return dailyLoss >= maxLoss;
}

bool CRiskManager::IsMaxTradesReached()
{
    return CountOpenTrades() >= m_MaxOpenTrades;
}

bool CRiskManager::IsExposureLimitReached(string currency)
{
    double exposure = GetCurrencyExposure(currency);
    return exposure >= m_MaxCurrencyExposure;
}

// ═══════════════════════════════════════════════════════════════
// EXPOSURE TRACKING
// ═══════════════════════════════════════════════════════════════

double CRiskManager::GetCurrencyExposure(string currency)
{
    double balance = AccountInfoDouble(ACCOUNT_BALANCE);
    if (balance <= 0) return 0;

    double exposure = 0;

    for (int i = PositionsTotal() - 1; i >= 0; i--)
    {
        if (!m_Position.SelectByIndex(i)) continue;
        if (m_MagicNumber > 0 && m_Position.Magic() != m_MagicNumber) continue;

        string symbol = m_Position.Symbol();
        string base = GetBaseCurrency(symbol);
        string quote = GetQuoteCurrency(symbol);

        if (base == currency || quote == currency)
        {
            double posValue = m_Position.Volume() *
                             SymbolInfoDouble(symbol, SYMBOL_TRADE_CONTRACT_SIZE) *
                             m_Position.PriceOpen();
            exposure += posValue;
        }
    }

    return (exposure / balance) * 100.0;
}

double CRiskManager::GetTotalExposure()
{
    double balance = AccountInfoDouble(ACCOUNT_BALANCE);
    if (balance <= 0) return 0;

    double totalExposure = 0;

    for (int i = PositionsTotal() - 1; i >= 0; i--)
    {
        if (!m_Position.SelectByIndex(i)) continue;
        if (m_MagicNumber > 0 && m_Position.Magic() != m_MagicNumber) continue;

        string symbol = m_Position.Symbol();
        double posValue = m_Position.Volume() *
                         SymbolInfoDouble(symbol, SYMBOL_TRADE_CONTRACT_SIZE) *
                         m_Position.PriceOpen();
        totalExposure += posValue;
    }

    return (totalExposure / balance) * 100.0;
}

int CRiskManager::CountOpenTrades(string symbol = "")
{
    int count = 0;

    for (int i = PositionsTotal() - 1; i >= 0; i--)
    {
        if (!m_Position.SelectByIndex(i)) continue;
        if (m_MagicNumber > 0 && m_Position.Magic() != m_MagicNumber) continue;
        if (symbol != "" && m_Position.Symbol() != symbol) continue;

        count++;
    }

    return count;
}

// ═══════════════════════════════════════════════════════════════
// STATUS
// ═══════════════════════════════════════════════════════════════

ENUM_CAPITAL_STATUS CRiskManager::GetCapitalStatus()
{
    double balance = AccountInfoDouble(ACCOUNT_BALANCE);
    double dailyLoss = m_DailyStartBalance - balance;
    double maxLoss = m_DailyStartBalance * m_MaxDailyLoss / 100.0;

    double lossRatio = dailyLoss / maxLoss;

    if (lossRatio >= 1.0) return CAPITAL_EMERGENCY;
    if (lossRatio >= 0.8) return CAPITAL_CRITICAL;
    if (lossRatio >= 0.5) return CAPITAL_WARNING;
    return CAPITAL_NORMAL;
}

ENUM_RISK_LEVEL CRiskManager::GetCurrentRiskLevel()
{
    double exposure = GetTotalExposure();

    if (exposure >= 80) return RISK_EXTREME;
    if (exposure >= 50) return RISK_HIGH;
    if (exposure >= 30) return RISK_MEDIUM;
    return RISK_LOW;
}

double CRiskManager::GetRemainingDailyRisk()
{
    double balance = AccountInfoDouble(ACCOUNT_BALANCE);
    double dailyLoss = m_DailyStartBalance - balance;
    double maxLoss = m_DailyStartBalance * m_MaxDailyLoss / 100.0;

    return MathMax(0, maxLoss - dailyLoss);
}

double CRiskManager::GetTodayPnL()
{
    return AccountInfoDouble(ACCOUNT_BALANCE) - m_DailyStartBalance;
}

// ═══════════════════════════════════════════════════════════════
// UTILITIES
// ═══════════════════════════════════════════════════════════════

void CRiskManager::ResetDaily()
{
    m_DailyStartBalance = AccountInfoDouble(ACCOUNT_BALANCE);
    m_DailyStartEquity = AccountInfoDouble(ACCOUNT_EQUITY);
    m_LastDayCheck = TimeCurrent();
    m_TodayTrades = 0;
    m_TodayPnL = 0;
}

void CRiskManager::UpdateDailyTracking()
{
    MqlDateTime dt_now, dt_last;
    TimeToStruct(TimeCurrent(), dt_now);
    TimeToStruct(m_LastDayCheck, dt_last);

    // Reset on new day
    if (dt_now.day != dt_last.day)
    {
        ResetDaily();
    }
}

string CRiskManager::GetStatusReport()
{
    string report = "\n";
    report += "═══════════════════════════════════════\n";
    report += "         RISK MANAGER STATUS           \n";
    report += "═══════════════════════════════════════\n";
    report += "Balance:      $" + DoubleToString(AccountInfoDouble(ACCOUNT_BALANCE), 2) + "\n";
    report += "Today P/L:    $" + DoubleToString(GetTodayPnL(), 2) + "\n";
    report += "Remaining:    $" + DoubleToString(GetRemainingDailyRisk(), 2) + "\n";
    report += "Open Trades:  " + IntegerToString(CountOpenTrades()) + "/" + IntegerToString(m_MaxOpenTrades) + "\n";
    report += "Exposure:     " + DoubleToString(GetTotalExposure(), 1) + "%\n";
    report += "Status:       " + EnumToString(GetCapitalStatus()) + "\n";
    report += "═══════════════════════════════════════\n";

    return report;
}

string CRiskManager::GetBaseCurrency(string symbol)
{
    return StringSubstr(symbol, 0, 3);
}

string CRiskManager::GetQuoteCurrency(string symbol)
{
    return StringSubstr(symbol, 3, 3);
}

//+------------------------------------------------------------------+
