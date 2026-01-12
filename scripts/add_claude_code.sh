#!/bin/bash

# ============================================
# ADD CLAUDE CODE INTEGRATION TO EXISTING PROJECT
# Usage: ./add_claude_code.sh [project_path]
# ============================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Get project path (default: current directory)
PROJECT_PATH="${1:-.}"
PROJECT_PATH=$(realpath "$PROJECT_PATH")

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║           ADD CLAUDE CODE INTEGRATION v1.0                    ║"
echo "║           Add Claude Code skills to existing projects         ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${CYAN}Project:${NC} $PROJECT_PATH"
echo ""

# Check if project exists
if [[ ! -d "$PROJECT_PATH" ]]; then
    echo -e "${RED}Error: Directory does not exist: $PROJECT_PATH${NC}"
    exit 1
fi

cd "$PROJECT_PATH"

# Check if .claude already exists
if [[ -d ".claude" ]]; then
    echo -e "${YELLOW}Warning: .claude directory already exists${NC}"
    read -p "Overwrite? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 0
    fi
    rm -rf .claude
fi

echo -e "${GREEN}[1/4] Creating .claude directory structure...${NC}"
mkdir -p .claude/commands

echo -e "${GREEN}[2/4] Creating settings.json...${NC}"
cat > .claude/settings.json << 'SETTINGS'
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
SETTINGS
echo -e "  ${GREEN}✓${NC} settings.json"

echo -e "${GREEN}[3/4] Creating slash commands...${NC}"

# /tools command
cat > .claude/commands/tools.md << 'CMD'
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
CMD
echo -e "  ${GREEN}✓${NC} /tools"

# /complete command
cat > .claude/commands/complete.md << 'CMD'
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

## 9-Phase Workflow

1. **Pre-verification** - Verify task completion
2. **Test generation** - Create/update tests
3. **Git operations** - Commit changes
4. **Database updates** - Update task status
5. **CHANGELOG** - Update changelog
6. **Notification** - Notify team
7. **Backup** - Create backup
8. **Sync** - Push to remote/cloud
9. **Report** - Generate completion report
CMD
echo -e "  ${GREEN}✓${NC} /complete"

# /status command
cat > .claude/commands/status.md << 'CMD'
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

# Sessions
python3 .agents/agent_tools.py session list
```

## Quick Status Check

```bash
# One-liner status
echo "=== AGENTS ===" && python3 .agents/agent_tools.py list 2>/dev/null || echo "No agents" && \
echo "=== TASKS ===" && python3 .agents/agent_tools.py task list 2>/dev/null || echo "No tasks" && \
echo "=== GIT ===" && git status -s 2>/dev/null || echo "Not a git repo"
```
CMD
echo -e "  ${GREEN}✓${NC} /status"

# /agent command
cat > .claude/commands/agent.md << 'CMD'
# Agent Management

## Register
```bash
python3 .agents/agent_tools.py register ROLE --focus "My focus area"
```

## List Agents
```bash
python3 .agents/agent_tools.py list
```

## Update Status
```bash
python3 .agents/agent_tools.py status ROLE -w "Currently working on X"
```

## Leave Session
```bash
python3 .agents/agent_tools.py leave ROLE --summary "Completed X, Y, Z"
```

## Available Roles
- ORCHESTRATOR - Project coordination
- PYTHON_ML - Python/ML development
- FLUTTER_AGENT - Flutter/Dart development
- DEVOPS - Infrastructure/deployment
- REVIEWER - Code review
- RESEARCHER - Research tasks
- N8N_AGENT - Workflow automation
- DOCUMENTATION - Documentation
CMD
echo -e "  ${GREEN}✓${NC} /agent"

# /session command
cat > .claude/commands/session.md << 'CMD'
# Session Management

## Start Session
```bash
python3 .agents/agent_tools.py session start ROLE
# Returns SESSION_ID - save this!
```

## Log Activity
```bash
python3 .agents/agent_tools.py session log SESSION_ID "Completed feature X"
```

## End Session
```bash
python3 .agents/agent_tools.py session end SESSION_ID "Session summary"
```

## List Sessions
```bash
python3 .agents/agent_tools.py session list
```

## View Session
```bash
python3 .agents/agent_tools.py session view SESSION_ID
```
CMD
echo -e "  ${GREEN}✓${NC} /session"

# /task command
cat > .claude/commands/task.md << 'CMD'
# Task Management

## List Tasks
```bash
python3 .agents/agent_tools.py task list
python3 .agents/agent_tools.py task list --status open
python3 .agents/agent_tools.py task list --assigned-to ROLE
```

## Create Task
```bash
python3 .agents/agent_tools.py task add "Task title" ASSIGNED_ROLE
python3 .agents/agent_tools.py task add "Task title" ROLE --priority high
```

## Update Task
```bash
python3 .agents/agent_tools.py task update TASK_ID --status in_progress
python3 .agents/agent_tools.py task done TASK_ID
```

## Complete Task (Full Workflow)
```bash
python3 .agents/agent_tools.py task complete TASK_ID SESSION_ID ROLE "Summary"
# Or use the full script:
./scripts/complete_task.sh TASK_ID SESSION_ID ROLE "Summary"
```
CMD
echo -e "  ${GREEN}✓${NC} /task"

# /msg command
cat > .claude/commands/msg.md << 'CMD'
# Messaging Commands

## List Messages
```bash
python3 .agents/agent_tools.py msg list
python3 .agents/agent_tools.py msg list --unread
```

## Send Message
```bash
python3 .agents/agent_tools.py msg send FROM_ROLE TO_ROLE "Subject" "Message content"
```

## Broadcast to All
```bash
python3 .agents/agent_tools.py msg broadcast FROM_ROLE "Subject" "Message to all agents"
```

## Read Message
```bash
python3 .agents/agent_tools.py msg read MESSAGE_ID
```

## Message Types
- `notification` - General notification
- `request` - Action request
- `response` - Reply to request
- `alert` - Important alert
CMD
echo -e "  ${GREEN}✓${NC} /msg"

# /sync command
cat > .claude/commands/sync.md << 'CMD'
# Sync Operations

## Git Push
```bash
git push origin $(git branch --show-current)
```

## Cloud Sync (if configured)
```bash
# Sync to cloud server
rsync -avz --exclude='venv' --exclude='__pycache__' \
  ./ user@server:/path/to/project/
```

## SD Card Sync (if available)
```bash
# Check if SD card mounted
if [[ -d "/Volumes/ArkOS" ]]; then
    rsync -avz --exclude='venv' --exclude='__pycache__' \
      ./ /Volumes/ArkOS/backup/$(basename $PWD)/
fi
```

## Full Sync (all targets)
```bash
./scripts/complete_task.sh TASK_ID SID ROLE "Summary"
# Includes sync phase automatically
```
CMD
echo -e "  ${GREEN}✓${NC} /sync"

# /backup command
cat > .claude/commands/backup.md << 'CMD'
# Backup Commands

## Quick Backup
```bash
# Create timestamped backup
BACKUP_DIR=".agents/backups"
mkdir -p "$BACKUP_DIR"
tar -czf "$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).tar.gz" \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='node_modules' \
    --exclude='.git' \
    --exclude='*.pyc' \
    .
```

## Backup Specific Files
```bash
# Backup databases and configs
tar -czf backup_critical.tar.gz \
    .agents/*.db \
    knowledge_base/*.db \
    *.json \
    .env* 2>/dev/null || true
```

## List Backups
```bash
ls -la .agents/backups/
```

## Restore from Backup
```bash
tar -xzf .agents/backups/backup_YYYYMMDD_HHMMSS.tar.gz
```
CMD
echo -e "  ${GREEN}✓${NC} /backup"

echo -e "${GREEN}[4/4] Verifying installation...${NC}"

# Count created files
CMD_COUNT=$(ls -1 .claude/commands/*.md 2>/dev/null | wc -l | tr -d ' ')
echo -e "  ${GREEN}✓${NC} Created $CMD_COUNT slash commands"

# Summary
echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}           ${GREEN}✓ CLAUDE CODE INTEGRATION ADDED${NC}                     ${BLUE}║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Available Slash Commands:${NC}"
echo "  /tools    - Project tools index"
echo "  /complete - Task completion workflow"
echo "  /status   - Project status overview"
echo "  /agent    - Agent management"
echo "  /session  - Session management"
echo "  /task     - Task management"
echo "  /msg      - Messaging commands"
echo "  /sync     - Sync operations"
echo "  /backup   - Backup commands"
echo ""
echo -e "${CYAN}Settings:${NC} .claude/settings.json"
echo ""
echo -e "${YELLOW}Note:${NC} Ensure your project has .agents/agent_tools.py"
echo "      and scripts/complete_task.sh for full functionality."
echo ""
echo -e "${GREEN}Done!${NC}"
