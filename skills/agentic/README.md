# Agentic AI Skills

**Extracted from:** Fokha Trading System - 20 Implemented Patterns

---

## Overview

This directory contains the **20 agentic design patterns** that were fully implemented in the Fokha Trading System. Each pattern is a proven approach to building autonomous AI agents.

---

## Pattern Categories

```
┌─────────────────────────────────────────────────────────────┐
│                    20 AGENTIC PATTERNS                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  CORE (3)                 EXECUTION (3)                      │
│  ├── Prompt Chaining      ├── Parallelization               │
│  ├── Routing              ├── Planning (ReAct)              │
│  └── Tool Use             └── Orchestrator-Workers          │
│                                                              │
│  QUALITY (3)              MULTI-AGENT (3)                    │
│  ├── Reflection           ├── Consensus                     │
│  ├── Evaluator-Optimizer  ├── Debate                        │
│  └── Self-Improvement     └── Hierarchical                  │
│                                                              │
│  MEMORY (2)               SAFETY (3)                         │
│  ├── Memory Management    ├── Guardrails                    │
│  └── Context Injection    ├── Human-in-Loop                 │
│                           └── Fallback & Escalation         │
│                                                              │
│  LEARNING (3)                                                │
│  ├── Meta-Learning                                          │
│  ├── Dynamic Prompting                                      │
│  └── Feedback Loop                                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Reference

| # | Pattern | Use When | Template |
|---|---------|----------|----------|
| 1 | Prompt Chaining | Sequential steps needed | `prompt_chaining_template.py` |
| 2 | Routing | Task needs classification | `routing_template.py` |
| 3 | Tool Use | External APIs/tools needed | `tool_use_template.py` |
| 4 | Parallelization | Independent tasks | `parallelization_template.py` |
| 5 | Planning (ReAct) | Multi-step reasoning | `react_planning_template.py` |
| 6 | Orchestrator-Workers | Coordination needed | `orchestrator_template.py` |
| 7 | Reflection | Quality check before output | `reflection_template.py` |
| 8 | Evaluator-Optimizer | Parameter tuning | `evaluator_template.py` |
| 9 | Self-Improvement | Learn from results | `self_improvement_template.py` |
| 10 | Consensus | Multiple opinions needed | `consensus_template.py` |
| 11 | Debate | Adversarial analysis | `debate_template.py` |
| 12 | Hierarchical | Delegation needed | `hierarchical_template.py` |
| 13 | Memory Management | Persistent context | `memory_template.py` |
| 14 | Context Injection | Relevant history needed | `context_injection_template.py` |
| 15 | Guardrails | Output validation | `guardrails_template.py` |
| 16 | Human-in-Loop | User approval needed | `human_loop_template.py` |
| 17 | Fallback & Escalation | Error recovery | `fallback_template.py` |
| 18 | Meta-Learning | Strategy adaptation | `meta_learning_template.py` |
| 19 | Dynamic Prompting | Context-aware prompts | `dynamic_prompting_template.py` |
| 20 | Feedback Loop | Continuous improvement | `feedback_loop_template.py` |

---

## Most Important Pattern: ReAct

The **ReAct (Reasoning + Acting)** pattern was the primary pattern used for trading agents:

```
Thought: [Analyze what I know and what I need]
Action: [Specify API call or analysis]
Observation: [Note what I learned]
... (repeat as needed)
Final Answer: [Clear recommendation with confidence %]
```

### ReAct Example (Trading)

```
Thought: User wants XAUUSD signal. I need current price, trend, and sentiment.

Action: GET /predict/signal {"symbol": "XAUUSD"}
Observation: Signal is BUY with 75% confidence, EMA crossover bullish

Action: GET /sentiment/XAUUSD
Observation: Market sentiment is 65% bullish

Action: GET /market/blackout {"symbol": "XAUUSD"}
Observation: No news blackout, safe to trade

Final Answer: BUY XAUUSD
- Confidence: 75%
- Entry: Current price
- SL: 1.5 ATR below
- TP: 2.0 ATR above
- Rationale: EMA crossover + bullish sentiment + no blackout
```

---

## Pattern Implementation Template

Each pattern follows this structure:

```python
class PatternExecutor:
    """Base class for pattern execution."""

    def __init__(self, config: dict):
        self.config = config
        self.memory = {}

    def execute(self, input_data: dict) -> dict:
        """Execute the pattern."""
        raise NotImplementedError

    def validate(self, result: dict) -> bool:
        """Validate the result."""
        return True

    def fallback(self, error: Exception) -> dict:
        """Handle errors."""
        return {"success": False, "error": str(error)}
```

---

## API Endpoints

Each pattern has an execution endpoint:

| Endpoint | Pattern |
|----------|---------|
| `POST /agent/patterns/execute/parallelization` | Parallelization |
| `POST /agent/patterns/execute/reflection` | Reflection |
| `POST /agent/patterns/execute/consensus` | Consensus |
| `POST /agent/patterns/execute/debate` | Debate |
| `POST /agent/patterns/execute/meta-learning` | Meta-Learning |
| `POST /agent/patterns/execute/prompt-chaining` | Prompt Chaining |
| `POST /agent/patterns/execute/planning` | Planning (ReAct) |
| `POST /agent/patterns/execute/memory` | Memory |
| `POST /agent/patterns/execute/orchestrator` | Orchestrator |
| `POST /agent/patterns/execute/evaluator` | Evaluator |
| `POST /agent/patterns/execute/hierarchical` | Hierarchical |
| `POST /agent/patterns/execute/self-improvement` | Self-Improvement |
| `POST /agent/patterns/execute/fallback` | Fallback |

---

## Combining Patterns

Patterns work best when combined:

```
User Request
     │
     ▼
┌─────────────┐
│   Routing   │  ─── Classify task type
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Planning   │  ─── Create execution plan
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Tool Use    │  ─── Execute API calls
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Reflection  │  ─── Check quality
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Guardrails  │  ─── Validate output
└──────┬──────┘
       │
       ▼
   Response
```

---

## Usage in Trading Systems

The 20 agentic patterns are actively used in the Fokha Trading System:

### Pattern Executor Service

**File:** `python_ml/services/pattern_executor.py`

The `PatternExecutor` class provides full implementation of all 20 patterns with SQLite persistence for memory patterns and ThreadPoolExecutor for parallel execution.

### Trading System Integration

| Pattern | Trading Use Case | Implementation |
|---------|-----------------|----------------|
| **Consensus** | Multi-timeframe voting | 8-TF weighted signal aggregation |
| **Debate** | Bull vs Bear analysis | Opposing viewpoints before decision |
| **ReAct Planning** | Trade execution | Step-by-step signal → validation → execution |
| **Reflection** | Signal quality check | Confidence validation before notification |
| **Parallelization** | Batch signal scanning | 5 symbols × 3 strategies simultaneously |
| **Memory Management** | Context persistence | Trade history, agent state |
| **Guardrails** | Risk validation | Position size limits, exposure checks |
| **Fallback** | Error recovery | Retry logic with escalation |
| **Meta-Learning** | Strategy adaptation | Weekly performance-based tuning |
| **Orchestrator** | Multi-agent coordination | Master agent delegating to specialists |

### Example: Signal Generation Pipeline

```python
# Uses 5 patterns combined:
# 1. Parallelization - Scan all symbols
# 2. Consensus - Multi-timeframe voting
# 3. Reflection - Quality check
# 4. Guardrails - Risk validation
# 5. Memory - Store signal history

result = pattern_executor.execute_pipeline([
    ('parallelization', {'symbols': ['XAUUSD', 'US30', 'BTCUSD']}),
    ('consensus', {'timeframes': ['M15', 'H1', 'H4', 'D1']}),
    ('reflection', {'min_confidence': 0.70}),
    ('guardrails', {'max_exposure': 0.30}),
    ('memory', {'action': 'store'})
])
```

### N8N Integration

N8N workflows trigger agentic patterns via API:

| Workflow | Pattern Used |
|----------|-------------|
| `ml_signal_generator.json` | Consensus + Reflection |
| `model_health_monitor.json` | Guardrails + Fallback |
| `weekly_report.json` | Memory Management |
| `market_data_collector.json` | Parallelization |

### Flutter App Integration

The Flutter app uses agentic patterns through:

- `AgentConfigService` - Fetches pattern configurations
- `SuperAIProvider` - Multi-agent pipeline execution
- `TradingProvider` - ReAct pattern for trade execution

### API Endpoint Summary

**Base URL:** `http://localhost:5050/agent/patterns/execute/`

| Pattern | Endpoint | Status |
|---------|----------|--------|
| Parallelization | `/parallelization` | Active |
| Reflection | `/reflection` | Active |
| Consensus | `/consensus` | Active |
| Debate | `/debate` | Active |
| Meta-Learning | `/meta-learning` | Active |
| Prompt Chaining | `/prompt-chaining` | Active |
| Planning | `/planning` | Active |
| Memory | `/memory` | Active |
| Orchestrator | `/orchestrator` | Active |
| Evaluator | `/evaluator` | Active |
| Hierarchical | `/hierarchical` | Active |
| Self-Improvement | `/self-improvement` | Active |
| Fallback | `/fallback` | Active |
