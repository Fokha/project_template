# Skills Index - Extracted from Fokha Trading System

**Version:** 1.0
**Source Project:** Fokha Unified Trading System v2.3.7
**Last Updated:** January 2026

---

## Overview

This directory contains **reusable skill templates** extracted from the Fokha Trading System project. Each skill is a proven pattern that can be applied to new projects.

```
skills/
├── SKILLS_INDEX.md          # This file - Master reference
├── flutter/                 # Flutter/Dart patterns
├── python_api/              # Python Flask API patterns
├── machine_learning/        # ML pipeline patterns
├── mql5/                    # MetaTrader 5 patterns
├── devops/                  # Infrastructure patterns
├── n8n/                     # Workflow automation patterns
├── agentic/                 # AI agent design patterns
└── integration/             # Cross-system integration patterns
```

---

## Quick Reference Matrix

| Category | Skills | Files | Complexity | Used In Trading |
|----------|--------|-------|------------|-----------------|
| **Flutter** | 8 patterns | 8 templates | ⭐⭐⭐ | Yes (fokha_apps) |
| **Python API** | 10 patterns | 10 templates | ⭐⭐⭐ | Yes (api_server.py) |
| **Machine Learning** | 12 patterns | 12 templates | ⭐⭐⭐⭐ | Yes (ML models) |
| **MQL5** | 8 patterns | 10 templates | ⭐⭐⭐⭐ | Yes (Ultimate EA v19) |
| **DevOps** | 10 patterns | 10 templates | ⭐⭐⭐ | Yes (automation) |
| **N8N** | 10 patterns | 10 templates | ⭐⭐ | Yes (45 workflows) |
| **Agentic AI** | 21 patterns | 21 templates | ⭐⭐⭐⭐⭐ | Yes (PatternExecutor) |
| **Integration** | 8 patterns | 8 templates | ⭐⭐⭐⭐ | Yes (bridge) |

**Total: 87 skill patterns**

### Trading System Usage Summary

| Skill Category | Integration Point | Active Usage |
|----------------|-------------------|--------------|
| Flutter | fokha_apps (6 apps) | AgentConfigService, MLSignalService |
| Python API | localhost:5050 | 242+ endpoints, 577 tests |
| Machine Learning | SignalClassificationModel | 8-TF consensus voting |
| MQL5 | Ultimate System v19.0 | PropFirm profiles, 25 strategies |
| DevOps | Oracle Cloud + Local | Active-active failover |
| N8N | 45 workflows | Signal generation, monitoring |
| Agentic | PatternExecutor | 13 execution endpoints |
| Integration | WebSocket + REST | Real-time + batch processing |

---

## 1. Flutter Skills (`flutter/`)

### Patterns Extracted

| # | Pattern | Template | Description |
|---|---------|----------|-------------|
| 1 | **Provider Pattern** | `provider_template.dart` | State management with ChangeNotifier |
| 2 | **Service Pattern** | `service_template.dart` | Business logic encapsulation |
| 3 | **Model Pattern** | `model_template.dart` | Data model with JSON serialization |
| 4 | **API Client Pattern** | `api_client_template.dart` | HTTP client with error handling |
| 5 | **WebSocket Client** | `websocket_client_template.dart` | Real-time data streaming |
| 6 | **Widget Composition** | `widget_composition_template.dart` | Reusable widget patterns |
| 7 | **Theme Constants** | `theme_constants_template.dart` | Hardcoded fonts, colors, spacing |
| 8 | **Plugin Architecture** | `plugin_template.dart` | Extensible plugin system |

### Usage Example
```dart
// Copy template
cp skills/flutter/provider_template.dart lib/providers/my_provider.dart

// Customize
sed -i 's/{{PROVIDER_NAME}}/MyFeature/g' lib/providers/my_provider.dart
```

---

## 2. Python API Skills (`python_api/`)

### Patterns Extracted

| # | Pattern | Template | Description |
|---|---------|----------|-------------|
| 1 | **Flask Blueprint** | `blueprint_template.py` | Modular API organization |
| 2 | **Endpoint Pattern** | `endpoint_template.py` | Standard request/response |
| 3 | **Error Handler** | `error_handler_template.py` | Consistent error responses |
| 4 | **Database Operations** | `database_template.py` | SQLite CRUD operations |
| 5 | **Background Tasks** | `background_task_template.py` | Async task execution |
| 6 | **Caching Pattern** | `cache_template.py` | Request/response caching |
| 7 | **Validation Pattern** | `validation_template.py` | Input validation |
| 8 | **Logging Pattern** | `logging_template.py` | Structured logging |
| 9 | **Health Check** | `health_check_template.py` | Service health monitoring |
| 10 | **Deduplication** | `dedup_template.py` | Prevent duplicate operations |

### Standard Response Format
```python
# All endpoints return this structure
{
    "success": True,
    "data": {...},
    "error": None,
    "timestamp": "2026-01-11T10:00:00Z"
}
```

---

## 3. Machine Learning Skills (`machine_learning/`)

### Patterns Extracted

| # | Pattern | Template | Description |
|---|---------|----------|-------------|
| 1 | **Model Training** | `training_template.py` | Complete training pipeline |
| 2 | **Feature Engineering** | `feature_engineering_template.py` | Feature extraction patterns |
| 3 | **Model Serving** | `model_serving_template.py` | Prediction endpoint |
| 4 | **Ensemble Methods** | `ensemble_template.py` | XGBoost + LightGBM combo |
| 5 | **Walk-Forward Validation** | `walkforward_template.py` | Time-series validation |
| 6 | **Hyperparameter Tuning** | `hyperparameter_template.py` | Grid/Random search |
| 7 | **Model Persistence** | `persistence_template.py` | Save/load models |
| 8 | **Confidence Calibration** | `calibration_template.py` | Confidence scoring |
| 9 | **Multi-Timeframe** | `mtf_template.py` | Multi-timeframe analysis |
| 10 | **Sentiment Analysis** | `sentiment_template.py` | NLP for financial text |
| 11 | **Anomaly Detection** | `anomaly_template.py` | Isolation Forest pattern |
| 12 | **Scheduled Retraining** | `retrain_template.py` | Automated model updates |

### Model Accuracy Expectations
```
Asset Class → Expected Accuracy Range
├── Metals:    80-90%
├── Indices:   65-75%
├── Forex:     60-70%
└── Crypto:    50-65%
```

---

## 4. MQL5 Skills (`mql5/`)

### Patterns Extracted

| # | Pattern | Template | Description |
|---|---------|----------|-------------|
| 1 | **EA Structure** | `ea_template.mq5` | Complete EA skeleton |
| 2 | **Include Header** | `include_template.mqh` | Header file with guards |
| 3 | **Risk Management** | `risk_manager_template.mqh` | Position sizing, exposure |
| 4 | **Indicator Wrapper** | `indicator_template.mqh` | Indicator encapsulation |
| 5 | **Order Management** | `order_manager_template.mqh` | Trade execution |
| 6 | **API Bridge** | `api_bridge_template.mqh` | Python API communication |
| 7 | **Dashboard** | `dashboard_template.mqh` | Chart panel UI |
| 8 | **Notification Service** | `notification_template.mqh` | Telegram/Discord alerts |

### MQL5 Naming Conventions
```cpp
// Prefixes
m_    → Member variables
g_    → Global variables
s_    → Static variables
Inp   → Input parameters

// Classes
C[Name]    → CMyClass
I[Name]    → IMyInterface (rare in MQL5)
```

---

## 5. DevOps Skills (`devops/`)

### Patterns Extracted

| # | Pattern | Template | Description |
|---|---------|----------|-------------|
| 1 | **Docker Compose** | `docker-compose.template.yml` | Multi-service setup |
| 2 | **Dockerfile API** | `Dockerfile.api.template` | Python API container |
| 3 | **Nginx Config** | `nginx.template.conf` | Reverse proxy |
| 4 | **Backup Script** | `backup_template.sh` | Automated backups |
| 5 | **Sync Script** | `sync_template.sh` | Local-cloud sync |
| 6 | **Health Monitor** | `health_monitor_template.py` | Service watchdog |
| 7 | **LaunchAgent** | `launchagent_template.plist` | macOS scheduling |
| 8 | **Cron Setup** | `cron_template.sh` | Linux scheduling |
| 9 | **Deploy Script** | `deploy_template.sh` | Deployment automation |
| 10 | **Failover Script** | `failover_template.sh` | Active-active failover |

### 3-Site Architecture Pattern
```
[Primary] ←─sync─→ [Portable] ←─deploy─→ [Secondary]
   Mac                SD Card              Windows/Cloud
```

---

## 6. N8N Skills (`n8n/`)

### Patterns Extracted

| # | Pattern | Template | Description |
|---|---------|----------|-------------|
| 1 | **API Poller** | `api_poller.json` | Scheduled API polling |
| 2 | **Cron Workflow** | `cron_workflow.json` | Time-based triggers |
| 3 | **Webhook Handler** | `webhook_handler.json` | Incoming webhooks |
| 4 | **Notification Hub** | `notification_hub.json` | Multi-channel alerts |
| 5 | **Data Pipeline** | `data_pipeline.json` | ETL workflow |
| 6 | **Error Handler** | `error_handler.json` | Error recovery flow |
| 7 | **ML Signal Generator** | `ml_signal_generator.json` | ML predictions → Telegram |
| 8 | **Market Data Collector** | `market_data_collector.json` | Multi-symbol data fetch |
| 9 | **Model Health Monitor** | `model_health_monitor.json` | ML model health alerts |
| 10 | **Weekly Report** | `weekly_report.json` | Performance summary |

### Trading System Integration

These workflows are actively used in the Fokha Trading System (45 production workflows):

| Workflow Type | Production Count | Purpose |
|---------------|-----------------|---------|
| Signal Generation | 8 | ML predictions, telegram alerts |
| Data Collection | 6 | Market data, sentiment |
| Monitoring | 10 | Health, performance, alerts |
| Reporting | 5 | Daily/weekly reports |
| Training | 4 | Model retraining pipelines |
| Other | 12 | Misc automation |

### N8N Workflow Naming
```
fokha_{category}_{action}_v{version}.json

Examples:
fokha_ml_predictions_v2.json
fokha_notification_trade_v1.json
fokha_batch_optimization_v1.json
```

---

## 7. Agentic AI Skills (`agentic/`)

### Hierarchical Agent Architecture (v2.0)

The recommended pattern for complex multi-agent systems:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    HIERARCHICAL AGENT ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   LAYER 1: USER INTERFACE                                               │
│   └── THE_ASSISTANT (Supervisor) - All user interactions                │
│                                                                          │
│   LAYER 2: STRATEGIC                                                    │
│   └── THE_MASTER (Architect) - Architecture & planning                  │
│                                                                          │
│   LAYER 3: IMPLEMENTATION                                               │
│   └── Specialists: BACKEND, FRONTEND, DEVOPS, AUTOMATION, etc.          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Benefits:**
- Clear chain of command
- Separation of concerns
- Scalable specialist model
- Consistent user experience

**Templates:**
- `agents/prompts/THE_ASSISTANT.md` - Supervisor template
- `agents/prompts/THE_MASTER.md` - Architect template
- `agents/prompts/SPECIALIST_AGENT_TEMPLATE.md` - Generic specialist

### 21 Agentic Patterns Extracted

| # | Category | Pattern | Template |
|---|----------|---------|----------|
| **Architecture** |||
| 0 | Architecture | Hierarchical Agent System | `hierarchical_agent_system_template.md` |
| **Core** |||
| 1 | Core | Prompt Chaining | `prompt_chaining_template.py` |
| 2 | Core | Routing | `routing_template.py` |
| 3 | Core | Tool Use | `tool_use_template.py` |
| **Execution** |||
| 4 | Execution | Parallelization | `parallelization_template.py` |
| 5 | Execution | Planning (ReAct) | `react_planning_template.py` |
| 6 | Execution | Orchestrator-Workers | `orchestrator_template.py` |
| **Quality** |||
| 7 | Quality | Reflection | `reflection_template.py` |
| 8 | Quality | Evaluator-Optimizer | `evaluator_template.py` |
| 9 | Quality | Self-Improvement | `self_improvement_template.py` |
| **Multi-Agent** |||
| 10 | Multi-Agent | Consensus | `consensus_template.py` |
| 11 | Multi-Agent | Debate | `debate_template.py` |
| 12 | Multi-Agent | Hierarchical | `hierarchical_template.py` |
| **Memory** |||
| 13 | Memory | Memory Management | `memory_template.py` |
| 14 | Memory | Context Injection | `context_injection_template.py` |
| **Safety** |||
| 15 | Safety | Guardrails | `guardrails_template.py` |
| 16 | Safety | Human-in-Loop | `human_loop_template.py` |
| 17 | Safety | Fallback & Escalation | `fallback_template.py` |
| **Learning** |||
| 18 | Learning | Meta-Learning | `meta_learning_template.py` |
| 19 | Learning | Dynamic Prompting | `dynamic_prompting_template.py` |
| 20 | Learning | Feedback Loop | `feedback_loop_template.py` |

### ReAct Pattern (Most Used)
```
Thought: [Analyze what I know and what I need]
Action: [Specify API call or analysis]
Observation: [Note what I learned]
... (repeat as needed)
Final Answer: [Clear recommendation with confidence %]
```

### Trading System Integration

All 21 patterns are implemented in `services/pattern_executor.py` with 13 API endpoints:

| Pattern | Trading Use Case | API Endpoint |
|---------|-----------------|--------------|
| Consensus | Multi-timeframe voting | `/agent/patterns/execute/consensus` |
| Debate | Bull vs Bear analysis | `/agent/patterns/execute/debate` |
| Parallelization | Batch signal scanning | `/agent/patterns/execute/parallelization` |
| Reflection | Signal quality check | `/agent/patterns/execute/reflection` |
| Memory | Trade history persistence | `/agent/patterns/execute/memory` |
| Guardrails | Risk validation | (internal) |
| Meta-Learning | Strategy adaptation | `/agent/patterns/execute/meta-learning` |

**Active in Production:**
- PatternExecutor class with SQLite persistence
- ThreadPoolExecutor for parallel execution
- N8N workflows trigger patterns via API
- Flutter app uses AgentConfigService

---

## 8. Integration Skills (`integration/`)

### Patterns Extracted

| # | Pattern | Template | Description |
|---|---------|----------|-------------|
| 1 | **REST API Design** | `rest_api_template.md` | API design guidelines |
| 2 | **WebSocket Server** | `websocket_server_template.py` | Real-time server |
| 3 | **WebSocket Client** | `websocket_client_template.dart` | Real-time client |
| 4 | **File Bridge** | `file_bridge_template.py` | Cross-platform file sync |
| 5 | **Signal Queue** | `signal_queue_template.py` | Message queue pattern |
| 6 | **Health Check** | `health_check_template.py` | Cross-service health |
| 7 | **Deduplication** | `dedup_cache_template.py` | Prevent duplicates |
| 8 | **API Versioning** | `api_versioning_template.md` | Version management |

### Integration Data Flow
```
Source → API (5050) → DB → Consumers
                    ↓
             WebSocket (8765) → Real-time clients
```

---

## How to Use Skills

### Method 1: Copy and Customize

```bash
# 1. Navigate to skills directory
cd project_template/skills/

# 2. Copy the template you need
cp flutter/provider_template.dart ~/my_project/lib/providers/my_provider.dart

# 3. Replace placeholders
sed -i 's/{{FEATURE_NAME}}/MyFeature/g' ~/my_project/lib/providers/my_provider.dart
```

### Method 2: Use init_project.sh

```bash
# The init script can copy selected skill templates
./scripts/init_project.sh "My Project" --skills flutter,python_api,devops
```

### Method 3: Reference Only

Some skills are reference documentation (`.md` files) that guide implementation without code templates.

---

## Skill Dependencies

Some skills work together:

```
┌─────────────────────────────────────────────────────────────┐
│                    SKILL DEPENDENCIES                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Flutter Provider ────────► Flutter API Client               │
│         │                          │                         │
│         └──────────────────────────┼───► Python API          │
│                                    │                         │
│  Python API ──────────────────────►│                         │
│         │                          │                         │
│         └──► ML Training ──► Model Serving                   │
│                                    │                         │
│  MQL5 EA ─────► API Bridge ────────┘                         │
│         │                                                    │
│         └──► Risk Manager ──► Order Manager                  │
│                                                              │
│  DevOps Docker ──► Health Monitor ──► Failover               │
│                                                              │
│  N8N Workflows ──► Notification Hub ──► Telegram             │
│                                                              │
│  Agentic Patterns:                                           │
│    ReAct Planning ──► Tool Use ──► Reflection                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Placeholder Conventions

All templates use these placeholder patterns:

| Placeholder | Meaning |
|-------------|---------|
| `{{PROJECT_NAME}}` | Your project name |
| `{{FEATURE_NAME}}` | Feature/module name |
| `{{AGENT_NAME}}` | Agent identifier |
| `{{API_URL}}` | API base URL |
| `{{DB_PATH}}` | Database file path |
| `{{PORT}}` | Service port number |
| `{{VERSION}}` | Version string |

---

## Adding New Skills

When you discover a new reusable pattern:

1. **Document it** in the appropriate category README
2. **Create template** with placeholders
3. **Add to this index** with description
4. **Test** by using it in a new project
5. **Refine** based on usage feedback

---

## Contributing

To suggest new skills or improvements:

1. Create the template in the appropriate directory
2. Add entry to this index
3. Test in a real project
4. Submit for review

---

*Skills extracted from Fokha Trading System (v2.3.7 Flutter, v4.3.21 Python, v19.0.37 MQL5)*
