# New Project Workflow

**Version:** 1.0
**Updated:** 2026-01-12

A step-by-step guide for creating new projects using the Fokha Project Template.

---

## Overview

This workflow covers:
1. Project initialization from templates
2. Documentation setup
3. Agent system configuration
4. Infrastructure deployment
5. Skills integration

---

## Quick Start (5 Minutes)

```bash
# 1. Create new project
./scripts/init_project.sh "/path/to/new_project" "My Project Name"

# 2. Navigate to project
cd /path/to/new_project

# 3. Start services
docker-compose -f infrastructure/docker-compose.yml up -d

# 4. Verify
curl http://localhost:5050/health
```

---

## Complete Workflow

### Phase 1: Project Creation

#### Step 1.1: Copy Template

```bash
# Option A: Copy entire template
cp -r ~/Documents/development/ai_studio/project_template/ ~/projects/my_new_project/

# Option B: Use init script (recommended)
cd ~/Documents/development/ai_studio/project_template
./scripts/init_project.sh ~/projects/my_new_project "My Project Name"
```

#### Step 1.2: Initialize Project

```bash
cd ~/projects/my_new_project
chmod +x scripts/*.sh agents/*.sh

# Run initialization
./scripts/init_project.sh "My Project Name"
```

**What gets created:**
| Item | Description |
|------|-------------|
| `api/.env` | Environment configuration (auto-generated passwords) |
| `.gitignore` | Git ignore rules |
| `CLAUDE.md` | Project context for Claude Code |
| `VERSION` | Version file (starts at 1.0.0) |
| `knowledge_base/kb.db` | SQLite database from schema |
| Directory structure | All required folders |

---

### Phase 2: Documentation Setup

#### Step 2.1: Fill Out Core Documents

Use the templates in `docs/` to create your project documentation:

```bash
# Copy and customize each template
cp docs/README_TEMPLATE.md README.md
cp docs/PRD_TEMPLATE.md docs/PRD.md
cp docs/DEV_GUIDE_TEMPLATE.md docs/DEV_GUIDE.md
cp docs/PROJECT_STRUCTURE_TEMPLATE.md docs/PROJECT_STRUCTURE.md
cp docs/CLAUDE_TEMPLATE.md CLAUDE.md
```

#### Step 2.2: Replace Placeholders

All templates use `{{PLACEHOLDER}}` format. Replace these with your project values:

```bash
# Example: Replace project name across all files
find . -name "*.md" -exec sed -i '' 's/{{PROJECT_NAME}}/MyAwesomeProject/g' {} \;

# Or manually edit each file
```

**Key placeholders to replace:**

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{PROJECT_NAME}}` | Project name | `TradingBot` |
| `{{PROJECT_TAGLINE}}` | One-line description | `Automated trading signals` |
| `{{VERSION}}` | Current version | `1.0.0` |
| `{{REPO_URL}}` | Git repository URL | `https://github.com/user/repo` |
| `{{PORT}}` | Main service port | `5050` |
| `{{AUTHOR_NAME}}` | Your name | `Fokha` |

#### Step 2.3: Update CLAUDE.md

This is the most important file - it gives Claude Code context about your project:

```markdown
# My Project Name

## Overview
[2-3 sentences about what this project does]

## Architecture
- **API**: Python Flask (port 5050)
- **Database**: SQLite Knowledge Base
- **Automation**: n8n workflows
- **Agents**: Multi-agent system with [list roles]

## Key Commands
- `./scripts/dev-start.sh` - Start development
- `./agents/init_agents.sh . minimal` - Launch agents

## Conventions
[Your coding standards, naming conventions, etc.]
```

---

### Phase 3: Agent System Setup

#### Step 3.1: Choose Team Configuration

Available team types in `agents/init_agents.sh`:

| Team | Agents | Use Case |
|------|--------|----------|
| `minimal` | ORCHESTRATOR, PYTHON_ML, REVIEWER | Small projects |
| `backend` | ORCHESTRATOR, PYTHON_ML, DEVOPS, REVIEWER | Backend-focused |
| `frontend` | ORCHESTRATOR, FLUTTER_AGENT, PYTHON_ML, REVIEWER | Mobile/UI projects |
| `full` | All 8 agents | Large projects |
| `research` | ORCHESTRATOR, RESEARCHER, PYTHON_ML, REVIEWER | Research projects |
| `automation` | ORCHESTRATOR, N8N_AGENT, DEVOPS, PYTHON_ML | Automation focus |
| `docs` | ORCHESTRATOR, RESEARCHER, DOCUMENTATION | Documentation projects |
| `custom` | Your choice | Custom setup |

#### Step 3.2: Initialize Agent Infrastructure

```bash
cd ~/projects/my_new_project

# Initialize with chosen team (e.g., minimal)
./agents/init_agents.sh . minimal

# Or with custom agents
./agents/init_agents.sh . custom PYTHON_ML RESEARCHER REVIEWER
```

**What gets created:**
```
.agents/
├── project_kb.db      # Agent database (SQLite)
├── agent_tools.py     # CLI for agent operations
├── QUICK_PROMPT.md    # Quick reference
├── sessions/          # Session logs
└── logs/              # Activity logs
```

#### Step 3.3: Launch Agents (Optional)

```bash
# Launch in tmux (interactive prompt)
./agents/init_agents.sh . minimal
# Answer 'y' to launch

# Attach to session
tmux attach -t agents-my_new_project

# Navigate: Ctrl+B 0-9 or Ctrl+B n/p
```

#### Step 3.4: Agent Quick Commands

```bash
# Register an agent
python3 .agents/agent_tools.py register PYTHON_ML --focus "Backend development"

# List active agents
python3 .agents/agent_tools.py list

# Send message between agents
python3 .agents/agent_tools.py msg send PYTHON_ML REVIEWER "Code Review" "Please review auth module"

# Start a session
python3 .agents/agent_tools.py session start PYTHON_ML
# Returns SESSION_ID: SESS-PYTH-20260112...

# Log work
python3 .agents/agent_tools.py session log $SID "Implemented auth endpoints"

# End session
python3 .agents/agent_tools.py session end $SID "Completed auth module"
```

---

### Phase 4: Infrastructure Setup

#### Step 4.1: Configure Environment

```bash
cd ~/projects/my_new_project

# Edit environment file
nano api/.env
```

**Key settings:**
```bash
PROJECT_NAME=MyProject
API_PORT=5050
N8N_PORT=5678

# Add your API keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

#### Step 4.2: Start Services with Docker

```bash
cd infrastructure

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api
```

#### Step 4.3: Manual Development Setup (Alternative)

```bash
# Python API
cd api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python api_server.py

# In another terminal - Knowledge Base
sqlite3 knowledge_base/kb.db < knowledge_base/schema.sql
```

#### Step 4.4: Use tmux Development Environment

```bash
# Start organized dev environment
./scripts/dev-start.sh

# Layout:
# ┌─────────────┬─────────────┬─────────────┐
# │  0: API     │  1: Docker  │  2: Cloud   │
# ├─────────────┼─────────────┼─────────────┤
# │  3: Logs    │  4: Claude  │  5: Shell   │
# └─────────────┴─────────────┴─────────────┘

# Stop
./scripts/dev-stop.sh
```

---

### Phase 5: Skills Integration

#### Step 5.1: Browse Available Skills

```bash
# View skills index
cat skills/SKILLS_INDEX.md

# Or list by category
ls skills/
# agentic/        (20 patterns)
# devops/         (10 patterns)
# flutter/        (8 patterns)
# integration/    (8 patterns)
# machine_learning/ (12 patterns)
# mql5/           (8 patterns)
# n8n/            (6 patterns)
# python_api/     (10 patterns)
```

#### Step 5.2: Copy Needed Skills

```bash
# Example: Add Flask endpoint template
cp skills/python_api/endpoint_template.py api/routes/my_endpoint.py

# Example: Add provider for Flutter
cp skills/flutter/provider_template.dart app/lib/providers/my_provider.dart

# Example: Add Docker setup
cp skills/devops/docker-compose.template.yml infrastructure/docker-compose.yml
```

#### Step 5.3: Customize Skills

Replace placeholders in copied skills:

```bash
# Replace feature name
sed -i '' 's/{{FEATURE_NAME}}/UserAuth/g' api/routes/my_endpoint.py
sed -i '' 's/{{feature_name}}/user_auth/g' api/routes/my_endpoint.py
```

---

## Project Checklist

### Initial Setup
- [ ] Copy template to new location
- [ ] Run `init_project.sh`
- [ ] Configure `api/.env`
- [ ] Update `CLAUDE.md` with project context

### Documentation
- [ ] Create `README.md` from template
- [ ] Create `docs/PRD.md` (Product Requirements)
- [ ] Create `docs/DEV_GUIDE.md`
- [ ] Update `docs/PROJECT_STRUCTURE.md`

### Agent System
- [ ] Choose team configuration
- [ ] Run `init_agents.sh`
- [ ] Customize agent prompts (optional)

### Infrastructure
- [ ] Docker services running
- [ ] Knowledge base initialized
- [ ] API responding to `/health`

### Development
- [ ] Dev environment working (`dev-start.sh`)
- [ ] Git initialized with `.gitignore`
- [ ] First commit made

---

## Template File Reference

### Documentation Templates (`docs/`)

| File | Purpose | Size |
|------|---------|------|
| `README_TEMPLATE.md` | Project README | 10.6 KB |
| `PRD_TEMPLATE.md` | Product Requirements | 12.2 KB |
| `DEV_GUIDE_TEMPLATE.md` | Developer Guide | 14.9 KB |
| `PROJECT_STRUCTURE_TEMPLATE.md` | Directory docs | 10.3 KB |
| `CLAUDE_TEMPLATE.md` | Claude Code context | 28.3 KB |
| `AGENT_KNOWLEDGE_BASE_SETUP.md` | KB setup guide | 10.9 KB |

### Agent Templates (`agents/`)

| File | Purpose |
|------|---------|
| `init_agents.sh` | Initialize agent system |
| `AGENT_SYSTEM.md` | Agent architecture docs |
| `prompts/AGENT_SYSTEM_PROMPT_TEMPLATE.md` | Agent prompt template |
| `prompts/PROMPT_STYLE_GUIDE.md` | Prompt writing guide |

### Skills Library (`skills/`)

| Category | Count | Key Patterns |
|----------|-------|--------------|
| `agentic/` | 20 | ReAct planning, consensus, memory |
| `python_api/` | 10 | Endpoints, blueprints, validation |
| `machine_learning/` | 12 | Training, inference, pipelines |
| `flutter/` | 8 | Providers, services, widgets |
| `devops/` | 10 | Docker, CI/CD, monitoring |
| `integration/` | 8 | Webhooks, bridges, sync |
| `mql5/` | 8 | EA patterns, indicators |
| `n8n/` | 6 | Workflow patterns |

### Scripts (`scripts/`)

| Script | Purpose |
|--------|---------|
| `init_project.sh` | Initialize new project |
| `dev-start.sh` | Start tmux dev environment |
| `dev-stop.sh` | Stop tmux session |
| `update_skills.sh` | Update skills from source |

---

## Directory Structure After Setup

```
my_new_project/
├── README.md               # From README_TEMPLATE.md
├── CLAUDE.md               # Project context (critical!)
├── VERSION                 # 1.0.0
├── .gitignore              # Auto-generated
│
├── api/                    # Python API
│   ├── .env                # Configuration
│   ├── api_server.py       # Main server
│   ├── requirements.txt
│   └── utils/
│       └── kb_api.py       # Knowledge Base API
│
├── .agents/                # Agent system
│   ├── project_kb.db       # Agent database
│   ├── agent_tools.py      # Agent CLI
│   ├── QUICK_PROMPT.md     # Quick reference
│   ├── sessions/
│   └── logs/
│
├── agents/                 # Agent templates
│   ├── init_agents.sh
│   ├── AGENT_SYSTEM.md
│   └── prompts/
│
├── knowledge_base/         # Project KB
│   ├── kb.db               # Main database
│   ├── schema.sql
│   └── documents/
│
├── infrastructure/         # Docker & cloud
│   ├── docker-compose.yml
│   └── cloud/
│
├── skills/                 # Reusable patterns
│   ├── python_api/
│   ├── flutter/
│   └── ...
│
├── docs/                   # Documentation
│   ├── PRD.md
│   ├── DEV_GUIDE.md
│   └── ...
│
├── app/                    # Frontend (if needed)
│   └── lib/
│       └── theme/
│
└── scripts/                # Utility scripts
    ├── init_project.sh
    ├── dev-start.sh
    └── dev-stop.sh
```

---

## Troubleshooting

### Agent System Issues

```bash
# Database locked
sqlite3 .agents/project_kb.db "PRAGMA busy_timeout = 5000;"

# Reset agent database
rm .agents/project_kb.db
./agents/init_agents.sh . minimal
```

### Docker Issues

```bash
# Port conflicts
# Edit api/.env to use different ports

# Container won't start
docker-compose logs api
docker-compose down && docker-compose up -d
```

### Knowledge Base Issues

```bash
# Reset KB
rm knowledge_base/kb.db
sqlite3 knowledge_base/kb.db < knowledge_base/schema.sql

# Check tables
sqlite3 knowledge_base/kb.db ".tables"
```

---

## Next Steps After Setup

1. **Define your project** in CLAUDE.md
2. **Create first tasks** in knowledge base
3. **Add custom endpoints** to api_server.py
4. **Configure n8n workflows** for automation
5. **Set up CI/CD** for deployment

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│                 NEW PROJECT QUICK REFERENCE                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  CREATE PROJECT                                             │
│  ./scripts/init_project.sh /path/to/project "Name"         │
│                                                             │
│  SETUP AGENTS                                               │
│  ./agents/init_agents.sh . minimal                          │
│                                                             │
│  START SERVICES                                             │
│  docker-compose -f infrastructure/docker-compose.yml up -d  │
│                                                             │
│  DEV ENVIRONMENT                                            │
│  ./scripts/dev-start.sh                                     │
│                                                             │
│  VERIFY                                                     │
│  curl http://localhost:5050/health                          │
│                                                             │
│  AGENT COMMANDS                                             │
│  python3 .agents/agent_tools.py register ROLE               │
│  python3 .agents/agent_tools.py list                        │
│  python3 .agents/agent_tools.py msg send FROM TO "Subj" "Msg"│
│                                                             │
│  TEMPLATES TO CUSTOMIZE                                     │
│  docs/README_TEMPLATE.md → README.md                        │
│  docs/CLAUDE_TEMPLATE.md → CLAUDE.md                        │
│  docs/PRD_TEMPLATE.md → docs/PRD.md                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```
