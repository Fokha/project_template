#!/usr/bin/env bash
# ============================================================
# PROJECT AGENT INITIALIZER
# Creates agent infrastructure for any project
# Usage: ./init_agents.sh [project_path] [team_type]
# ============================================================

set -e

# Default values
PROJECT_PATH="${1:-$(pwd)}"
TEAM_TYPE="${2:-minimal}"
SESSION_NAME="agents-$(basename $PROJECT_PATH)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Team configurations (simple function-based approach for compatibility)
get_team() {
    case "$1" in
        full)       echo "ORCHESTRATOR PYTHON_ML MQL5_AGENT FLUTTER_AGENT N8N_AGENT DEVOPS INFRASTRUCTURE RESEARCHER REVIEWER" ;;
        backend)    echo "ORCHESTRATOR PYTHON_ML DEVOPS REVIEWER" ;;
        frontend)   echo "ORCHESTRATOR FLUTTER_AGENT PYTHON_ML REVIEWER" ;;
        research)   echo "ORCHESTRATOR RESEARCHER PYTHON_ML REVIEWER" ;;
        automation) echo "ORCHESTRATOR N8N_AGENT DEVOPS PYTHON_ML" ;;
        infra)      echo "ORCHESTRATOR INFRASTRUCTURE DEVOPS PYTHON_ML" ;;
        minimal)    echo "ORCHESTRATOR PYTHON_ML REVIEWER" ;;
        docs)       echo "ORCHESTRATOR RESEARCHER DOCUMENTATION" ;;
        custom)     echo "" ;;
        *)          echo "ORCHESTRATOR PYTHON_ML REVIEWER" ;;
    esac
}

# Role emojis (simple function-based approach)
get_emoji() {
    case "$1" in
        ORCHESTRATOR)   echo "🎯" ;;
        PYTHON_ML)      echo "🐍" ;;
        MQL5_AGENT)     echo "📊" ;;
        FLUTTER_AGENT)  echo "📱" ;;
        N8N_AGENT)      echo "⚡" ;;
        DEVOPS)         echo "🚀" ;;
        INFRASTRUCTURE) echo "🏗️" ;;
        RESEARCHER)     echo "🔬" ;;
        REVIEWER)       echo "👁️" ;;
        DOCUMENTATION)  echo "📚" ;;
        DESIGNER)       echo "🎨" ;;
        TESTER)         echo "🧪" ;;
        CLOUD)          echo "☁️" ;;
        *)              echo "🤖" ;;
    esac
}

show_help() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  PROJECT AGENT INITIALIZER${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Usage: $0 [project_path] [team_type]"
    echo ""
    echo "Team Types:"
    echo "  full       - All 9 standard agents"
    echo "  backend    - ORCHESTRATOR, PYTHON_ML, DEVOPS, REVIEWER"
    echo "  frontend   - ORCHESTRATOR, FLUTTER_AGENT, PYTHON_ML, REVIEWER"
    echo "  research   - ORCHESTRATOR, RESEARCHER, PYTHON_ML, REVIEWER"
    echo "  automation - ORCHESTRATOR, N8N_AGENT, DEVOPS, PYTHON_ML"
    echo "  infra      - ORCHESTRATOR, INFRASTRUCTURE, DEVOPS, PYTHON_ML"
    echo "  minimal    - ORCHESTRATOR, PYTHON_ML, REVIEWER"
    echo "  docs       - ORCHESTRATOR, RESEARCHER, DOCUMENTATION"
    echo "  custom     - Specify custom agents as arguments"
    echo ""
    echo "Examples:"
    echo "  $0 /path/to/project backend"
    echo "  $0 . minimal"
    echo "  $0 /path/to/project custom PYTHON_ML DOCUMENTATION TESTER"
    echo ""
    exit 0
}

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    show_help
fi

# Setup project agent directory
setup_project() {
    echo -e "${GREEN}Setting up agent infrastructure in: $PROJECT_PATH${NC}"

    mkdir -p "$PROJECT_PATH/.agents"
    mkdir -p "$PROJECT_PATH/.agents/sessions"
    mkdir -p "$PROJECT_PATH/.agents/logs"

    # Create project-specific KB database if not exists
    if [[ ! -f "$PROJECT_PATH/.agents/project_kb.db" ]]; then
        sqlite3 "$PROJECT_PATH/.agents/project_kb.db" "
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
                summary TEXT,
                tasks_completed TEXT,
                files_modified TEXT
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
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                agent_id TEXT,
                action TEXT,
                details TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        "
        echo -e "${GREEN}  Created project KB database${NC}"
    fi

    # Create project quick prompt
    create_project_prompt
}

create_project_prompt() {
    local PROJECT_NAME=$(basename "$PROJECT_PATH")

    cat > "$PROJECT_PATH/.agents/QUICK_PROMPT.md" << 'PROMPT_EOF'
# Project Agent Quick Prompt

You are joining a multi-agent team for this project.

## YOUR IDENTITY
- **You are:** [YOUR_ROLE] Agent
- **Project:** This project directory
- **Session:** Active after registration
- **Remember:** You are an AI agent with a specific role. Stay focused on your responsibilities.

## FIRST: REGISTER YOURSELF

```bash
# Register with your assigned role
python3 .agents/agent_tools.py register YOUR_ROLE --focus "Your specialization"

# Start logging session
python3 .agents/agent_tools.py session start YOUR_ROLE
# SAVE THE SESSION ID! export SID=SESS-XXXX-XXXXXX

# Check messages from other agents
python3 .agents/agent_tools.py msg list

# See who else is working
python3 .agents/agent_tools.py list
```

## QUICK COMMANDS

### Agent Management
```bash
python3 .agents/agent_tools.py register ROLE         # Register
python3 .agents/agent_tools.py list                  # List agents
python3 .agents/agent_tools.py status ROLE -w "task" # Update status
python3 .agents/agent_tools.py leave ROLE            # End session
```

### Messaging
```bash
python3 .agents/agent_tools.py msg list              # List messages
python3 .agents/agent_tools.py msg send FROM TO "Subject" "Content"
python3 .agents/agent_tools.py msg broadcast FROM "Subject" "Content"
```

### Session Logging
```bash
python3 .agents/agent_tools.py session start ROLE    # Start session
python3 .agents/agent_tools.py session log SID "What I did"
python3 .agents/agent_tools.py session end SID "Summary"
```

### Task Management
```bash
python3 .agents/agent_tools.py task list             # List all tasks
python3 .agents/agent_tools.py task add "Task" ROLE  # Create & assign task
python3 .agents/agent_tools.py task done TASK_ID     # Mark task complete (simple)
python3 .agents/agent_tools.py task assign TASK_ID ROLE  # Reassign task
python3 .agents/agent_tools.py task complete TASK_ID SID ROLE "Summary"  # Full completion flow
```

## PRE-DEPLOYMENT CHECKLIST (CRITICAL!)

### Before ANY Code Changes:
1. **Check existing work** - Avoid duplicating what others did:
   ```bash
   # Check recent messages
   python3 .agents/agent_tools.py msg list

   # Check what other agents are working on
   python3 .agents/agent_tools.py list

   # Check recent sessions for similar work
   python3 .agents/agent_tools.py session list

   # Check git log for recent changes
   git log --oneline -20

   # Search for existing implementations
   grep -r "function_name" --include="*.py"
   ```

2. **Check task status** - Don't work on completed tasks:
   ```bash
   python3 .agents/agent_tools.py task list
   ```

3. **Claim your task** - Prevent others from duplicating:
   ```bash
   python3 .agents/agent_tools.py status YOUR_ROLE -w "Working on: [task]"
   python3 .agents/agent_tools.py msg broadcast YOUR_ROLE "Starting Task" "I am working on [task]. Do not duplicate."
   ```

### Before Deploying/Committing:
1. **Run tests:** `pytest` or project-specific test command
2. **Check for conflicts:** `git status && git diff`
3. **Review changes:** Ensure no duplicate code added
4. **Update docs:** CHANGELOG.md, relevant documentation

## TASK TRACKING & ASSIGNMENT

### When You Complete a Task:
```bash
# RECOMMENDED: Use the unified complete command (does all 4 steps in one):
python3 .agents/agent_tools.py task complete TASK_ID $SID YOUR_ROLE "Brief summary"

# OR use scripts/complete_task.sh for extended flow with verification:
./scripts/complete_task.sh TASK_ID $SID YOUR_ROLE "Brief summary"

# MANUAL STEPS (if needed):
# 1. Mark task done
python3 .agents/agent_tools.py task done TASK_ID

# 2. Log completion
python3 .agents/agent_tools.py session log $SID "Completed: [task description]"

# 3. Broadcast to team
python3 .agents/agent_tools.py msg broadcast YOUR_ROLE "Task Complete" "Completed TASK_ID"

# 4. If new tasks discovered, create and assign them:
python3 .agents/agent_tools.py task add "New task description" TARGET_AGENT
```

### Task Assignment Rules:
| Task Type | Assign To |
|-----------|-----------|
| Python/ML/API | PYTHON_ML |
| Flutter/Mobile | FLUTTER_AGENT |
| MQL5/Trading EA | MQL5_AGENT |
| N8N/Automation | N8N_AGENT |
| Cloud/Deploy | DEVOPS |
| Documentation | DOCUMENTATION |
| Testing/QA | TESTER or REVIEWER |
| Research | RESEARCHER |
| Unclear | ORCHESTRATOR (for delegation) |

## VERSION & RELEASE MANAGEMENT

### Semantic Versioning (MAJOR.MINOR.PATCH)
- **MAJOR:** Breaking changes, incompatible API changes
- **MINOR:** New features, backward compatible
- **PATCH:** Bug fixes, minor improvements

### Before Making Changes
1. Check current version: `cat VERSION` or `grep version package.json`
2. Decide version bump based on change type
3. Update version in relevant files

### Changelog Format (CHANGELOG.md)
```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New feature description

### Changed
- Modified behavior description

### Fixed
- Bug fix description

### Removed
- Removed feature description

### Security
- Security fix description
```

### Release Checklist
1. Update VERSION file
2. Update CHANGELOG.md with all changes
3. Update version in code files (package.json, setup.py, etc.)
4. Create git tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
5. Push with tags: `git push origin main --tags`
6. Notify team via message

### Version Commands
```bash
# Create/update VERSION file
echo "1.2.3" > VERSION

# Git tag for release
git tag -a v1.2.3 -m "Release v1.2.3: Description"

# View all tags
git tag -l
```

## CONTEXT MANAGEMENT (CRITICAL!)

### At ~10% Context Remaining:
Run `/compact` to free up context while preserving history.

### At ~5% Context Remaining - CREATE HANDOFF REPORT:
Before compacting, create a continuation report:

```markdown
# HANDOFF REPORT - [YOUR_ROLE] - [DATE]

## Session Summary
- Session ID: [SID]
- Started: [time]
- Context used: ~95%

## Work Completed
1. [Task 1 - DONE]
2. [Task 2 - DONE]
3. [Task 3 - IN PROGRESS]

## Current State
- Working on: [specific task]
- Files modified: [list]
- Pending changes: [unsaved work]

## Next Steps (CONTINUE FROM HERE)
1. [Immediate next action]
2. [Following action]
3. [Remaining tasks]

## Key Context to Preserve
- [Important decision made]
- [Critical info discovered]
- [Dependencies to remember]

## Continuation Prompt
"Continue as [ROLE] agent. Previous session completed: [summary].
Next: [specific next step]. Key context: [critical info]."
```

### Save Report Before Compact:
```bash
# Log the handoff
python3 .agents/agent_tools.py session log $SID "Creating handoff report at 5% context"

# Save to file
echo "[REPORT CONTENT]" > .agents/sessions/handoff_$(date +%Y%m%d_%H%M%S).md

# Send to team
python3 .agents/agent_tools.py msg broadcast YOUR_ROLE "Context Low - Handoff" "Report saved. Continuing after /compact"
```

Then run `/compact` and use the continuation prompt to resume.

## BEFORE CLOSING (CRITICAL!)
1. **Log your work:** `python3 .agents/agent_tools.py session log $SID "What I completed"`
2. **End session:** `python3 .agents/agent_tools.py session end $SID "Summary of work"`
3. **Leave registry:** `python3 .agents/agent_tools.py leave YOUR_ROLE --summary "Done"`
4. **Send handoff:** If work continues, message the next agent
5. **Update changelog:** If you made code changes, update CHANGELOG.md

## Available Roles
| Role | Emoji | Focus |
|------|-------|-------|
| ORCHESTRATOR | 🎯 | Team coordination, task delegation |
| PYTHON_ML | 🐍 | Python, ML, API development |
| MQL5_AGENT | 📊 | MetaTrader 5, MQL5 development |
| FLUTTER_AGENT | 📱 | Flutter, Dart, mobile apps |
| N8N_AGENT | ⚡ | N8N workflows, automation |
| DEVOPS | 🚀 | Cloud, Docker, deployment |
| RESEARCHER | 🔬 | Research, analysis, documentation |
| REVIEWER | 👁️ | Code review, testing, QA |
| DOCUMENTATION | 📚 | Docs, guides, API docs |
| DESIGNER | 🎨 | UI/UX design |
| TESTER | 🧪 | Testing, QA |
| CLOUD | ☁️ | Cloud infrastructure |

## REMEMBER
- You are **YOUR_ROLE** agent - stay in character
- Log significant actions during your session
- Communicate with other agents via messages
- Update your status when switching tasks
- Always end session properly before closing
PROMPT_EOF

    echo -e "${GREEN}  Created QUICK_PROMPT.md${NC}"
}

# Create the unified agent tools script
create_agent_tools() {
    cat > "$PROJECT_PATH/.agents/agent_tools.py" << 'TOOLS_EOF'
#!/usr/bin/env python3
"""
Unified Agent Tools - Registration, Messaging, and Session Logging
Works with any project's local .agents/ directory
"""

import sqlite3
import argparse
import json
from datetime import datetime
from pathlib import Path
import sys
import os

# Find project root (where .agents/ is)
def find_project_root():
    current = Path.cwd()
    while current != current.parent:
        if (current / '.agents').exists():
            return current
        current = current.parent
    return Path.cwd()

PROJECT_ROOT = find_project_root()
DB_PATH = PROJECT_ROOT / ".agents" / "project_kb.db"

ROLE_EMOJIS = {
    "ORCHESTRATOR": "🎯", "PYTHON_ML": "🐍", "MQL5_AGENT": "📊",
    "FLUTTER_AGENT": "📱", "N8N_AGENT": "⚡", "DEVOPS": "🚀",
    "RESEARCHER": "🔬", "REVIEWER": "👁️", "DOCUMENTATION": "📚",
    "DESIGNER": "🎨", "TESTER": "🧪", "CLOUD": "☁️", "CUSTOM": "🤖"
}

def get_conn():
    return sqlite3.connect(DB_PATH)

def generate_id(prefix, agent):
    ts = datetime.now().strftime('%Y%m%d%H%M%S')
    return f"{prefix}-{agent[:4].upper()}-{ts}"

# ============ REGISTRATION ============
def register(role, focus=None):
    conn = get_conn()
    now = datetime.now().isoformat()
    conn.execute("""
        INSERT INTO agents (agent_id, role, status, focus, session_start, last_heartbeat)
        VALUES (?, ?, 'active', ?, ?, ?)
        ON CONFLICT(agent_id) DO UPDATE SET
            status='active', focus=COALESCE(?, focus),
            session_start=?, last_heartbeat=?
    """, (role.upper(), role.upper(), focus, now, now, focus, now, now))
    conn.commit()
    conn.close()
    emoji = ROLE_EMOJIS.get(role.upper(), "🤖")
    print(f"\n{emoji} REGISTERED: {role.upper()}")
    print(f"   Focus: {focus or 'General'}")
    print(f"   Time: {now}")
    # Announce
    msg_send(role.upper(), None, f"Agent Joined: {role.upper()}", f"New agent registered with focus: {focus or 'General'}")

def list_agents(show_all=False):
    conn = get_conn()
    q = "SELECT * FROM agents" + ("" if show_all else " WHERE status='active'")
    agents = conn.execute(q).fetchall()
    conn.close()
    print(f"\n{'='*50}\nACTIVE AGENTS\n{'='*50}")
    for a in agents:
        emoji = ROLE_EMOJIS.get(a[1], "🤖")
        status = "🟢" if a[2] == 'active' else "⚫"
        print(f"{status} {emoji} {a[0]} - {a[3] or 'No focus'}")
    print(f"{'='*50}\nTotal: {len(agents)}")

def leave(role, summary=None):
    conn = get_conn()
    conn.execute("UPDATE agents SET status='inactive' WHERE agent_id=?", (role.upper(),))
    conn.commit()
    conn.close()
    print(f"\n👋 {role.upper()} session ended")
    if summary:
        msg_send(role.upper(), None, f"Session End: {role.upper()}", summary)

def update_status(role, working_on=None):
    conn = get_conn()
    conn.execute("""
        UPDATE agents SET working_on=?, last_heartbeat=datetime('now')
        WHERE agent_id=?
    """, (working_on, role.upper()))
    conn.commit()
    conn.close()
    print(f"✓ {role.upper()} status updated: {working_on}")

# ============ MESSAGING ============
def msg_list(unread_only=False):
    conn = get_conn()
    q = "SELECT * FROM messages" + (" WHERE is_read=0" if unread_only else "") + " ORDER BY created_at DESC LIMIT 20"
    msgs = conn.execute(q).fetchall()
    conn.close()
    print(f"\n{'='*50}\nMESSAGES\n{'='*50}")
    for m in msgs:
        status = "📩" if m[7] == 0 else "📭"
        print(f"{status} [{m[1]}] {m[2]} → {m[3] or 'ALL'}: {m[4]}")
    print(f"{'='*50}")

def msg_send(from_agent, to_agent, subject, content, msg_type='notification'):
    conn = get_conn()
    msg_id = generate_id("MSG", from_agent)
    conn.execute("""
        INSERT INTO messages (message_id, from_agent, to_agent, subject, content, message_type)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (msg_id, from_agent.upper(), to_agent.upper() if to_agent else None, subject, content, msg_type))
    conn.commit()
    conn.close()
    print(f"✉️ Sent: {msg_id}")

def msg_read(msg_id):
    conn = get_conn()
    conn.execute("UPDATE messages SET is_read=1 WHERE message_id=?", (msg_id,))
    msg = conn.execute("SELECT * FROM messages WHERE message_id=?", (msg_id,)).fetchone()
    conn.commit()
    conn.close()
    if msg:
        print(f"\n{'='*50}\n{msg[4]}\n{'='*50}")
        print(f"From: {msg[2]} | To: {msg[3] or 'ALL'}")
        print(f"Type: {msg[6]} | Date: {msg[8]}")
        print(f"\n{msg[5]}\n{'='*50}")

# ============ SESSIONS ============
def session_start(role):
    conn = get_conn()
    sid = generate_id("SESS", role)
    conn.execute("""
        INSERT INTO sessions (session_id, agent_id, role) VALUES (?, ?, ?)
    """, (sid, role.upper(), role.upper()))
    conn.commit()
    conn.close()
    print(f"\n📋 SESSION STARTED: {sid}")
    print(f"   Agent: {role.upper()}")
    print(f"\n   Save this ID: export SID={sid}")
    return sid

def session_log(session_id, action, details=None):
    conn = get_conn()
    conn.execute("""
        INSERT INTO activity_log (session_id, action, details) VALUES (?, ?, ?)
    """, (session_id, action, details))
    conn.commit()
    conn.close()
    print(f"  📝 Logged: {action[:50]}...")

def session_end(session_id, summary=None):
    conn = get_conn()
    conn.execute("""
        UPDATE sessions SET ended_at=datetime('now'), status='completed', summary=?
        WHERE session_id=?
    """, (summary, session_id))
    conn.commit()
    conn.close()
    print(f"\n✅ SESSION ENDED: {session_id}")
    if summary:
        print(f"   Summary: {summary}")

def session_list(agent=None):
    conn = get_conn()
    q = "SELECT * FROM sessions"
    if agent:
        q += f" WHERE agent_id='{agent.upper()}'"
    q += " ORDER BY started_at DESC LIMIT 10"
    sessions = conn.execute(q).fetchall()
    conn.close()
    print(f"\n{'='*50}\nSESSIONS\n{'='*50}")
    for s in sessions:
        status = "🟢" if s[5] == 'active' else "⚫"
        print(f"{status} {s[0]} - {s[1]} ({s[3]})")
    print(f"{'='*50}")

# ============ TASKS ============
def ensure_tasks_table():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'open',
            priority TEXT DEFAULT 'medium',
            assigned_to TEXT,
            created_by TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            completed_at DATETIME
        )
    """)
    conn.commit()
    conn.close()

def task_list(status_filter=None, assigned_to=None):
    ensure_tasks_table()
    conn = get_conn()
    q = "SELECT * FROM tasks WHERE 1=1"
    params = []
    if status_filter:
        q += " AND status=?"
        params.append(status_filter)
    if assigned_to:
        q += " AND assigned_to=?"
        params.append(assigned_to.upper())
    q += " ORDER BY created_at DESC"
    tasks = conn.execute(q, params).fetchall()
    conn.close()
    print(f"\n{'='*60}\nTASKS\n{'='*60}")
    for t in tasks:
        status_icon = {"open": "📋", "in_progress": "🔄", "done": "✅", "blocked": "🚫"}.get(t[3], "❓")
        priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(t[4], "⚪")
        print(f"{status_icon} {priority_icon} [{t[0]}] {t[1]}")
        print(f"   Assigned: {t[5] or 'Unassigned'} | Status: {t[3]} | Created: {t[7]}")
    print(f"{'='*60}\nTotal: {len(tasks)} tasks")

def task_add(title, assigned_to=None, priority="medium", description=None, created_by=None):
    ensure_tasks_table()
    conn = get_conn()
    task_id = generate_id("TASK", assigned_to or "ORCH")
    conn.execute("""
        INSERT INTO tasks (task_id, title, description, priority, assigned_to, created_by)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (task_id, title, description, priority, assigned_to.upper() if assigned_to else None, created_by))
    conn.commit()
    conn.close()
    print(f"📋 Task created: {task_id}")
    print(f"   Title: {title}")
    print(f"   Assigned to: {assigned_to or 'Unassigned'}")
    if assigned_to:
        msg_send(created_by or "SYSTEM", assigned_to, f"New Task: {task_id}", f"You have been assigned: {title}")
    return task_id

def task_done(task_id):
    ensure_tasks_table()
    conn = get_conn()
    conn.execute("""
        UPDATE tasks SET status='done', completed_at=datetime('now')
        WHERE task_id=?
    """, (task_id,))
    conn.commit()
    conn.close()
    print(f"✅ Task completed: {task_id}")

def task_assign(task_id, assigned_to, from_agent=None):
    ensure_tasks_table()
    conn = get_conn()
    conn.execute("UPDATE tasks SET assigned_to=? WHERE task_id=?", (assigned_to.upper(), task_id))
    task = conn.execute("SELECT title FROM tasks WHERE task_id=?", (task_id,)).fetchone()
    conn.commit()
    conn.close()
    print(f"📋 Task {task_id} assigned to {assigned_to.upper()}")
    if task:
        msg_send(from_agent or "SYSTEM", assigned_to, f"Task Assigned: {task_id}", f"You have been assigned: {task[0]}")

def task_status(task_id, new_status):
    ensure_tasks_table()
    conn = get_conn()
    conn.execute("UPDATE tasks SET status=? WHERE task_id=?", (new_status, task_id))
    conn.commit()
    conn.close()
    print(f"📋 Task {task_id} status: {new_status}")

def task_complete(task_id, session_id, role, summary, skip_tests=False, skip_git=False, skip_backup=False, skip_sync=False):
    """Complete a task with full workflow: mark done, log, broadcast, backup, sync, report."""
    import os
    import subprocess
    import shutil
    from datetime import datetime

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  TASK COMPLETION FLOW v2.0")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    print(f"Task ID:     {task_id}")
    print(f"Session ID:  {session_id}")
    print(f"Role:        {role}")
    print(f"Summary:     {summary}")
    print()

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    date_str = datetime.now().strftime("%Y-%m-%d")
    steps_completed = []
    steps_skipped = []

    # 1. Mark task done
    print("[1/7] Marking task complete...")
    task_done(task_id)
    steps_completed.append("Task marked done")

    # 2. Log completion
    print("[2/7] Logging completion...")
    session_log(session_id, f"COMPLETED: {task_id} - {summary}")
    steps_completed.append("Session logged")

    # 3. Broadcast to team
    print("[3/7] Broadcasting to team...")
    msg_send(role, None, f"Task Complete: {task_id}", summary)
    steps_completed.append("Team notified")

    # 4. Update CHANGELOG (reminder)
    print("[4/7] CHANGELOG check...")
    changelog_path = os.path.join(project_root, "CHANGELOG.md")
    if os.path.exists(changelog_path):
        with open(changelog_path, 'r') as f:
            if date_str in f.read():
                print("  ℹ CHANGELOG.md has entry for today")
            else:
                print(f"  ⚠ Remember to update CHANGELOG.md with:")
                print(f"    - **{task_id}** ({role}): {summary}")
        steps_skipped.append("CHANGELOG (manual)")
    else:
        print("  ⚠ CHANGELOG.md not found")
        steps_skipped.append("CHANGELOG (not found)")

    # 5. Backup (lightweight)
    print("[5/7] Creating backup...")
    if not skip_backup:
        backup_dir = os.path.join(project_root, ".agents", "backups")
        os.makedirs(backup_dir, exist_ok=True)
        backup_file = os.path.join(backup_dir, f"backup_{task_id}_{timestamp}.tar.gz")
        try:
            import tarfile
            with tarfile.open(backup_file, "w:gz") as tar:
                agents_dir = os.path.join(project_root, ".agents")
                if os.path.exists(agents_dir):
                    for db_file in os.listdir(agents_dir):
                        if db_file.endswith('.db'):
                            tar.add(os.path.join(agents_dir, db_file), arcname=f".agents/{db_file}")
            print(f"  ✓ Backup: {os.path.basename(backup_file)}")
            steps_completed.append("Backup created")
        except Exception as e:
            print(f"  ⚠ Backup failed: {e}")
            steps_skipped.append("Backup (failed)")
    else:
        print("  ⚠ Backup skipped")
        steps_skipped.append("Backup")

    # 6. Sync operations
    print("[6/7] Sync operations...")
    if not skip_sync:
        synced = False
        # Git push if available
        if not skip_git and shutil.which('git'):
            try:
                result = subprocess.run(['git', '-C', project_root, 'push'], capture_output=True, timeout=30)
                if result.returncode == 0:
                    print("  ✓ Git push successful")
                    steps_completed.append("Git push")
                    synced = True
                else:
                    print("  ℹ Git push skipped (no remote or up to date)")
            except:
                pass
        if not synced:
            print("  ℹ No sync targets available")
            steps_skipped.append("Sync")
    else:
        print("  ⚠ Sync skipped")
        steps_skipped.append("Sync")

    # 7. Create completion report
    print("[7/7] Creating completion report...")
    report_dir = os.path.join(project_root, ".agents", "sessions")
    os.makedirs(report_dir, exist_ok=True)
    report_file = os.path.join(report_dir, f"completion_{task_id}_{timestamp}.md")

    report_content = f"""# Task Completion Report

## Task Information
| Field | Value |
|-------|-------|
| Task ID | {task_id} |
| Completed By | {role} |
| Session ID | {session_id} |
| Date/Time | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |

## Summary
{summary}

## Workflow Results
### Completed
{chr(10).join(['- ✅ ' + s for s in steps_completed])}

### Skipped
{chr(10).join(['- ⏭️ ' + s for s in steps_skipped])}

## Verification Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Code reviewed (if required)

## Notes
[Add any additional notes here]

---
Generated by agent_tools.py task complete v2.0
"""

    with open(report_file, 'w') as f:
        f.write(report_content)

    print(f"  ✓ Report: {os.path.basename(report_file)}")
    steps_completed.append("Report generated")

    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  ✓ TASK COMPLETION FLOW FINISHED")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    print(f"Completed: {len(steps_completed)} steps | Skipped: {len(steps_skipped)} steps")
    print()
    print("For FULL completion workflow with tests, git, and more:")
    print(f"  ./scripts/complete_task.sh {task_id} {session_id} {role} \"{summary}\"")
    print()
    print("Next steps:")
    print("  1. Review and update CHANGELOG.md")
    print("  2. Push changes if ready: git push")
    print("  3. Continue with next task or end session")

# ============ MAIN ============
def main():
    parser = argparse.ArgumentParser(description="Unified Agent Tools")
    subparsers = parser.add_subparsers(dest="cmd")

    # Register
    reg = subparsers.add_parser("register", help="Register agent")
    reg.add_argument("role", help="Agent role")
    reg.add_argument("--focus", "-f", help="Focus area")

    # List
    subparsers.add_parser("list", help="List agents")

    # Leave
    lv = subparsers.add_parser("leave", help="Leave session")
    lv.add_argument("role", help="Agent role")
    lv.add_argument("--summary", "-s", help="Summary")

    # Status
    st = subparsers.add_parser("status", help="Update status")
    st.add_argument("role", help="Agent role")
    st.add_argument("--working-on", "-w", help="Current task")

    # Messaging
    msg = subparsers.add_parser("msg", help="Messaging")
    msg_sub = msg.add_subparsers(dest="msg_cmd")
    msg_sub.add_parser("list", help="List messages")
    msg_send_p = msg_sub.add_parser("send", help="Send message")
    msg_send_p.add_argument("from_agent")
    msg_send_p.add_argument("to_agent")
    msg_send_p.add_argument("subject")
    msg_send_p.add_argument("content")
    msg_read_p = msg_sub.add_parser("read", help="Read message")
    msg_read_p.add_argument("msg_id")
    msg_bc = msg_sub.add_parser("broadcast", help="Broadcast")
    msg_bc.add_argument("from_agent")
    msg_bc.add_argument("subject")
    msg_bc.add_argument("content")

    # Sessions
    sess = subparsers.add_parser("session", help="Session management")
    sess_sub = sess.add_subparsers(dest="sess_cmd")
    sess_start = sess_sub.add_parser("start", help="Start session")
    sess_start.add_argument("role")
    sess_log = sess_sub.add_parser("log", help="Log action")
    sess_log.add_argument("session_id")
    sess_log.add_argument("action")
    sess_end = sess_sub.add_parser("end", help="End session")
    sess_end.add_argument("session_id")
    sess_end.add_argument("summary", nargs="?")
    sess_sub.add_parser("list", help="List sessions")

    # Tasks
    task = subparsers.add_parser("task", help="Task management")
    task_sub = task.add_subparsers(dest="task_cmd")
    task_sub.add_parser("list", help="List tasks")
    task_add_p = task_sub.add_parser("add", help="Add task")
    task_add_p.add_argument("title", help="Task title")
    task_add_p.add_argument("assigned_to", nargs="?", help="Assign to agent")
    task_add_p.add_argument("--priority", "-p", default="medium", help="Priority: high/medium/low")
    task_add_p.add_argument("--from", dest="created_by", help="Created by agent")
    task_done_p = task_sub.add_parser("done", help="Mark task done")
    task_done_p.add_argument("task_id", help="Task ID")
    task_assign_p = task_sub.add_parser("assign", help="Assign task")
    task_assign_p.add_argument("task_id", help="Task ID")
    task_assign_p.add_argument("assigned_to", help="Assign to agent")
    task_assign_p.add_argument("--from", dest="from_agent", help="From agent")
    task_status_p = task_sub.add_parser("status", help="Update task status")
    task_status_p.add_argument("task_id", help="Task ID")
    task_status_p.add_argument("new_status", help="Status: open/in_progress/done/blocked")
    task_complete_p = task_sub.add_parser("complete", help="Complete task with full workflow")
    task_complete_p.add_argument("task_id", help="Task ID")
    task_complete_p.add_argument("session_id", help="Session ID")
    task_complete_p.add_argument("role", help="Your agent role")
    task_complete_p.add_argument("summary", help="Brief summary of what was done")

    args = parser.parse_args()

    if args.cmd == "register":
        register(args.role, args.focus)
    elif args.cmd == "list":
        list_agents()
    elif args.cmd == "leave":
        leave(args.role, args.summary)
    elif args.cmd == "status":
        update_status(args.role, args.working_on)
    elif args.cmd == "msg":
        if args.msg_cmd == "list":
            msg_list()
        elif args.msg_cmd == "send":
            msg_send(args.from_agent, args.to_agent, args.subject, args.content)
        elif args.msg_cmd == "read":
            msg_read(args.msg_id)
        elif args.msg_cmd == "broadcast":
            msg_send(args.from_agent, None, args.subject, args.content)
    elif args.cmd == "session":
        if args.sess_cmd == "start":
            session_start(args.role)
        elif args.sess_cmd == "log":
            session_log(args.session_id, args.action)
        elif args.sess_cmd == "end":
            session_end(args.session_id, args.summary)
        elif args.sess_cmd == "list":
            session_list()
    elif args.cmd == "task":
        if args.task_cmd == "list":
            task_list()
        elif args.task_cmd == "add":
            task_add(args.title, args.assigned_to, args.priority, created_by=args.created_by)
        elif args.task_cmd == "done":
            task_done(args.task_id)
        elif args.task_cmd == "assign":
            task_assign(args.task_id, args.assigned_to, args.from_agent)
        elif args.task_cmd == "status":
            task_status(args.task_id, args.new_status)
        elif args.task_cmd == "complete":
            task_complete(args.task_id, args.session_id, args.role, args.summary)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
TOOLS_EOF

    chmod +x "$PROJECT_PATH/.agents/agent_tools.py"
    echo -e "${GREEN}  Created agent_tools.py${NC}"
}

# Generate agent prompt for specific role
generate_prompt() {
    local ROLE=$1
    local EMOJI=$(get_emoji "$ROLE")
    local PROJECT_NAME=$(basename "$PROJECT_PATH")

    cat << EOF
# ${EMOJI} ${ROLE} AGENT - ${PROJECT_NAME}

## YOUR IDENTITY
You are **${ROLE}** agent in the ${PROJECT_NAME} multi-agent team.
- Role: ${ROLE}
- Emoji: ${EMOJI}
- Project: ${PROJECT_NAME}
- Stay focused on your role responsibilities throughout this session.

## FIRST: REGISTER YOURSELF (REQUIRED!)
\`\`\`bash
python3 .agents/agent_tools.py register ${ROLE} --focus "Your specialization"
python3 .agents/agent_tools.py session start ${ROLE}
# SAVE THE SESSION ID: export SID=SESS-XXXX-XXXXXX

# Check messages & team
python3 .agents/agent_tools.py msg list
python3 .agents/agent_tools.py list
\`\`\`

## QUICK COMMANDS
\`\`\`bash
# Messaging
python3 .agents/agent_tools.py msg send ${ROLE} TARGET "Subject" "Content"
python3 .agents/agent_tools.py msg broadcast ${ROLE} "Subject" "Content"

# Status
python3 .agents/agent_tools.py status ${ROLE} -w "current task"

# Session logging
python3 .agents/agent_tools.py session log \$SID "Action description"
\`\`\`

## VERSION & CHANGELOG
When making changes:
1. Check VERSION file: \`cat VERSION\`
2. Update CHANGELOG.md with your changes
3. Use semantic versioning: MAJOR.MINOR.PATCH

## BEFORE CLOSING (CRITICAL!)
\`\`\`bash
python3 .agents/agent_tools.py session log \$SID "Final actions"
python3 .agents/agent_tools.py session end \$SID "Summary of work"
python3 .agents/agent_tools.py leave ${ROLE} --summary "Session complete"
\`\`\`

## CONTEXT MANAGEMENT
- At ~10%: Run \`/compact\` to free context
- At ~5%: CREATE HANDOFF REPORT first!
  1. Save report to .agents/sessions/handoff_DATE.md
  2. Include: completed work, current state, next steps, continuation prompt
  3. Then run \`/compact\` and paste continuation prompt

## REMEMBER
- You are ${EMOJI} **${ROLE}** - stay in character
- Log significant actions
- Update CHANGELOG.md for code changes
- Communicate with team via messages
- Run /compact before 5% context remaining
- End session properly before closing

Ready to work as ${ROLE}. Register first!
EOF
}

# Launch agents in tmux
launch_agents() {
    local AGENTS=($1)

    tmux kill-session -t "$SESSION_NAME" 2>/dev/null

    echo -e "${GREEN}Creating tmux session: $SESSION_NAME${NC}"
    tmux new-session -d -s "$SESSION_NAME" -n "${AGENTS[0]}" -c "$PROJECT_PATH"

    for ((i=1; i<${#AGENTS[@]}; i++)); do
        tmux new-window -t "$SESSION_NAME" -n "${AGENTS[$i]}" -c "$PROJECT_PATH"
    done

    for ((i=0; i<${#AGENTS[@]}; i++)); do
        local ROLE="${AGENTS[$i]}"
        local EMOJI=$(get_emoji "$ROLE")
        echo -e "${GREEN}Launching $EMOJI $ROLE...${NC}"

        local PROMPT=$(generate_prompt "$ROLE")
        PROMPT=$(echo "$PROMPT" | sed 's/"/\\"/g')

        tmux send-keys -t "$SESSION_NAME:$i" "cd $PROJECT_PATH && claude -p \"$PROMPT\"" C-m
        sleep 0.3
    done
}

# Main execution
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  PROJECT AGENT INITIALIZER${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

# Setup project
setup_project
create_agent_tools

# Determine agents
if [[ "$TEAM_TYPE" == "custom" ]]; then
    AGENTS_LIST="${@:3}"
else
    AGENTS_LIST=$(get_team "$TEAM_TYPE")
fi

echo -e "\n${GREEN}Team: $TEAM_TYPE${NC}"
echo -e "${GREEN}Agents: $AGENTS_LIST${NC}"

# Launch
read -p "Launch agents in tmux? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    launch_agents "$AGENTS_LIST"

    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  AGENTS LAUNCHED${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Attach: tmux attach -t $SESSION_NAME"
    echo "Navigate: Ctrl+B 0-9 or Ctrl+B n/p"
    echo ""

    tmux attach -t "$SESSION_NAME"
else
    echo ""
    echo -e "${GREEN}Project initialized. To launch later:${NC}"
    echo "  cd $PROJECT_PATH"
    echo "  # Start agents manually with quick prompt:"
    echo "  claude -p \"\$(cat .agents/QUICK_PROMPT.md)\""
fi
