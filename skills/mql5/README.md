# MQL5 Trading Skills

**Extracted from:** Ultimate System v19.0.37 (25 strategies, 240+ parameters)

---

## Patterns in This Directory

| # | Pattern | Template | Purpose |
|---|---------|----------|---------|
| 1 | Expert Advisor Structure | `ea_template.mq5` | Complete EA skeleton |
| 2 | Risk Manager | `risk_manager.mqh` | Position sizing, exposure |
| 3 | Indicator Wrapper | `indicator_wrapper.mqh` | Indicator caching |
| 4 | Trade Manager | `trade_manager.mqh` | Order execution |
| 5 | Strategy Base | `strategy_base.mqh` | Strategy interface |
| 6 | Session Filter | `session_filter.mqh` | Trading hours control |
| 7 | News Filter | `news_filter.mqh` | Economic event filtering |
| 8 | Python Bridge | `python_bridge.mqh` | ML API integration |

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
