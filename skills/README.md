# Skills Templates Library

**Reusable patterns extracted from the Fokha Unified Trading System**

Version: 1.1 | Templates: 74 | Categories: 8

---

## Overview

This library contains **production-tested skill templates** extracted from the Fokha Trading System. Each template is a proven pattern that can be copied and customized for new projects.

```
skills/
├── README.md              # This file
├── SKILLS_INDEX.md        # Detailed pattern documentation
├── python_api/      (10)  # Flask API patterns
├── flutter/         (8)   # Flutter/Dart patterns
├── mql5/            (8)   # MetaTrader 5 patterns
├── n8n/             (6)   # N8N workflow patterns
├── agentic/         (20)  # AI agent design patterns
├── devops/          (10)  # Infrastructure patterns
├── integration/     (8)   # Cross-system patterns
└── machine_learning/ (12) # ML pipeline patterns
```

---

## Quick Start

### Copy a Template

```bash
# Example: Add a new Flask API endpoint
cp skills/python_api/endpoint_template.py ~/my_project/api/users.py

# Replace placeholders
sed -i '' 's/{{FEATURE_NAME}}/users/g' ~/my_project/api/users.py
```

### Browse Available Templates

```bash
# List all templates
find skills -name "*.py" -o -name "*.dart" -o -name "*.mq5" -o -name "*.json" | head -20

# View template with placeholders
head -50 skills/agentic/orchestrator_template.py
```

---

## Template Categories

| Category | Templates | Language | Complexity |
|----------|-----------|----------|------------|
| **Python API** | 10 | Python | Medium |
| **Flutter** | 8 | Dart | Medium |
| **MQL5** | 8 | MQL5/C++ | High |
| **N8N Workflows** | 6 | JSON | Low |
| **Agentic AI** | 20 | Python | Very High |
| **DevOps** | 10 | Bash/YAML | Medium |
| **Integration** | 8 | Python | High |
| **Machine Learning** | 12 | Python | High |

---

## Category Details

### Python API (`python_api/`)
Flask-based API patterns for building REST services.

| Template | Purpose |
|----------|---------|
| `blueprint_template.py` | Modular API organization |
| `endpoint_template.py` | Standard request/response |
| `error_handler_template.py` | Consistent error responses |
| `database_template.py` | SQLite CRUD operations |
| `background_task_template.py` | Async task execution |
| `cache_template.py` | Response caching |
| `validation_template.py` | Input validation |
| `logging_template.py` | Structured logging |
| `health_check_template.py` | Service monitoring |
| `dedup_template.py` | Prevent duplicate operations |

### Flutter (`flutter/`)
Dart patterns for Flutter mobile/desktop apps.

| Template | Purpose |
|----------|---------|
| `provider_template.dart` | State management |
| `service_template.dart` | Business logic |
| `model_template.dart` | JSON serialization |
| `api_client_template.dart` | HTTP client |
| `websocket_client_template.dart` | Real-time streaming |
| `widget_composition_template.dart` | Reusable widgets |
| `theme_constants_template.dart` | Theming system |
| `plugin_template.dart` | Plugin architecture |

### Agentic AI (`agentic/`)
20 AI agent design patterns for building intelligent systems.

**Core Patterns:**
- `prompt_chaining_template.py` - Sequential prompt pipelines
- `routing_template.py` - Intent-based routing
- `tool_use_template.py` - Function calling patterns

**Execution Patterns:**
- `parallelization_template.py` - Parallel task execution
- `react_planning_template.py` - ReAct planning loops
- `orchestrator_template.py` - Worker coordination

**Quality Patterns:**
- `reflection_template.py` - Self-critique
- `evaluator_template.py` - Output optimization
- `self_improvement_template.py` - Performance tuning

**Multi-Agent Patterns:**
- `consensus_template.py` - Multi-agent voting
- `debate_template.py` - Adversarial reasoning
- `hierarchical_template.py` - Agent delegation

**Memory Patterns:**
- `memory_management_template.py` - Context persistence
- `context_injection_template.py` - Dynamic prompting

**Safety Patterns:**
- `guardrails_template.py` - Output validation
- `human_loop_template.py` - Human approval
- `fallback_template.py` - Error recovery

**Learning Patterns:**
- `meta_learning_template.py` - Strategy adaptation
- `dynamic_prompting_template.py` - Prompt optimization
- `feedback_loop_template.py` - Continuous improvement

### Machine Learning (`machine_learning/`)
ML pipeline patterns for training and serving models.

| Template | Purpose |
|----------|---------|
| `training_template.py` | Complete training pipeline |
| `feature_engineering_template.py` | Feature extraction |
| `model_serving_template.py` | Prediction endpoint |
| `ensemble_template.py` | XGBoost + LightGBM |
| `walkforward_template.py` | Time-series validation |
| `hyperparameter_template.py` | Grid/Random search |
| `persistence_template.py` | Save/load models |
| `calibration_template.py` | Confidence scoring |
| `mtf_template.py` | Multi-timeframe analysis |
| `sentiment_template.py` | NLP for text |
| `anomaly_template.py` | Isolation Forest |
| `retrain_template.py` | Scheduled retraining |

### MQL5 (`mql5/`)
MetaTrader 5 Expert Advisor patterns.

| Template | Purpose |
|----------|---------|
| `ea_template.mq5` | Complete EA skeleton |
| (+ 7 more) | Risk, orders, API bridge, dashboard |

### N8N Workflows (`n8n/`)
Workflow automation patterns.

| Template | Purpose |
|----------|---------|
| `webhook_handler.json` | Incoming webhook |
| `notification_hub.json` | Multi-channel alerts |
| `api_poller.json` | Scheduled API calls |
| `error_handler.json` | Error recovery |
| `data_pipeline.json` | ETL workflow |
| `cron_workflow.json` | Scheduled jobs |

### DevOps (`devops/`)
Infrastructure and deployment patterns.

| Template | Purpose |
|----------|---------|
| `docker_template.py` | Container setup |
| `deployment_template.py` | Deploy automation |
| `backup_template.py` | Backup scripts |
| `monitoring_template.py` | Health monitoring |
| `ci_cd_template.py` | CI/CD pipelines |
| `secrets_template.py` | Secrets management |
| `logging_infra_template.py` | Log aggregation |
| `service_mesh_template.py` | Service discovery |

### Integration (`integration/`)
Cross-system communication patterns.

| Template | Purpose |
|----------|---------|
| `websocket_server.py` | Real-time server |
| `api_client_template.py` | HTTP client |
| `mt5_bridge_template.py` | MT5 communication |
| `telegram_bot_template.py` | Telegram integration |
| `webhook_handler_template.py` | Webhook receiver |
| `notification_template.py` | Multi-channel notify |
| `data_sync_template.py` | Data synchronization |
| `dedup_cache.py` | Deduplication cache |

---

## Placeholder Conventions

All templates use these placeholders:

| Placeholder | Meaning | Example |
|-------------|---------|---------|
| `{{PROJECT_NAME}}` | Project name | `my_trading_bot` |
| `{{FEATURE_NAME}}` | Feature/module | `signals` |
| `{{AGENT_NAME}}` | Agent identifier | `market_analyzer` |
| `{{API_URL}}` | API base URL | `http://localhost:5050` |
| `{{DB_PATH}}` | Database path | `data/trading.db` |
| `{{PORT}}` | Service port | `5050` |
| `{{VERSION}}` | Version string | `1.0.0` |
| `{{MAX_WORKERS}}` | Worker count | `4` |

---

## Usage Examples

### Example 1: Add Caching to Flask API

```bash
# 1. Copy template
cp skills/python_api/cache_template.py ~/my_api/utils/cache.py

# 2. Replace placeholders
sed -i '' 's/{{CACHE_TTL}}/300/g' ~/my_api/utils/cache.py

# 3. Import and use
# from utils.cache import cached_response
```

### Example 2: Add ReAct Agent Pattern

```bash
# 1. Copy template
cp skills/agentic/react_planning_template.py ~/my_agent/patterns/react.py

# 2. Customize for your use case
# Edit the tool definitions and prompt templates
```

### Example 3: Add Flutter State Management

```bash
# 1. Copy template
cp skills/flutter/provider_template.dart ~/my_app/lib/providers/settings_provider.dart

# 2. Replace placeholders
sed -i '' 's/{{PROVIDER_NAME}}/Settings/g' ~/my_app/lib/providers/settings_provider.dart
```

---

## Best Practices

1. **Read the template header** - Each template has a docstring explaining when to use it
2. **Replace ALL placeholders** - Use `grep '{{' template.py` to find them
3. **Customize, don't copy blindly** - Templates are starting points, adapt to your needs
4. **Keep templates DRY** - If you improve a pattern, update the template

---

## Template Dependencies

Some templates work together:

```
Python API Stack:
  blueprint_template.py
    └── endpoint_template.py
          └── validation_template.py
          └── error_handler_template.py
          └── cache_template.py

Agentic Stack:
  orchestrator_template.py
    └── routing_template.py
    └── tool_use_template.py
    └── reflection_template.py

ML Pipeline Stack:
  training_template.py
    └── feature_engineering_template.py
    └── walkforward_template.py
    └── persistence_template.py
          └── model_serving_template.py
```

---

## Adding New Templates

1. Create template in appropriate category directory
2. Add header with purpose, placeholders, and usage
3. Use `{{PLACEHOLDER}}` syntax for customization points
4. Update this README and SKILLS_INDEX.md
5. Test by using in a real project

---

## Source Project

Templates extracted from:
- **Flutter App**: v2.3.7 (AI Studio Pro)
- **Python ML**: v4.3.22 (US_PY Engine)
- **MQL5 EA**: v19.0.37 (Ultimate System)
- **N8N**: 45 workflows

---

## More Information

See [SKILLS_INDEX.md](./SKILLS_INDEX.md) for:
- Detailed pattern descriptions
- Complete placeholder reference
- Skill dependency diagrams
- Category-specific documentation
