#!/bin/bash

# ============================================
# FOKHA PROJECT CREATOR - Master Script
# Creates a complete project from templates
# Usage: ./create_project.sh <project_path> <project_name> [team_type]
# ============================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Get script directory (template location)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$(dirname "$SCRIPT_DIR")"

# Arguments
PROJECT_PATH="${1:-}"
PROJECT_NAME="${2:-}"
TEAM_TYPE="${3:-minimal}"

# Banner
echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║           FOKHA PROJECT CREATOR v1.0                          ║"
echo "║           Create complete projects from templates              ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Help
show_help() {
    echo "Usage: $0 <project_path> <project_name> [team_type]"
    echo ""
    echo "Arguments:"
    echo "  project_path    Where to create the project"
    echo "  project_name    Name of the project"
    echo "  team_type       Agent team configuration (default: minimal)"
    echo ""
    echo "Team Types:"
    echo "  minimal     - ORCHESTRATOR, PYTHON_ML, REVIEWER"
    echo "  backend     - ORCHESTRATOR, PYTHON_ML, DEVOPS, REVIEWER"
    echo "  frontend    - ORCHESTRATOR, FLUTTER_AGENT, PYTHON_ML, REVIEWER"
    echo "  full        - All 8 agents"
    echo "  research    - ORCHESTRATOR, RESEARCHER, PYTHON_ML, REVIEWER"
    echo "  automation  - ORCHESTRATOR, N8N_AGENT, DEVOPS, PYTHON_ML"
    echo "  docs        - ORCHESTRATOR, RESEARCHER, DOCUMENTATION"
    echo ""
    echo "Examples:"
    echo "  $0 ~/projects/trading_bot \"Trading Bot\" backend"
    echo "  $0 ~/projects/ml_api \"ML API Service\" minimal"
    echo "  $0 . \"Current Project\" full"
    echo ""
    exit 0
}

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    show_help
fi

# Validate arguments
if [[ -z "$PROJECT_PATH" || -z "$PROJECT_NAME" ]]; then
    echo -e "${RED}Error: Missing required arguments${NC}"
    echo ""
    show_help
fi

# Resolve paths (macOS compatible)
if [[ "$PROJECT_PATH" != /* ]]; then
    PROJECT_PATH="$(pwd)/$PROJECT_PATH"
fi
PROJECT_PATH=$(cd "$(dirname "$PROJECT_PATH")" 2>/dev/null && pwd)/$(basename "$PROJECT_PATH") || PROJECT_PATH="$PROJECT_PATH"
PROJECT_SLUG=$(echo "$PROJECT_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '_' | tr -cd '[:alnum:]_')
DATE=$(date +%Y-%m-%d)

echo -e "${CYAN}Project Path:${NC}  $PROJECT_PATH"
echo -e "${CYAN}Project Name:${NC}  $PROJECT_NAME"
echo -e "${CYAN}Project Slug:${NC}  $PROJECT_SLUG"
echo -e "${CYAN}Team Type:${NC}     $TEAM_TYPE"
echo -e "${CYAN}Template Dir:${NC}  $TEMPLATE_DIR"
echo ""

# Confirm
read -p "Create project? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 1
fi

echo ""

# ============================================
# PHASE 1: Copy Template
# ============================================
echo -e "${GREEN}[1/8] Copying template files...${NC}"

if [[ -d "$PROJECT_PATH" && "$(ls -A $PROJECT_PATH 2>/dev/null)" ]]; then
    echo -e "${YELLOW}  Warning: Directory exists and is not empty${NC}"
    read -p "  Merge with existing? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

mkdir -p "$PROJECT_PATH"

# Copy template (excluding .git and script itself)
rsync -av --exclude='.git' --exclude='*.pyc' --exclude='__pycache__' \
    --exclude='*.db' --exclude='.DS_Store' --exclude='venv' \
    "$TEMPLATE_DIR/" "$PROJECT_PATH/"

echo -e "  ${GREEN}✓${NC} Template copied"

# ============================================
# PHASE 2: Initialize Project
# ============================================
echo -e "${GREEN}[2/8] Initializing project structure...${NC}"

cd "$PROJECT_PATH"

# Create additional directories
mkdir -p api/utils api/routes
mkdir -p knowledge_base/documents/{specs,designs,references,outputs}
mkdir -p knowledge_base/attachments/{images,pdfs,logs}
mkdir -p knowledge_base/exports
mkdir -p automation/workflows
mkdir -p infrastructure/cloud
mkdir -p cli/.claude/commands
mkdir -p app/lib
mkdir -p logs
mkdir -p data
mkdir -p tests

# Create .gitkeep files
touch knowledge_base/attachments/.gitkeep
touch knowledge_base/exports/.gitkeep
touch data/.gitkeep
touch logs/.gitkeep

echo -e "  ${GREEN}✓${NC} Directories created"

# ============================================
# PHASE 3: Generate Configuration Files
# ============================================
echo -e "${GREEN}[3/8] Generating configuration files...${NC}"

# Generate secure passwords
N8N_PASS=$(openssl rand -hex 12 2>/dev/null || echo "change_me_$(date +%s)")
POSTGRES_PASS=$(openssl rand -hex 16 2>/dev/null || echo "change_me_$(date +%s)")

# Create .env
cat > api/.env << EOF
# ============================================
# $PROJECT_NAME - Environment Configuration
# Generated: $DATE
# ============================================

# Project
PROJECT_NAME=$PROJECT_NAME
PROJECT_SLUG=$PROJECT_SLUG
VERSION=1.0.0

# API Server
API_PORT=5050
FLASK_ENV=development
LOG_LEVEL=INFO

# Database
DATABASE_PATH=./data/kb.db

# n8n Automation
N8N_PORT=5678
N8N_USER=admin
N8N_PASSWORD=$N8N_PASS
N8N_HOST=localhost

# PostgreSQL (for n8n)
POSTGRES_PASSWORD=$POSTGRES_PASS

# Redis (optional)
REDIS_PORT=6379

# Cloud/Deploy
PUBLIC_IP=localhost
TIMEZONE=UTC

# API Keys (add your keys here)
# OPENAI_API_KEY=
# ANTHROPIC_API_KEY=
# TAVILY_API_KEY=

EOF

echo -e "  ${GREEN}✓${NC} Created api/.env"

# Create .gitignore
cat > .gitignore << 'EOF'
# Environment
.env
.env.local
*.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/

# Databases
*.db
*.sqlite
*.sqlite3

# Logs
*.log
logs/

# IDE
.idea/
.vscode/
*.swp
*.swo
.DS_Store

# Build
build/
dist/
*.egg-info/

# Docker
.docker/

# Secrets
*.pem
*.key
credentials.json

# Knowledge Base
knowledge_base/attachments/*
!knowledge_base/attachments/.gitkeep
knowledge_base/exports/*
!knowledge_base/exports/.gitkeep

# Data
data/*
!data/.gitkeep

EOF

echo -e "  ${GREEN}✓${NC} Created .gitignore"

# Create VERSION
echo "1.0.0" > VERSION
echo -e "  ${GREEN}✓${NC} Created VERSION"

# ============================================
# PHASE 4: Initialize Knowledge Base
# ============================================
echo -e "${GREEN}[4/8] Initializing Knowledge Base...${NC}"

if [[ -f "knowledge_base/schema.sql" ]]; then
    sqlite3 knowledge_base/kb.db < knowledge_base/schema.sql 2>/dev/null || true

    # Set project name
    sqlite3 knowledge_base/kb.db "UPDATE kb_project SET value='$PROJECT_NAME' WHERE key='project_name';" 2>/dev/null || true

    echo -e "  ${GREEN}✓${NC} Knowledge Base initialized"
else
    echo -e "  ${YELLOW}⚠${NC} schema.sql not found, skipping KB init"
fi

# ============================================
# PHASE 5: Generate Documentation
# ============================================
echo -e "${GREEN}[5/8] Generating documentation...${NC}"

# Create CLAUDE.md
cat > CLAUDE.md << EOF
# $PROJECT_NAME

## Overview
[Add your project description here]

## Architecture
- **API**: Python Flask server (port 5050)
- **Database**: SQLite Knowledge Base
- **Automation**: n8n workflows (port 5678)
- **Agents**: Multi-agent system ($TEAM_TYPE team)

## Quick Start
\`\`\`bash
# Start services
docker-compose -f infrastructure/docker-compose.yml up -d

# Check health
curl http://localhost:5050/health

# Start agents
./agents/init_agents.sh . $TEAM_TYPE
\`\`\`

## Agent Commands
\`\`\`bash
python3 .agents/agent_tools.py register ROLE --focus "description"
python3 .agents/agent_tools.py list
python3 .agents/agent_tools.py msg send FROM TO "Subject" "Content"
\`\`\`

## Project Tools

### Agent Tools (\`python3 .agents/agent_tools.py\`)
| Command | Description |
|---------|-------------|
| \`register ROLE\` | Register as an agent |
| \`list\` | List all agents |
| \`leave ROLE\` | Leave session |
| \`status ROLE -w "..."\` | Update working status |
| \`msg list\` | List messages |
| \`msg send FROM TO "Subj" "Msg"\` | Send message |
| \`msg broadcast FROM "Subj" "Msg"\` | Broadcast to all |
| \`session start ROLE\` | Start work session |
| \`session log SID "..."\` | Log activity |
| \`session end SID "..."\` | End session |
| \`task list\` | List all tasks |
| \`task add "Title" AGENT\` | Create task |
| \`task done TASK_ID\` | Mark task done |
| \`task complete TASK_ID SID ROLE "Summary"\` | Full completion |

### Scripts (\`./scripts/\`)
| Script | Description |
|--------|-------------|
| \`complete_task.sh\` | Full 9-phase task completion |
| \`run_tests.sh\` | Run test suite |

### Claude Code Slash Commands
| Command | Description |
|---------|-------------|
| \`/tools\` | Show all project tools |
| \`/complete\` | Task completion workflow |
| \`/status\` | Project status overview |
| \`/agent\` | Agent management |
| \`/session\` | Session management |
| \`/task\` | Task management |
| \`/msg\` | Messaging commands |
| \`/sync\` | Sync operations |
| \`/backup\` | Backup commands |

## Directory Structure
\`\`\`
$PROJECT_SLUG/
├── api/                 # Python API
├── .agents/             # Agent system
├── .claude/             # Claude Code integration
│   ├── commands/        # Slash commands
│   └── settings.json    # Permissions
├── knowledge_base/      # Project KB
├── infrastructure/      # Docker & cloud
├── skills/              # Reusable patterns
├── docs/                # Documentation
├── scripts/             # Utility scripts
└── tests/               # Test suite
\`\`\`

## Conventions
- Python: Type hints, docstrings required
- API: RESTful endpoints, JSON responses
- Git: Conventional commits (feat:, fix:, docs:)

---

## Claude Code Rules (PRODUCTION MODE)

### Core Rules
- **FULL CODE**: Always provide production-ready code in ONE SHOT
- **PRESERVE**: Keep all existing working code, naming, structures
- **COMPLETE**: Include ALL imports, dependencies, configs
- **NO PLACEHOLDERS**: Code must be complete and functional

### Special Commands
| Command | Action |
|---------|--------|
| \`[FULL_REBUILD]\` | Complete project generation |
| \`[FIX_ERRORS]\` | Surgical error correction |
| \`[PRESERVE_ENHANCE]\` | Improve without breaking |
| \`[PRODUCTION_MODE]\` | Apply all rules maximally |

### Output Format
1. Folder structure (tree)
2. Complete file contents
3. Configuration files
4. Environment setup
5. Documentation
6. Setup instructions

### Prohibitions
- ❌ No samples/snippets (full code only)
- ❌ No placeholders
- ❌ No modifying working code without permission
- ❌ No simplified versions

See \`agents/prompts/CLAUDE_CODE_RULES.md\` for complete rules.

---

## Generated
- Date: $DATE
- Template: Fokha Project Template v2.0
- Team: $TEAM_TYPE
- Claude Code Rules: v3.2

EOF

echo -e "  ${GREEN}✓${NC} Created CLAUDE.md"

# Create README.md
cat > README.md << EOF
# $PROJECT_NAME

> [Add your project tagline here]

## Quick Start

\`\`\`bash
# Start services
docker-compose -f infrastructure/docker-compose.yml up -d

# Verify
curl http://localhost:5050/health
\`\`\`

## Documentation

- [Development Guide](docs/DEV_GUIDE.md)
- [Project Structure](docs/PROJECT_STRUCTURE.md)
- [API Reference](docs/API_REFERENCE.md)

## Agent System

This project uses a multi-agent system. See [CLAUDE.md](CLAUDE.md) for details.

---

Generated from Fokha Project Template on $DATE
EOF

echo -e "  ${GREEN}✓${NC} Created README.md"

# ============================================
# PHASE 6: Initialize Agent System
# ============================================
echo -e "${GREEN}[6/8] Initializing agent system...${NC}"

chmod +x scripts/*.sh 2>/dev/null || true
chmod +x agents/*.sh 2>/dev/null || true

# Run agent initialization (non-interactive)
if [[ -f "agents/init_agents.sh" ]]; then
    # Initialize without launching tmux
    mkdir -p .agents/sessions .agents/logs

    # Create agent database
    if [[ -f "knowledge_base/schema.sql" ]]; then
        # Use embedded schema for agents
        sqlite3 .agents/project_kb.db "
            CREATE TABLE IF NOT EXISTS agents (
                agent_id TEXT PRIMARY KEY,
                role TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                focus TEXT,
                working_on TEXT,
                session_start DATETIME,
                last_heartbeat DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                role TEXT,
                started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                ended_at DATETIME,
                status TEXT DEFAULT 'active',
                summary TEXT
            );
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT UNIQUE,
                from_agent TEXT NOT NULL,
                to_agent TEXT,
                subject TEXT,
                content TEXT,
                message_type TEXT DEFAULT 'notification',
                is_read INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                status TEXT DEFAULT 'open',
                priority TEXT DEFAULT 'medium',
                assigned_to TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        " 2>/dev/null || true
    fi

    echo -e "  ${GREEN}✓${NC} Agent database created"
    echo -e "  ${GREEN}✓${NC} Run './agents/init_agents.sh . $TEAM_TYPE' to launch agents"
else
    echo -e "  ${YELLOW}⚠${NC} init_agents.sh not found"
fi

# ============================================
# PHASE 7: Claude Code Integration
# ============================================
echo -e "${GREEN}[7/8] Setting up Claude Code integration...${NC}"

# Create .claude directory if it doesn't exist
mkdir -p .claude/commands

# Create settings.json for Claude Code
cat > .claude/settings.json << 'CLAUDE_SETTINGS'
{
  "permissions": {
    "allow": [
      "Bash(python3 .agents/*)",
      "Bash(./scripts/*)",
      "Bash(git *)",
      "Bash(pytest *)",
      "Read(.agents/*)",
      "Read(scripts/*)",
      "Read(docs/*)",
      "Write(.agents/sessions/*)",
      "Write(tests/*)",
      "Write(CHANGELOG.md)"
    ],
    "deny": []
  },
  "env": {
    "PROJECT_TYPE": "fokha-template",
    "AGENT_TOOLS": ".agents/agent_tools.py"
  }
}
CLAUDE_SETTINGS

# Create tools command
cat > .claude/commands/tools.md << 'TOOLS_CMD'
# Project Tools Index

## Agent Tools (python3 .agents/agent_tools.py)

| Command | Description |
|---------|-------------|
| `register ROLE` | Register as an agent |
| `list` | List all agents |
| `leave ROLE` | Leave session |
| `status ROLE -w "..."` | Update working status |
| `msg list` | List messages |
| `msg send FROM TO "Subj" "Msg"` | Send message |
| `msg broadcast FROM "Subj" "Msg"` | Broadcast to all |
| `session start ROLE` | Start work session |
| `session log SID "..."` | Log activity |
| `session end SID "..."` | End session |
| `task list` | List all tasks |
| `task add "Title" AGENT` | Create task |
| `task done TASK_ID` | Mark task done |
| `task complete TASK_ID SID ROLE "Summary"` | Full completion |

## Scripts (./scripts/)

| Script | Description |
|--------|-------------|
| `complete_task.sh` | Full 9-phase task completion |
| `run_tests.sh` | Run test suite |

## Quick Start

```bash
# Register and start session
python3 .agents/agent_tools.py register ROLE --focus "My focus"
python3 .agents/agent_tools.py session start ROLE
# Save the SESSION_ID as $SID

# Complete task
./scripts/complete_task.sh TASK_ID $SID ROLE "Summary"

# End session
python3 .agents/agent_tools.py session end $SID "Done"
python3 .agents/agent_tools.py leave ROLE --summary "Done"
```
TOOLS_CMD

# Create complete command
cat > .claude/commands/complete.md << 'COMPLETE_CMD'
# Task Completion Command

Complete a task with full workflow:

```bash
./scripts/complete_task.sh TASK_ID SESSION_ID ROLE "Summary"
```

Options:
- `--skip-tests` - Skip test generation
- `--skip-git` - Skip git operations
- `--skip-backup` - Skip backup
- `--skip-sync` - Skip sync operations

Quick version:
```bash
python3 .agents/agent_tools.py task complete TASK_ID SESSION_ID ROLE "Summary"
```
COMPLETE_CMD

# Create status command
cat > .claude/commands/status.md << 'STATUS_CMD'
# Project Status

Get project status:

```bash
# Agents
python3 .agents/agent_tools.py list

# Tasks
python3 .agents/agent_tools.py task list

# Messages
python3 .agents/agent_tools.py msg list

# Git
git status
git log --oneline -5
```
STATUS_CMD

echo -e "  ${GREEN}✓${NC} Claude Code commands created"
echo -e "  ${GREEN}✓${NC} Use /tools, /complete, /status in Claude Code"

# ============================================
# PHASE 8: Governance Integration
# ============================================
echo -e "${GREEN}[8/8] Setting up governance framework...${NC}"

# Create governance directory structure
mkdir -p .governance/scripts
mkdir -p .governance/docs/process/adr
mkdir -p .governance/docs/ai
mkdir -p .governance/docs/metrics

# Create governance config
cat > guidelines-config.yaml << 'GOV_CONFIG'
# Governance Configuration
# Profile: standard (adjust thresholds as needed)

project_name: "${PROJECT_NAME}"
enable_localization_audit: false
supported_locales: [en]

audit:
  hardcoded_string_threshold: 100
  provider_duplicate_fail: false
  require_navigation_keys: false
  fail_on_unlocalized_new_keys: false
  enforce_session_log_entry: true

drift:
  enforce: false
  ignore:
    - docs/process/session_log.md
    - docs/process/adr

metrics:
  enable_analyzer_trend: false
  export_metrics_json: true
  metrics_output: .governance/docs/metrics/metrics.json

ai_context:
  include_sections:
    - architecture
    - session_log_tail
GOV_CONFIG

# Create run_audit.sh script
cat > .governance/scripts/run_audit.sh << 'AUDIT_SCRIPT'
#!/usr/bin/env bash
# Governance Audit Runner
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

echo "=== Governance Audit ==="
echo ""

FAILURES=0

# Check for uncommitted changes
echo "[1/4] Checking git status..."
if [[ -n "$(git status --porcelain 2>/dev/null)" ]]; then
    echo "  ⚠ Uncommitted changes detected"
else
    echo "  ✓ Working tree clean"
fi

# Check session log
echo "[2/4] Checking session log..."
if [[ -f ".governance/docs/process/session_log.md" ]]; then
    ENTRIES=$(grep -c "^## " .governance/docs/process/session_log.md 2>/dev/null || echo "0")
    echo "  ✓ Session log exists ($ENTRIES entries)"
else
    echo "  ⚠ No session log found"
fi

# Check ADRs
echo "[3/4] Checking ADRs..."
ADR_COUNT=$(find .governance/docs/process/adr -name "ADR-*.md" 2>/dev/null | wc -l | tr -d ' ')
echo "  ✓ Found $ADR_COUNT ADR(s)"

# Check tests
echo "[4/4] Checking tests..."
if [[ -d "tests" ]]; then
    TEST_COUNT=$(find tests -name "test_*.py" -o -name "*_test.py" 2>/dev/null | wc -l | tr -d ' ')
    echo "  ✓ Found $TEST_COUNT test file(s)"
else
    echo "  ⚠ No tests directory"
fi

echo ""
if [[ $FAILURES -eq 0 ]]; then
    echo "✅ Audit passed"
    exit 0
else
    echo "❌ Audit failed with $FAILURES issue(s)"
    exit 1
fi
AUDIT_SCRIPT
chmod +x .governance/scripts/run_audit.sh

# Create session log template
cat > .governance/docs/process/session_log.md << 'SESSION_LOG'
# Session Log

Track AI-assisted development sessions for continuity.

---

## $(date +%Y-%m-%d) - Project Initialization

**Agent**: ORCHESTRATOR
**Duration**: ~30 min
**Summary**: Project created from Fokha template

### Completed
- Project structure created
- Agent system initialized
- Governance framework set up

### Next Steps
- Configure project-specific settings
- Create initial ADR for architecture decisions
- Begin feature development

---
SESSION_LOG

# Create ADR template
cat > .governance/docs/process/adr/ADR-TEMPLATE.md << 'ADR_TEMPLATE'
# ADR-XXXX: [Title]

**Status**: Proposed | Accepted | Deprecated | Superseded
**Date**: YYYY-MM-DD
**Authors**: [Names]

## Context

[What is the issue or situation that requires a decision?]

## Decision

[What is the decision that was made?]

## Alternatives Considered

1. **Alternative A**: [Description]
   - Pros: ...
   - Cons: ...

2. **Alternative B**: [Description]
   - Pros: ...
   - Cons: ...

## Consequences

### Positive
- [Benefit 1]
- [Benefit 2]

### Negative
- [Tradeoff 1]
- [Tradeoff 2]

## References

- [Link to relevant docs]
ADR_TEMPLATE

# Create AI bootstrap template
cat > .governance/docs/ai/AI_BOOTSTRAP.md << 'AI_BOOTSTRAP'
# AI Session Bootstrap

Use this template to initialize AI chat sessions with project context.

## Project Overview

**Name**: ${PROJECT_NAME}
**Type**: Multi-agent system with Knowledge Base
**Stack**: Python API + SQLite + Docker

## Architecture

```
project/
├── api/              # Python Flask API
├── .agents/          # Agent system & tools
├── .governance/      # Governance framework
├── knowledge_base/   # SQLite KB
├── infrastructure/   # Docker configs
└── scripts/          # Automation
```

## Key Commands

```bash
# Agent tools
python3 .agents/agent_tools.py [command]

# Governance audit
./.governance/scripts/run_audit.sh

# Task completion
./scripts/complete_task.sh TASK_ID SID ROLE "Summary"
```

## Current Focus

[Update with current sprint/milestone goals]

## Recent Sessions

[See session_log.md for history]
AI_BOOTSTRAP

# Create metrics placeholder
cat > .governance/docs/metrics/metrics.json << 'METRICS'
{
  "project": "${PROJECT_NAME}",
  "created": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "metrics": {
    "files": 0,
    "tests": 0,
    "adrs": 0,
    "sessions": 1
  }
}
METRICS

# Add governance commands to Claude Code
cat > .claude/commands/audit.md << 'AUDIT_CMD'
# Governance Audit

Run the governance audit:

```bash
./.governance/scripts/run_audit.sh
```

## What It Checks

1. **Git Status** - Uncommitted changes
2. **Session Log** - AI session tracking
3. **ADRs** - Architecture decisions
4. **Tests** - Test coverage

## Quick Fixes

```bash
# Update session log
echo "## $(date +%Y-%m-%d) - Session" >> .governance/docs/process/session_log.md

# Create ADR
cp .governance/docs/process/adr/ADR-TEMPLATE.md .governance/docs/process/adr/ADR-0001-title.md
```
AUDIT_CMD

cat > .claude/commands/adr.md << 'ADR_CMD'
# Architecture Decision Records

## Create New ADR

```bash
# Copy template
cp .governance/docs/process/adr/ADR-TEMPLATE.md \
   .governance/docs/process/adr/ADR-XXXX-slug.md

# Edit the new ADR
nano .governance/docs/process/adr/ADR-XXXX-slug.md
```

## List ADRs

```bash
ls -la .governance/docs/process/adr/
```

## ADR Status Flow

```
Proposed → Accepted → [Deprecated | Superseded]
```

## Template Sections

- **Context**: Why is this decision needed?
- **Decision**: What was decided?
- **Alternatives**: What else was considered?
- **Consequences**: Pros and cons
ADR_CMD

cat > .claude/commands/session-log.md << 'SESSLOG_CMD'
# Session Log Management

## Add Entry

```bash
cat >> .governance/docs/process/session_log.md << 'EOF'

## $(date +%Y-%m-%d) - [Session Title]

**Agent**: [ROLE]
**Duration**: ~X hours
**Summary**: [Brief description]

### Completed
- [Task 1]
- [Task 2]

### Next Steps
- [Todo 1]
- [Todo 2]

---
EOF
```

## View Recent Sessions

```bash
tail -50 .governance/docs/process/session_log.md
```

## Session Log Purpose

- Track AI-assisted development
- Maintain continuity across sessions
- Document decisions and progress
- Enable handoffs between agents
SESSLOG_CMD

cat > .claude/commands/metrics.md << 'METRICS_CMD'
# Project Metrics

## Export Metrics

```bash
# Count files
FILES=$(find . -type f -name "*.py" | wc -l)

# Count tests
TESTS=$(find tests -name "test_*.py" 2>/dev/null | wc -l)

# Count ADRs
ADRS=$(find .governance/docs/process/adr -name "ADR-*.md" 2>/dev/null | wc -l)

# Update metrics.json
cat > .governance/docs/metrics/metrics.json << EOF
{
  "updated": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "metrics": {
    "files": $FILES,
    "tests": $TESTS,
    "adrs": $ADRS
  }
}
EOF
```

## View Metrics

```bash
cat .governance/docs/metrics/metrics.json | python3 -m json.tool
```
METRICS_CMD

cat > .claude/commands/drift.md << 'DRIFT_CMD'
# Governance Drift Check

## Check for Drift

```bash
# Compare local governance with template
diff -r .governance/ /path/to/governance-kit/.governance/ 2>/dev/null | head -50
```

## Verify Integrity

```bash
# Check required files exist
for f in guidelines-config.yaml .governance/scripts/run_audit.sh .governance/docs/process/session_log.md; do
    [[ -f "$f" ]] && echo "✓ $f" || echo "✗ $f MISSING"
done
```

## Update Governance

```bash
# If using git subtree
git subtree pull --prefix .governance <governance-kit-url> main --squash
```
DRIFT_CMD

echo -e "  ${GREEN}✓${NC} Governance framework created"
echo -e "  ${GREEN}✓${NC} Use /audit, /adr, /session-log in Claude Code"

# ============================================
# Summary
# ============================================
echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}           ${GREEN}✓ PROJECT CREATED SUCCESSFULLY${NC}                      ${BLUE}║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Project:${NC}  $PROJECT_NAME"
echo -e "${CYAN}Location:${NC} $PROJECT_PATH"
echo -e "${CYAN}Team:${NC}     $TEAM_TYPE"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo ""
echo "  1. Navigate to project:"
echo -e "     ${GREEN}cd $PROJECT_PATH${NC}"
echo ""
echo "  2. Edit configuration:"
echo -e "     ${GREEN}nano api/.env${NC}"
echo ""
echo "  3. Update project description:"
echo -e "     ${GREEN}nano CLAUDE.md${NC}"
echo ""
echo "  4. Start services:"
echo -e "     ${GREEN}docker-compose -f infrastructure/docker-compose.yml up -d${NC}"
echo ""
echo "  5. Launch agents (optional):"
echo -e "     ${GREEN}./agents/init_agents.sh . $TEAM_TYPE${NC}"
echo ""
echo "  6. Verify:"
echo -e "     ${GREEN}curl http://localhost:5050/health${NC}"
echo ""
echo -e "${CYAN}Documentation:${NC}"
echo "  - Workflow:  docs/NEW_PROJECT_WORKFLOW.md"
echo "  - Agents:    agents/AGENT_SYSTEM.md"
echo "  - Skills:    skills/SKILLS_INDEX.md"
echo ""
echo -e "${CYAN}Claude Code:${NC}"
echo "  - Commands:  /tools, /complete, /status, /agent"
echo "  - Settings:  .claude/settings.json"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
