# Fokha Project Template v2.1

A complete project template with multi-agent system, knowledge base, automation, cloud infrastructure, **74 reusable code patterns**, **5 documentation templates**, and **8 Claude Code skill templates**.

**Total Templates: 87+**

---

## What's New in v2.1

- **Documentation Templates** - 5 comprehensive templates (~2,500 lines)
- **Claude Code Skills** - 8 reusable skill templates
- **Updated Skills Library** - 74 production-tested code patterns
- **Skills Sync Script** - `update_skills.sh` with 50+ pattern mappings

---

## Quick Overview

```
project_template/
├── docs/                        # 📄 Documentation Templates (NEW!)
│   ├── README_TEMPLATE.md       #    Project README (~560 lines)
│   ├── PRD_TEMPLATE.md          #    Product Requirements (~450 lines)
│   ├── DEV_GUIDE_TEMPLATE.md    #    Developer Guide (~550 lines)
│   ├── PROJECT_STRUCTURE_TEMPLATE.md
│   └── CLAUDE_TEMPLATE.md       #    AI Agent docs (~544 lines)
│
├── claude/                      # 🤖 Claude Code Skills (NEW!)
│   └── skills/                  #    8 workflow templates
│       ├── status.md            #    System health checks
│       ├── preflight.md         #    Pre-task verification
│       ├── done.md              #    Definition of done
│       ├── commit.md            #    Git commit helper
│       ├── test.md              #    Test execution guide
│       ├── deploy.md            #    Deployment procedures
│       ├── debug.md             #    Debugging guide
│       └── update-docs.md       #    Documentation updates
│
├── skills/                      # 💡 Code Templates (74 patterns)
│   ├── flutter/         (8)     #    Flutter/Dart patterns
│   ├── python_api/      (10)    #    Python Flask patterns
│   ├── machine_learning/(12)    #    ML pipeline patterns
│   ├── agentic/         (20)    #    AI agent patterns
│   ├── devops/          (9)     #    Infrastructure patterns
│   ├── integration/     (8)     #    Cross-system patterns
│   ├── n8n/             (6)     #    Workflow patterns
│   └── mql5/            (1)     #    MetaTrader 5 patterns
│
├── agents/                      # 🧠 Multi-Agent System
├── knowledge_base/              # 📚 Knowledge Base
├── infrastructure/              # ☁️  Cloud & Docker
├── scripts/                     # 🔧 Automation Scripts
└── api/                         # 🔌 Python API Template
```

---

## Documentation Templates

New in v2.1: Complete documentation templates for any project.

| Template | Lines | Purpose |
|----------|-------|---------|
| `README_TEMPLATE.md` | ~560 | Project README with all essential sections |
| `PRD_TEMPLATE.md` | ~450 | Product Requirements Document |
| `DEV_GUIDE_TEMPLATE.md` | ~550 | Developer onboarding & reference |
| `PROJECT_STRUCTURE_TEMPLATE.md` | ~350 | Codebase documentation |
| `CLAUDE_TEMPLATE.md` | ~544 | AI agent master documentation |

### Usage

```bash
# Copy template to your project
cp docs/README_TEMPLATE.md ~/my_project/README.md

# Replace placeholders
sed -i '' 's/{{PROJECT_NAME}}/MyProject/g' ~/my_project/README.md
sed -i '' 's/{{VERSION}}/1.0.0/g' ~/my_project/README.md
```

### Key Sections in Each Template

**README_TEMPLATE.md:**
- Features, Demo, Quick Start, Installation
- Usage, Configuration, API Reference
- Development, Testing, Deployment
- Contributing, Roadmap, FAQ, License

**PRD_TEMPLATE.md:**
- Executive Summary, Problem Statement
- Goals & KPIs, User Personas
- Feature Requirements with Priority Matrix
- Technical & Non-Functional Requirements
- Timeline, Risks, Sign-off

**DEV_GUIDE_TEMPLATE.md:**
- Quick Start, Project Structure
- Environment Setup, Coding Standards
- Architecture Overview, API Reference
- Database Schema, Testing Guide
- Deployment, Troubleshooting

**CLAUDE_TEMPLATE.md:**
- Project Overview, Architecture
- API Reference, Database Schema
- Workflows & Automation
- Agent Instructions (mandatory rules)
- Commands & Shortcuts

---

## Claude Code Skills

Templates for common development workflows. Copy to `.claude/skills/` in your project.

| Skill | Purpose |
|-------|---------|
| `status.md` | System health check commands |
| `preflight.md` | Pre-task environment verification |
| `done.md` | Task completion checklist |
| `update-docs.md` | Documentation update workflow |
| `commit.md` | Git commit conventions |
| `test.md` | Test execution guide |
| `deploy.md` | Deployment procedures |
| `debug.md` | Debugging tools & techniques |

### Setup

```bash
# Copy to your project
cp -r claude/skills/ ~/my_project/.claude/skills/

# Customize placeholders
sed -i '' 's/{{PORT}}/3000/g' ~/my_project/.claude/skills/*.md
sed -i '' 's/{{TEST_CMD}}/npm test/g' ~/my_project/.claude/skills/*.md
```

### Invoke Skills

After setup, use as slash commands in Claude Code:
- `/status` - Check system health
- `/preflight` - Pre-task checklist
- `/done` - Verify task completion
- `/commit` - Git commit helper

---

## Code Skills Library (74 Patterns)

Production-tested code templates extracted from the Fokha Trading System.

### Categories

| Category | Count | Description |
|----------|-------|-------------|
| **flutter/** | 8 | Provider, Service, Model, Widget, API Client, WebSocket, Theme, Plugin |
| **python_api/** | 10 | Blueprint, Endpoint, Database, Cache, Validation, Health Check |
| **machine_learning/** | 12 | Training, Serving, Feature Engineering, Walk-forward, Ensemble |
| **agentic/** | 20 | All 20 agentic design patterns (ReAct, Consensus, Debate, etc.) |
| **devops/** | 9 | Docker, CI/CD, Monitoring, Backup, Secrets Management |
| **integration/** | 8 | WebSocket, Telegram Bot, MT5 Bridge, Webhook Handler |
| **n8n/** | 6 | Cron, Webhook, API Poller, Error Handler |
| **mql5/** | 1 | EA Template, Risk Manager, Strategy Base |

### Quick Usage

```bash
# Copy a template
cp skills/python_api/endpoint_template.py ~/my_project/api/users.py

# Replace placeholders
sed -i '' 's/{{FEATURE_NAME}}/users/g' ~/my_project/api/users.py
```

### Sync Script

Use `scripts/update_skills.sh` to sync skills from any project:

```bash
# List all skills
./scripts/update_skills.sh --list

# Dry-run sync
./scripts/update_skills.sh --dry-run --all

# Sync specific category
./scripts/update_skills.sh --category flutter
```

See `skills/README.md` and `skills/SKILLS_INDEX.md` for full documentation.

---

## Multi-Agent System

```
agents/
├── AGENT_SYSTEM.md              # Architecture documentation
├── README.md                    # Agent setup guide
├── init_agents.sh               # Initialize agent system
└── prompts/
    ├── AGENT_SYSTEM_PROMPT_TEMPLATE.md
    └── PROMPT_STYLE_GUIDE.md
```

### Agent Roles

| Agent | Responsibility |
|-------|----------------|
| Orchestrator | Task coordination, delegation |
| Developer | Implementation, coding |
| Researcher | Information gathering |
| Reviewer | Quality assurance |

---

## Knowledge Base

SQLite-based knowledge base for project memory.

```
knowledge_base/
├── schema.sql                   # Database schema
├── migrations/
│   └── LESSONS_LEARNED.md       # Architecture insights
└── docs/
    └── AGENT_KNOWLEDGE_BASE_SETUP.md
```

### Key Tables

| Table | Purpose |
|-------|---------|
| `kb_tasks` | Work tracking |
| `kb_decisions` | Architecture decisions |
| `kb_messages` | Inter-agent communication |
| `kb_session_context` | Session persistence |
| `kb_activity_log` | Audit trail |

---

## Infrastructure

```
infrastructure/
├── docker-compose.yml           # Full stack compose
└── (cloud deployment configs)
```

### Scripts

| Script | Purpose |
|--------|---------|
| `scripts/dev-start.sh` | Start tmux dev environment |
| `scripts/dev-stop.sh` | Stop dev environment |
| `scripts/init_project.sh` | Initialize new project |
| `scripts/update_skills.sh` | Sync skills from source |

---

## Quick Start

```bash
# 1. Clone template
cp -r project_template/ ~/my_new_project/
cd ~/my_new_project

# 2. Initialize
./scripts/init_project.sh "My Project Name"

# 3. Copy documentation templates
cp docs/README_TEMPLATE.md README.md
cp docs/CLAUDE_TEMPLATE.md CLAUDE.md

# 4. Setup Claude Code skills
mkdir -p .claude/skills
cp -r claude/skills/* .claude/skills/

# 5. Customize placeholders
sed -i '' 's/{{PROJECT_NAME}}/MyProject/g' README.md CLAUDE.md
sed -i '' 's/{{PORT}}/3000/g' .claude/skills/*.md

# 6. Start dev environment
./scripts/dev-start.sh
```

---

## Dev Environment (tmux)

```bash
./scripts/dev-start.sh
```

**Pane Layout:**
```
┌─────────────┬─────────────┬─────────────┐
│  0: API     │  1: Docker  │  2: Cloud   │
├─────────────┼─────────────┼─────────────┤
│  3: Logs    │  4: Claude  │  5: Shell   │
└─────────────┴─────────────┴─────────────┘
```

**tmux Shortcuts (prefix = `Ctrl+B`):**
| Shortcut | Action |
|----------|--------|
| `Ctrl+B ←→↑↓` | Navigate panes |
| `Ctrl+B z` | Zoom/Unzoom pane |
| `Ctrl+B d` | Detach session |
| `Ctrl+B [` | Scroll mode (q to exit) |

---

## Template Counts Summary

| Category | Templates |
|----------|-----------|
| Documentation (docs/) | 5 |
| Claude Skills (claude/skills/) | 8 |
| Flutter Code (skills/flutter/) | 8 |
| Python API (skills/python_api/) | 10 |
| Machine Learning (skills/machine_learning/) | 12 |
| Agentic AI (skills/agentic/) | 20 |
| DevOps (skills/devops/) | 9 |
| Integration (skills/integration/) | 8 |
| N8N Workflows (skills/n8n/) | 6 |
| MQL5 (skills/mql5/) | 1 |
| **Total** | **87+** |

---

## Key Learnings

### 1. Single Source of Truth
All agents share ONE Knowledge Base. No silos.

### 2. Session Recovery Pattern
```
GET /kb/resume → Full context in one call
```

### 3. Placeholder Convention
Use `{{PLACEHOLDER}}` syntax for easy find-replace:
```bash
sed -i '' 's/{{PROJECT_NAME}}/MyApp/g' file.md
```

### 4. Documentation First
Every project needs:
- README.md (from README_TEMPLATE)
- CLAUDE.md (from CLAUDE_TEMPLATE)
- CHANGELOG.md
- VERSION file

### 5. Skills as Workflows
Claude Code skills = reusable workflow checklists.

---

## Documentation Index

| File | Purpose |
|------|---------|
| `docs/README_TEMPLATE.md` | Project README template |
| `docs/PRD_TEMPLATE.md` | Product requirements template |
| `docs/DEV_GUIDE_TEMPLATE.md` | Developer guide template |
| `docs/PROJECT_STRUCTURE_TEMPLATE.md` | Codebase docs template |
| `docs/CLAUDE_TEMPLATE.md` | AI agent docs template |
| `claude/skills/README.md` | Skills setup guide |
| `skills/README.md` | Code templates guide |
| `skills/SKILLS_INDEX.md` | Full skills reference |
| `agents/AGENT_SYSTEM.md` | Agent architecture |
| `knowledge_base/migrations/LESSONS_LEARNED.md` | Architecture insights |

---

## License

MIT - Use freely for any project.

---

*Template Version: 2.1 | Last Updated: January 2026*
