# Project Template - Complete Documentation

> **Purpose:** Reusable project scaffolding and skill templates extracted from production systems. Jump-start new projects with battle-tested patterns.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Market Analysis](#2-market-analysis)
3. [Product Overview](#3-product-overview)
4. [Technical Architecture](#4-technical-architecture)
5. [Features & Screenshots](#5-features--screenshots)
6. [API Reference](#6-api-reference)
7. [Installation Guide](#7-installation-guide)
8. [User Guide](#8-user-guide)
9. [Developer Guide](#9-developer-guide)
10. [Deployment](#10-deployment)
11. [Security](#11-security)
12. [Performance](#12-performance)
13. [Roadmap](#13-roadmap)
14. [Support](#14-support)

---

## 1. Executive Summary

### 1.1 Project Overview

| Field | Value |
|-------|-------|
| **Project Name** | Fokha Project Template |
| **Version** | 1.0.0 |
| **Status** | Production |
| **Last Updated** | January 2026 |
| **Repository** | Local (project_template/) |
| **License** | Proprietary |

### 1.2 Quick Description

> A comprehensive collection of 82+ reusable skill templates extracted from production trading systems. The Project Template provides battle-tested patterns for Flutter apps, Python APIs, ML pipelines, MQL5 Expert Advisors, DevOps automation, N8N workflows, and AI agent architectures. It enables rapid project bootstrapping with proven code patterns, reducing development time from weeks to days.

### 1.3 Key Metrics

| Metric | Value |
|--------|-------|
| Total Skill Patterns | 82+ |
| Template Categories | 8 |
| Flutter Templates | 9 |
| Python API Templates | 10 |
| ML Templates | 12 |
| MQL5 Templates | 8 |
| DevOps Templates | 10 |
| N8N Workflow Templates | 6 |
| Agentic AI Templates | 20 |
| Integration Templates | 8 |

---

## 2. Market Analysis

### 2.1 Industry Overview

**Market Size:**
- Global Software Development Tools market: $15.7B (2025)
- Expected CAGR: 11.3% (2025-2030)
- Target segment: Developer productivity tools - $4.2B

**Key Trends:**
1. AI-assisted development requiring structured templates
2. Cross-platform development demanding reusable patterns
3. MLOps adoption driving standardized ML pipelines
4. Algorithmic trading growth requiring proven EA patterns

### 2.2 Competitive Landscape

| Competitor | Strengths | Weaknesses | Our Advantage |
|------------|-----------|------------|---------------|
| Create React App | Easy setup | React only | Multi-platform |
| Cookiecutter | Flexible | Generic templates | Domain-specific patterns |
| Yeoman | Large ecosystem | Outdated patterns | Modern, production-tested |

### 2.3 Target Audience

**Primary Users:**
- **Solo Developers:** Building trading systems, ML apps, or cross-platform mobile apps who need proven patterns
- **Small Teams:** Starting new projects who want to avoid reinventing infrastructure

**User Pain Points:**
1. Spending weeks setting up project structure
2. Rebuilding the same patterns across projects
3. No reference for best practices in niche domains (trading, ML)

**How We Solve Them:**
1. 5-minute project setup with init script
2. 82+ ready-to-copy templates
3. Patterns extracted from production systems with proven accuracy

### 2.4 Value Proposition

```
┌─────────────────────────────────────────────────────────────┐
│                    VALUE PROPOSITION                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  FOR: Developers building trading, ML, or mobile apps       │
│  WHO: Need to start projects quickly with proven patterns   │
│  OUR PRODUCT IS: A comprehensive project template library   │
│  THAT: Provides 82+ battle-tested, production-ready skills  │
│  UNLIKE: Generic scaffolding tools                          │
│  WE: Include domain-specific patterns for trading + ML      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Product Overview

### 3.1 System Components

```
┌─────────────────────────────────────────────────────────────┐
│                PROJECT TEMPLATE ARCHITECTURE                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│   │   Scripts    │───▶│   Skills     │───▶│    Docs      │  │
│   │  (Init/Dev)  │    │  (82+ files) │    │  (Guides)    │  │
│   └──────────────┘    └──────────────┘    └──────────────┘  │
│          │                   │                   │          │
│          ▼                   ▼                   ▼          │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│   │    Agents    │    │ Infrastructure│    │  Knowledge   │  │
│   │  (Prompts)   │    │   (Docker)    │    │    Base      │  │
│   └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Skill Categories

| Category | Templates | Source Project | Complexity |
|----------|-----------|----------------|------------|
| Flutter | 9 patterns | AI Studio Pro v2.3.7 | ⭐⭐⭐ |
| Python API | 10 patterns | US_PY Engine v4.3.21 | ⭐⭐⭐ |
| Machine Learning | 12 patterns | US_PY Engine v4.3.21 | ⭐⭐⭐⭐ |
| MQL5 | 8 patterns | Ultimate System v19.0.37 | ⭐⭐⭐⭐ |
| DevOps | 10 patterns | All Projects | ⭐⭐⭐ |
| N8N | 6 patterns | 45 Production Workflows | ⭐⭐ |
| Agentic AI | 20 patterns | Dynamic Agent System v2.3 | ⭐⭐⭐⭐⭐ |
| Integration | 8 patterns | Cross-System Bridge | ⭐⭐⭐⭐ |

### 3.3 Key Features Matrix

| Feature | Status | Category | Description |
|---------|--------|----------|-------------|
| OAuth Template | ✅ Live | Flutter | Google/Apple/Microsoft/Email auth |
| Provider Pattern | ✅ Live | Flutter | State management with ChangeNotifier |
| Blueprint Template | ✅ Live | Python | Modular Flask API organization |
| Ensemble Template | ✅ Live | ML | XGBoost + LightGBM combo |
| EA Template | ✅ Live | MQL5 | Complete Expert Advisor skeleton |
| ReAct Pattern | ✅ Live | Agentic | Thought-Action-Observation loop |
| Docker Compose | ✅ Live | DevOps | Multi-service container setup |
| Notification Hub | ✅ Live | N8N | Multi-channel alerts workflow |

---

## 4. Technical Architecture

### 4.1 Directory Structure

```
project_template/
├── SETUP.md                    # Quick start guide
├── scripts/                    # Automation scripts
│   ├── init_project.sh         # Project initialization
│   ├── dev-start.sh            # Start development
│   ├── dev-stop.sh             # Stop development
│   └── update_skills.sh        # Sync latest skills
│
├── skills/                     # 82+ Skill Templates
│   ├── SKILLS_INDEX.md         # Master reference
│   ├── flutter/                # 9 Dart templates
│   ├── python_api/             # 10 Python templates
│   ├── machine_learning/       # 12 ML templates
│   ├── mql5/                   # 8 MQL5 templates
│   ├── devops/                 # 10 DevOps templates
│   ├── n8n/                    # 6 N8N workflows
│   ├── agentic/                # 20 AI agent patterns
│   └── integration/            # 8 integration templates
│
├── agents/                     # AI Agent System
│   ├── AGENT_SYSTEM.md         # Agent documentation
│   ├── prompts/                # Prompt templates
│   └── README.md
│
├── infrastructure/             # DevOps Config
│   └── docker-compose.yml      # Container orchestration
│
├── knowledge_base/             # KB Schema
│   ├── schema.sql              # SQLite schema
│   └── migrations/             # Schema migrations
│
├── api/                        # API Server Template
│   └── utils/kb_api.py         # KB API utilities
│
├── app/                        # Flutter App Template
│   └── lib/theme/              # Theme constants
│
└── docs/                       # Documentation
    ├── FULL_PROJECT_DOCUMENTATION.md
    ├── AGENT_KNOWLEDGE_BASE_SETUP.md
    └── PROJECT_TEMPLATE_DOCUMENTATION.md
```

### 4.2 Skill Dependencies

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

### 4.3 Placeholder System

All templates use standardized placeholders:

| Placeholder | Meaning | Example |
|-------------|---------|---------|
| `{{PROJECT_NAME}}` | Your project name | "My Trading App" |
| `{{FEATURE_NAME}}` | Feature/module name | "Authentication" |
| `{{AGENT_NAME}}` | Agent identifier | "trader_agent" |
| `{{API_URL}}` | API base URL | "http://localhost:5050" |
| `{{DB_PATH}}` | Database file path | "data/app.db" |
| `{{PORT}}` | Service port number | "5050" |
| `{{VERSION}}` | Version string | "1.0.0" |
| `{{WS_URL}}` | WebSocket URL | "ws://localhost:8765" |

---

## 5. Features & Screenshots

### 5.1 Feature: Flutter Templates (9 patterns)

**Description:** Production-tested Flutter/Dart patterns for building cross-platform mobile apps.

**Templates:**

| Template | Purpose | Lines |
|----------|---------|-------|
| `provider_template.dart` | State management with ChangeNotifier | ~150 |
| `service_template.dart` | Business logic encapsulation | ~200 |
| `model_template.dart` | Data models with JSON serialization | ~100 |
| `api_client_template.dart` | HTTP client with error handling | ~250 |
| `websocket_client_template.dart` | Real-time data streaming | ~180 |
| `widget_composition_template.dart` | Reusable widget patterns | ~120 |
| `theme_constants_template.dart` | Hardcoded fonts, colors, spacing | ~200 |
| `plugin_template.dart` | Extensible plugin system | ~220 |
| `oauth_template.dart` | Google/Apple/Microsoft/Email auth | ~700 |

**Architecture Pattern:**

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUTTER ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Widgets (UI) ──uses──► Providers (State)                   │
│        │                       │                             │
│        │                       ▼                             │
│        │               Services (Logic)                      │
│        │                       │                             │
│        │                       ▼                             │
│        │                Models (Data)                        │
│        │                       │                             │
│        └───────────────────────┼───► API Client              │
│                                │                             │
│                                ▼                             │
│                         External APIs                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

### 5.2 Feature: Python API Templates (10 patterns)

**Description:** Flask API patterns for building robust backend services.

**Templates:**

| Template | Purpose | Key Feature |
|----------|---------|-------------|
| `blueprint_template.py` | Modular API organization | Route separation |
| `endpoint_template.py` | Standard request/response | Validation |
| `error_handler_template.py` | Consistent error responses | Error codes |
| `database_template.py` | SQLite CRUD operations | Connection pooling |
| `background_task_template.py` | Async task execution | ThreadPool |
| `cache_template.py` | Request/response caching | TTL support |
| `validation_template.py` | Input validation | Schema validation |
| `logging_template.py` | Structured logging | Log rotation |
| `health_check_template.py` | Service health monitoring | Multiple checks |
| `dedup_template.py` | Prevent duplicate operations | TTL cache |

**Standard Response Format:**

```python
{
    "success": True,
    "data": {...},
    "error": None,
    "timestamp": "2026-01-12T10:00:00Z"
}
```

---

### 5.3 Feature: Machine Learning Templates (12 patterns)

**Description:** Complete ML pipeline patterns from data to deployment.

**Templates:**

| Template | Purpose | Algorithm |
|----------|---------|-----------|
| `training_template.py` | Complete training pipeline | sklearn |
| `feature_engineering_template.py` | Feature extraction | pandas |
| `model_serving_template.py` | Prediction endpoint | Flask |
| `ensemble_template.py` | XGBoost + LightGBM | Ensemble |
| `walkforward_template.py` | Time-series validation | Rolling window |
| `hyperparameter_template.py` | Grid/Random search | Optuna |
| `persistence_template.py` | Save/load models | joblib |
| `calibration_template.py` | Confidence scoring | Isotonic |
| `mtf_template.py` | Multi-timeframe analysis | Weighted voting |
| `sentiment_template.py` | NLP for financial text | FinBERT |
| `anomaly_template.py` | Outlier detection | Isolation Forest |
| `retrain_template.py` | Automated model updates | Scheduler |

**Expected Accuracy by Domain:**

```
Asset Class → Expected Accuracy Range
├── Metals:    80-90%
├── Indices:   65-75%
├── Forex:     60-70%
└── Crypto:    50-65%
```

---

### 5.4 Feature: MQL5 Templates (8 patterns)

**Description:** MetaTrader 5 Expert Advisor patterns for algorithmic trading.

**Templates:**

| Template | Purpose | Integration |
|----------|---------|-------------|
| `ea_template.mq5` | Complete EA skeleton | Entry point |
| `risk_manager.mqh` | Position sizing, exposure | Money management |
| `indicator_wrapper.mqh` | Indicator encapsulation | Technical analysis |
| `trade_manager.mqh` | Trade execution | Order handling |
| `strategy_base.mqh` | Strategy interface | Strategy pattern |
| `session_filter.mqh` | Trading session filter | Time-based |
| `news_filter.mqh` | News event blackout | Calendar |
| `python_bridge.mqh` | Python API communication | HTTP requests |

**MQL5 Naming Conventions:**

```cpp
// Prefixes
m_    → Member variables
g_    → Global variables
s_    → Static variables
Inp   → Input parameters

// Classes
C[Name]    → CMyClass
```

---

### 5.5 Feature: Agentic AI Templates (20 patterns)

**Description:** All 20 agentic design patterns for building AI agent systems.

**Pattern Categories:**

| Category | Patterns | Description |
|----------|----------|-------------|
| **Core** | Prompt Chaining, Routing, Tool Use | Foundation patterns |
| **Execution** | Parallelization, Planning (ReAct), Orchestrator-Workers | Task execution |
| **Quality** | Reflection, Evaluator-Optimizer, Self-Improvement | Quality assurance |
| **Multi-Agent** | Consensus, Debate, Hierarchical | Multi-agent coordination |
| **Memory** | Memory Management, Context Injection | State management |
| **Safety** | Guardrails, Human-in-Loop, Fallback & Escalation | Safety measures |
| **Learning** | Meta-Learning, Dynamic Prompting, Feedback Loop | Adaptation |

**ReAct Pattern (Most Used):**

```
Thought: [Analyze what I know and what I need]
Action: [Specify API call or analysis]
Observation: [Note what I learned]
... (repeat as needed)
Final Answer: [Clear recommendation with confidence %]
```

---

### 5.6 Feature: OAuth Authentication Template

**Supported Providers:**

| Provider | Status | Platforms |
|----------|--------|-----------|
| Google | ✅ | iOS, Android, Web, macOS |
| Apple | ✅ | iOS, Android, Web, macOS |
| Microsoft | ✅ | All |
| Email/Password | ✅ | All |

**Login Flow:**

```
┌─────────────────────────────────────┐
│         Welcome Back                 │
│                                      │
│  ┌─────────────────────────────────┐ │
│  │  🔵 Continue with Google        │ │
│  └─────────────────────────────────┘ │
│  ┌─────────────────────────────────┐ │
│  │  ⚫ Continue with Apple         │ │
│  └─────────────────────────────────┘ │
│  ┌─────────────────────────────────┐ │
│  │  🔷 Continue with Microsoft     │ │
│  └─────────────────────────────────┘ │
│                                      │
│  ─────────── or ───────────         │
│                                      │
│  Email:    [________________]        │
│  Password: [________________]        │
│                                      │
│  ┌─────────────────────────────────┐ │
│  │         Sign In                 │ │
│  └─────────────────────────────────┘ │
│                                      │
│     Don't have an account? Sign Up   │
└─────────────────────────────────────┘
```

---

## 6. API Reference

### 6.1 KB API Endpoints (Template)

The template includes a Knowledge Base API for project documentation storage.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/kb/projects` | List all projects |
| GET | `/kb/projects/:id` | Get project details |
| POST | `/kb/projects` | Create project |
| GET | `/kb/tasks` | List all tasks |
| POST | `/kb/tasks` | Create task |
| PUT | `/kb/tasks/:id` | Update task |
| GET | `/kb/research` | Search research |
| POST | `/kb/research` | Add research entry |

### 6.2 Health Check Endpoint

```python
# health_check_template.py

@app.route('/health')
def health():
    return {
        "success": True,
        "status": "healthy",
        "checks": {
            "api": True,
            "database": True,
            "models": True
        },
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }
```

### 6.3 Standard Error Response

```python
{
    "success": False,
    "data": None,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid input",
        "details": ["field 'email' is required"]
    },
    "timestamp": "2026-01-12T10:00:00Z"
}
```

---

## 7. Installation Guide

### 7.1 Prerequisites

| Requirement | Version | Check Command |
|-------------|---------|---------------|
| Python | 3.10+ | `python --version` |
| Flutter | 3.5+ | `flutter --version` |
| Docker | Latest | `docker --version` |
| SQLite | 3.x | `sqlite3 --version` |
| Node.js (for N8N) | 18+ | `node --version` |

### 7.2 Quick Start (5 minutes)

```bash
# 1. Copy template to new project
cp -r project_template/ ~/projects/my_new_project/
cd ~/projects/my_new_project/

# 2. Initialize project
chmod +x scripts/*.sh
./scripts/init_project.sh "My Project Name"

# 3. Configure environment
nano api/.env  # Edit settings

# 4. Start services
cd infrastructure
docker-compose up -d

# 5. Verify
curl http://localhost:5050/health
```

### 7.3 Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `PROJECT_NAME` | Project identifier | Yes | - |
| `API_PORT` | API server port | No | `5050` |
| `N8N_PORT` | N8N workflow port | No | `5678` |
| `DATABASE_PATH` | SQLite database path | No | `data/app.db` |
| `N8N_PASSWORD` | N8N admin password | Yes | Auto-generated |

### 7.4 Selective Skill Installation

```bash
# Install only specific skill categories
./scripts/init_project.sh "My Project" --skills flutter,python_api,devops

# Available categories:
# flutter, python_api, machine_learning, mql5, devops, n8n, agentic, integration
```

---

## 8. User Guide

### 8.1 Getting Started

**Choose Your Path:**

| Goal | Skills to Use | Time |
|------|---------------|------|
| Mobile App | flutter/ | 1 hour |
| REST API | python_api/ | 30 min |
| ML Pipeline | machine_learning/ | 2 hours |
| Trading Bot | mql5/ | 2 hours |
| Full Stack | All | 4 hours |

### 8.2 Using Templates

**Method 1: Copy and Customize**

```bash
# Copy template
cp skills/flutter/provider_template.dart lib/providers/my_provider.dart

# Replace placeholders
sed -i 's/{{FEATURE_NAME}}/MyFeature/g' lib/providers/my_provider.dart
```

**Method 2: Use Init Script**

```bash
./scripts/init_project.sh "My Project" --skills flutter,python_api
```

**Method 3: Reference Only**

Some skills are documentation guides (`.md` files) that provide implementation guidance without code templates.

### 8.3 Common Workflows

**Building a Flutter App:**

1. Start with `provider_template.dart` for state
2. Add `service_template.dart` for business logic
3. Create models with `model_template.dart`
4. Connect to API with `api_client_template.dart`
5. Add auth with `oauth_template.dart`

**Building an ML Service:**

1. Design features with `feature_engineering_template.py`
2. Train models with `training_template.py`
3. Ensemble with `ensemble_template.py`
4. Serve with `model_serving_template.py`
5. Automate retraining with `retrain_template.py`

---

## 9. Developer Guide

### 9.1 Adding New Skills

When you discover a reusable pattern:

1. **Document it** in the appropriate category README
2. **Create template** with `{{PLACEHOLDER}}` syntax
3. **Add to SKILLS_INDEX.md** with description
4. **Test** by using it in a new project
5. **Refine** based on usage feedback

### 9.2 Coding Standards

**Dart/Flutter:**

```dart
// Use camelCase for variables and functions
final myVariable = 'value';
void myFunction() {}

// Use PascalCase for classes
class MyClass {}

// Use SCREAMING_SNAKE_CASE for constants
const MAX_ITEMS = 100;
```

**Python:**

```python
# Use snake_case for variables and functions
my_variable = 'value'
def my_function():
    pass

# Use PascalCase for classes
class MyClass:
    pass
```

**MQL5:**

```cpp
// Use prefix conventions
m_memberVar;      // Member variable
g_globalVar;      // Global variable
InpParameter;     // Input parameter
CClassName;       // Class name
```

### 9.3 Template Guidelines

1. **Self-contained:** Each template should work independently
2. **Well-commented:** Explain non-obvious code
3. **Placeholder-ready:** Use `{{PLACEHOLDER}}` for customization
4. **Production-tested:** Only include patterns proven in production
5. **Documented:** Include README in each skill directory

---

## 10. Deployment

### 10.1 Docker Deployment

```bash
cd infrastructure
docker-compose up -d

# Services started:
# - API Server (port 5050)
# - N8N (port 5678)
# - WebSocket (port 8765)
```

### 10.2 Cloud Deployment

**Option 1: Manual Deploy**

```bash
ssh user@your-server
git clone your-repo
cd infrastructure
docker-compose up -d
```

**Option 2: Sync Script**

```bash
./infrastructure/cloud/sync.sh
```

### 10.3 Production Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    3-SITE ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   [Primary] ←──sync──→ [Portable] ←──deploy──→ [Secondary]  │
│     Mac                 SD Card               Windows/Cloud  │
│                                                              │
│   Development           Backup                Production     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 11. Security

### 11.1 Security Measures

| Measure | Implementation |
|---------|----------------|
| Authentication | OAuth template (Google/Apple/MS) |
| Data Encryption | TLS 1.3 in transit |
| API Security | Rate limiting, CORS, validation |
| Secrets | Environment variables |
| Input Validation | validation_template.py |

### 11.2 Best Practices

1. **Never commit secrets** - Use `.env` files
2. **Validate all inputs** - Use validation templates
3. **Use HTTPS** - Configure TLS in production
4. **Limit API exposure** - Use rate limiting
5. **Log security events** - Use logging templates

---

## 12. Performance

### 12.1 Template Metrics

| Template Category | Avg File Size | Setup Time |
|-------------------|---------------|------------|
| Flutter | 150-700 lines | 5-15 min |
| Python API | 100-250 lines | 5-10 min |
| ML | 200-400 lines | 15-30 min |
| MQL5 | 150-300 lines | 10-20 min |
| DevOps | 50-150 lines | 5-10 min |
| N8N | 50-100 nodes | 10-15 min |

### 12.2 Project Bootstrap Times

| Project Type | Templates Used | Total Setup |
|--------------|----------------|-------------|
| Simple API | 5 python templates | 30 min |
| Mobile App | 9 flutter templates | 1 hour |
| ML Service | 12 ML + 5 API | 2 hours |
| Full Trading System | All 82+ | 4 hours |

---

## 13. Roadmap

### Q1 2026
- [ ] Add more Flutter widget templates
- [ ] Create React/Next.js skill category
- [ ] Add FastAPI templates alongside Flask

### Q2 2026
- [ ] Create Rust API templates
- [ ] Add Kubernetes deployment templates
- [ ] Create mobile testing templates

### Future
- [ ] Interactive CLI for template selection
- [ ] Web-based template browser
- [ ] Community contribution system

---

## 14. Support

### 14.1 Documentation

| Resource | Location |
|----------|----------|
| Setup Guide | `SETUP.md` |
| Skills Index | `skills/SKILLS_INDEX.md` |
| Agent System | `agents/AGENT_SYSTEM.md` |
| KB Setup | `docs/AGENT_KNOWLEDGE_BASE_SETUP.md` |

### 14.2 Troubleshooting

**Docker Issues:**

```bash
docker-compose ps          # Check status
docker-compose logs api    # View logs
docker-compose restart     # Restart all
```

**Database Issues:**

```bash
rm knowledge_base/kb.db
sqlite3 knowledge_base/kb.db < knowledge_base/schema.sql
```

**Port Conflicts:**

```bash
# Edit api/.env
API_PORT=5051
N8N_PORT=5679
docker-compose up -d
```

### 14.3 Contributing

1. Create template in appropriate directory
2. Add entry to SKILLS_INDEX.md
3. Test in a real project
4. Submit for review

---

## Appendix

### A. Glossary

| Term | Definition |
|------|------------|
| **Skill** | A reusable code pattern with placeholders |
| **Template** | A file containing a skill |
| **Placeholder** | `{{NAME}}` syntax for customization |
| **KB** | Knowledge Base for project documentation |
| **ReAct** | Reasoning + Acting pattern for AI agents |

### B. Complete Skills List (82+)

| # | Category | Template | Description |
|---|----------|----------|-------------|
| 1 | Flutter | provider_template.dart | State management |
| 2 | Flutter | service_template.dart | Business logic |
| 3 | Flutter | model_template.dart | Data models |
| 4 | Flutter | api_client_template.dart | HTTP client |
| 5 | Flutter | websocket_client_template.dart | Real-time |
| 6 | Flutter | widget_composition_template.dart | UI patterns |
| 7 | Flutter | theme_constants_template.dart | Design system |
| 8 | Flutter | plugin_template.dart | Plugin system |
| 9 | Flutter | oauth_template.dart | Authentication |
| 10-19 | Python API | 10 templates | API patterns |
| 20-31 | ML | 12 templates | ML pipeline |
| 32-39 | MQL5 | 8 templates | Trading EA |
| 40-49 | DevOps | 10 templates | Infrastructure |
| 50-55 | N8N | 6 templates | Workflows |
| 56-75 | Agentic | 20 templates | AI agents |
| 76-83 | Integration | 8 templates | Cross-system |

### C. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | Jan 2026 | Initial release with 82 skills |

---

*Document generated with Project Template v1.0*
*Last Updated: January 12, 2026*
