# MQL5 Trading Skills

**Extracted from:** Ultimate System v19.0.37 (25 strategies, 240+ parameters)

---

## Quick Start

```mql5
// Include modular utilities
#include "Include/Risk/Risk_Manager.mqh"
#include "Include/Trading/Trade_Manager.mqh"
#include "Include/Utils/Logger.mqh"
#include "Include/Integration/Telegram.mqh"

// Initialize in OnInit()
CRiskManager   g_Risk;
CTradeManager  g_Trade;
CLogger        g_Log;
CTelegram      g_Telegram;

g_Risk.Init(_Symbol, PROPFIRM_FTMO);
g_Trade.Init(_Symbol, 123456, "MyEA");
g_Log.Init("MyEA", "logs/myea.log");
g_Telegram.Init("BOT_TOKEN", "CHAT_ID", "MyEA");
```

---

## Directory Structure

```
skills/mql5/
├── ea_template.mq5           # Complete EA template
├── Indicator_Template.mq5    # Custom indicator template
├── Include/
│   ├── Risk/
│   │   └── Risk_Manager.mqh  # PropFirm-compliant risk management
│   ├── Trading/
│   │   └── Trade_Manager.mqh # Trade execution & position management
│   ├── Utils/
│   │   └── Logger.mqh        # Multi-level logging system
│   ├── Integration/
│   │   └── Telegram.mqh      # Telegram bot notifications
│   └── Strategies/
│       └── Strategy_Base.mqh # Abstract strategy base class
├── risk_manager.mqh          # Legacy risk manager
├── trade_manager.mqh         # Legacy trade manager
├── strategy_base.mqh         # Legacy strategy base
├── indicator_wrapper.mqh     # Indicator caching
├── session_filter.mqh        # Trading hours control
├── news_filter.mqh           # Economic event filtering
└── python_bridge.mqh         # ML API integration
```

---

## Main Templates

| Template | Lines | Purpose |
|----------|-------|---------|
| `ea_template.mq5` | ~600 | Complete EA with risk management, signals, session filter |
| `Indicator_Template.mq5` | ~350 | Custom indicator with MTF support and alerts |

---

## Modular Utilities (Include/)

| Module | Class | Key Features |
|--------|-------|--------------|
| `Risk/Risk_Manager.mqh` | `CRiskManager` | PropFirm profiles (FTMO, FundedNext, MFF, E8), daily loss tracking, drawdown limits, position sizing |
| `Trading/Trade_Manager.mqh` | `CTradeManager` | Trade execution, trailing stops, breakeven, partial close, trade statistics |
| `Utils/Logger.mqh` | `CLogger` | DEBUG/INFO/WARN/ERROR/CRITICAL levels, file output, trade logging |
| `Integration/Telegram.mqh` | `CTelegram` | Rate-limited notifications, message queue, formatted alerts |
| `Strategies/Strategy_Base.mqh` | `CStrategyBase` | Abstract base class, signal generation, trend detection |

---

## Legacy Patterns

| # | Pattern | Template | Purpose |
|---|---------|----------|---------|
| 1 | Risk Manager | `risk_manager.mqh` | Position sizing, exposure |
| 2 | Indicator Wrapper | `indicator_wrapper.mqh` | Indicator caching |
| 3 | Trade Manager | `trade_manager.mqh` | Order execution |
| 4 | Strategy Base | `strategy_base.mqh` | Strategy interface |
| 5 | Session Filter | `session_filter.mqh` | Trading hours control |
| 6 | News Filter | `news_filter.mqh` | Economic event filtering |
| 7 | Python Bridge | `python_bridge.mqh` | ML API integration |

---

## MQL5 Architecture Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                     EXPERT ADVISOR (EA)                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   OnInit()  ───────► Initialize all modules                 │
│        │                                                     │
│        ▼                                                     │
│   OnTick()  ───────► For each price tick:                   │
│        │              1. Update indicators                   │
│        │              2. Check filters (session, news)       │
│        │              3. Generate signals                    │
│        │              4. Apply risk management               │
│        │              5. Execute trades                      │
│        │              6. Manage positions                    │
│        ▼                                                     │
│   OnDeinit() ──────► Cleanup resources                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Constants Pattern

Always define magic numbers and version constants:

```mql5
#define EA_VERSION "1.0.0"
#define EA_MAGIC   123456

// Per-symbol magic numbers (for multi-symbol EAs)
#define MAGIC_XAUUSD 100001
#define MAGIC_US30   100002
#define MAGIC_BTCUSD 100003
```

---

## Risk Management Rules

| Rule | Implementation |
|------|----------------|
| Max Risk/Trade | 1-2% of account |
| Max Daily Loss | 5% of account |
| Max Open Trades | 3-5 positions |
| Max Exposure | 30% per currency |
| Stop Loss | Required on all trades |

---

## Position Sizing Formula

```mql5
double CalculateLotSize(double riskPercent, double slPoints) {
    double accountRisk = AccountInfoDouble(ACCOUNT_BALANCE) * riskPercent / 100.0;
    double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
    double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
    double pointValue = tickValue / tickSize * _Point;

    double lots = accountRisk / (slPoints * pointValue);

    // Normalize to symbol constraints
    double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
    double maxLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
    double stepLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);

    lots = MathFloor(lots / stepLot) * stepLot;
    lots = MathMax(minLot, MathMin(maxLot, lots));

    return lots;
}
```

---

## Best Practices

### 1. Always Use Magic Numbers
Identify EA trades from manual trades.

### 2. Implement Error Handling
Check return codes on all trade operations.

### 3. Cache Indicator Values
Avoid recalculating on every tick.

### 4. Use Trailing Stops
Protect profits on winning trades.

### 5. Log Important Events
Keep audit trail for debugging.

---

## Dependencies

- MetaTrader 5 Terminal
- MQL5 Standard Library
- Optional: Python API for ML signals

---

## PropFirm Profiles

The Risk Manager supports pre-configured PropFirm limits:

| PropFirm | Daily Loss | Max Drawdown | Weekend Hold | News Trading |
|----------|------------|--------------|--------------|--------------|
| FTMO | 5% | 10% | ✅ | ✅ |
| FundedNext | 5% | 10% | ✅ | ✅ |
| MFF | 5% | 12% | ❌ | ❌ |
| E8 Funding | 5% | 8% | ✅ | ✅ |

```mql5
// Use PropFirm profile
CRiskManager risk;
risk.Init(_Symbol, PROPFIRM_FTMO);

// Or set custom limits
risk.SetLimits(4.0, 8.0, 5);  // 4% daily, 8% DD, 5 max positions
```

---

## EA Template Features

The `ea_template.mq5` includes:

- **Input Parameters**: Grouped settings for trading, risk, SL/TP, strategy, session, notifications
- **Risk Management**: Daily loss limits, max drawdown, position limits, cooldown
- **Session Filter**: Trading hours, Friday handling
- **Signal Generation**: MA crossover + RSI confirmation (customizable)
- **Position Sizing**: Risk-based lot calculation with ATR stops
- **Notifications**: Alert, push notification, email support

---

## Creating a New Strategy

1. Copy `ea_template.mq5` to your Experts folder
2. Modify `GenerateSignal()` with your entry logic
3. Adjust input parameters as needed
4. Configure PropFirm profile if applicable

```mql5
int GenerateSignal()
{
   // Your custom logic here
   // Return: 1 = Buy, -1 = Sell, 0 = No signal

   if(/* buy condition */)
      return 1;
   if(/* sell condition */)
      return -1;

   return 0;
}
```
