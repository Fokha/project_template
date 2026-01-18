# Project Template

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/Fokha/project_template.svg)](https://github.com/Fokha/project_template/stargazers)

A production-ready project template featuring a **multi-agent system**, **150+ reusable code patterns**, and **Claude Code integration**. Battle-tested in the Fokha Trading System.

## Features

- **Multi-Agent System** - Hierarchical agents (THE_ASSISTANT, THE_MASTER, Specialists)
- **Skills Library** - 120+ code templates across 9 categories
- **Claude Code Integration** - 10+ slash commands ready to use
- **Documentation Templates** - README, PRD, Dev Guide, CLAUDE.md
- **Knowledge Base** - SQLite schema for project memory
- **DevOps Ready** - Docker, CI/CD, monitoring templates

---

## Quick Start

```bash
# Clone the template
git clone https://github.com/Fokha/project_template.git my-project
cd my-project

# Remove git history and start fresh
rm -rf .git && git init

# Initialize your project
./scripts/init_project.sh "My Project Name"

# Start development
./scripts/dev-start.sh
```

---

## Project Structure

```
project_template/
├── .claude/                    # Claude Code configuration
│   ├── commands/               # 10 slash commands
│   └── settings.json           # Claude Code settings
│
├── agents/                     # Multi-Agent System
│   ├── prompts/                # Agent prompt templates
│   │   ├── THE_ASSISTANT.md    # User interface agent
│   │   ├── THE_MASTER.md       # Strategic architect
│   │   ├── BACKEND_DEV_AGENT.md
│   │   ├── DEVOPS_AGENT.md
│   │   └── SPECIALIST_AGENT_TEMPLATE.md
│   └── AGENT_SYSTEM.md         # Architecture docs
│
├── skills/                     # Code Templates (120+ patterns)
│   ├── agentic/        (21)    # AI agent patterns
│   ├── data_layer/     (47)    # Data handling patterns
│   ├── devops/         (10)    # Infrastructure patterns
│   ├── flutter/        (10)    # Dart/Flutter patterns
│   ├── integration/    (8)     # Cross-system patterns
│   ├── machine_learning/(12)   # ML pipeline patterns
│   ├── mql5/           (9)     # MetaTrader 5 patterns
│   ├── n8n/            (6)     # Workflow automation
│   └── python_api/     (10)    # Flask API patterns
│
├── docs/                       # Documentation Templates
│   ├── README_TEMPLATE.md
│   ├── PRD_TEMPLATE.md
│   ├── DEV_GUIDE_TEMPLATE.md
│   ├── CLAUDE_TEMPLATE.md
│   └── PROJECT_STRUCTURE_TEMPLATE.md
│
├── claude/skills/              # Claude Code Skills (8)
├── knowledge_base/             # SQLite KB schema
├── infrastructure/             # Docker configs
└── scripts/                    # Automation scripts
```

---

## Multi-Agent System

A hierarchical agent architecture with clear separation of concerns:

```
                    USER
                      │
                      ▼
            ┌─────────────────┐
            │  THE_ASSISTANT  │  ← Layer 1: User Interface
            │   (Supervisor)  │
            └────────┬────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
   ┌─────────┐  ┌─────────┐  ┌─────────┐
   │ MASTER  │  │ Direct  │  │ Direct  │  ← Layer 2: Routing
   │(Architect)│  │ Execute │  │ Query   │
   └────┬────┘  └─────────┘  └─────────┘
        │
   ┌────┴────┬─────────┬─────────┐
   ▼         ▼         ▼         ▼         ← Layer 3: Specialists
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│BACKEND│ │FRONTEND│ │DEVOPS│ │ ...  │
└──────┘ └──────┘ └──────┘ └──────┘
```

### Agent Roles

| Agent | Role | When to Use |
|-------|------|-------------|
| THE_ASSISTANT | User interface, task routing | All user interactions |
| THE_MASTER | Architecture, strategic decisions | New features, tech choices |
| BACKEND_DEV | APIs, databases, server logic | Backend implementation |
| DEVOPS | Infrastructure, deployment | CI/CD, Docker, monitoring |

---

## Skills Library

### Categories

| Category | Count | Description |
|----------|-------|-------------|
| `agentic/` | 21 | ReAct, Consensus, Debate, Reflection, Routing, etc. |
| `data_layer/` | 47 | Models, Factory, Processors, Storage, Pipeline |
| `devops/` | 10 | Docker, CI/CD, monitoring, backup, secrets |
| `flutter/` | 10 | Providers, services, models, widgets, OAuth |
| `integration/` | 8 | WebSocket, Telegram, webhooks, MT5 bridge |
| `machine_learning/` | 12 | Training, serving, walk-forward, ensembles |
| `mql5/` | 9 | EA template, indicators, risk management |
| `n8n/` | 6 | Cron workflows, API polling, error handling |
| `python_api/` | 10 | Flask blueprints, endpoints, validation, caching |

### Usage

```bash
# Copy a template to your project
cp skills/python_api/endpoint_template.py src/api/users.py

# Replace placeholders
sed -i '' 's/{{FEATURE_NAME}}/users/g' src/api/users.py
sed -i '' 's/{{MODEL_NAME}}/User/g' src/api/users.py
```

---

## Claude Code Integration

### Slash Commands

Pre-configured commands in `.claude/commands/`:

| Command | Description |
|---------|-------------|
| `/status` | Check system health |
| `/task` | Task management |
| `/agent` | Agent coordination |
| `/session` | Session management |
| `/backup` | Backup operations |
| `/sync` | Sync commands |
| `/infra` | Infrastructure commands |
| `/msg` | Inter-agent messaging |
| `/complete` | Task completion |
| `/tools` | Available tools index |

### Setup in Your Project

```bash
# Copy Claude Code configuration
cp -r .claude/ ~/my-project/.claude/

# Customize settings
vim ~/my-project/.claude/settings.json
```

---

## Documentation Templates

| Template | Purpose | Lines |
|----------|---------|-------|
| `README_TEMPLATE.md` | Project README | ~560 |
| `PRD_TEMPLATE.md` | Product Requirements | ~450 |
| `DEV_GUIDE_TEMPLATE.md` | Developer Guide | ~550 |
| `CLAUDE_TEMPLATE.md` | AI Agent Documentation | ~544 |
| `PROJECT_STRUCTURE_TEMPLATE.md` | Codebase Docs | ~350 |

### Placeholders

All templates use `{{PLACEHOLDER}}` syntax:

```bash
# Replace all placeholders
sed -i '' 's/{{PROJECT_NAME}}/MyApp/g' docs/*.md
sed -i '' 's/{{VERSION}}/1.0.0/g' docs/*.md
sed -i '' 's/{{AUTHOR}}/Your Name/g' docs/*.md
```

---

## Knowledge Base

SQLite-based project memory with schema for:

| Table | Purpose |
|-------|---------|
| `kb_tasks` | Task tracking |
| `kb_decisions` | Architecture decisions |
| `kb_messages` | Agent communication |
| `kb_session_context` | Session persistence |
| `kb_activity_log` | Audit trail |

```bash
# Initialize knowledge base
sqlite3 knowledge_base/project_kb.db < knowledge_base/schema.sql
```

---

## Scripts

| Script | Purpose |
|--------|---------|
| `init_project.sh` | Initialize new project from template |
| `dev-start.sh` | Start tmux development environment |
| `dev-stop.sh` | Stop development environment |
| `update_skills.sh` | Sync skills from source project |
| `create_project.sh` | Create new project structure |
| `complete_task.sh` | Mark task as complete |

---

## Development Environment

```bash
./scripts/dev-start.sh
```

Creates a tmux session with 6 panes:

```
┌─────────────┬─────────────┬─────────────┐
│  0: API     │  1: Docker  │  2: Cloud   │
├─────────────┼─────────────┼─────────────┤
│  3: Logs    │  4: Claude  │  5: Shell   │
└─────────────┴─────────────┴─────────────┘
```

---

## Creating a New Project

```bash
# 1. Clone template
git clone https://github.com/Fokha/project_template.git my-app
cd my-app

# 2. Reset git
rm -rf .git
git init
git add -A
git commit -m "Initial commit from project_template"

# 3. Initialize
./scripts/init_project.sh "My App"

# 4. Customize documentation
cp docs/README_TEMPLATE.md README.md
cp docs/CLAUDE_TEMPLATE.md CLAUDE.md

# 5. Replace placeholders
find . -type f -name "*.md" -exec sed -i '' 's/{{PROJECT_NAME}}/My App/g' {} \;

# 6. Create GitHub repo
gh repo create my-app --public --source . --push
```

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open a Pull Request

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Acknowledgments

- Built with patterns from [Claude Code](https://claude.ai/claude-code)
- Agent architecture inspired by multi-agent systems research
- Battle-tested in the Fokha Trading System

---

**Version:** 2.2 | **Last Updated:** January 2026
