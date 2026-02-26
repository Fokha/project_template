# Agent Knowledge Base Setup Guide

Complete guide to setting up and using the Agent Knowledge Base for Claude Code agent conversations and context persistence.

## Overview

The Agent Knowledge Base (`agent_kb.db`) is a SQLite database that stores:
- **Tasks** - Work items with status, priority, assignments
- **Research** - Research findings, sources, and analysis
- **Decisions** - Architectural and technical decisions with rationale
- **Messages** - Inter-agent communication
- **Context** - Session context that survives restarts
- **Conversations** - Important conversation points
- **Architecture** - Project component documentation
- **Activity Log** - All system activity

## Quick Setup

### 1. Create the Database

```bash
# Navigate to your project
cd /path/to/your/project

# Create knowledge_base directory
mkdir -p knowledge_base

# Create database from schema
sqlite3 knowledge_base/agent_kb.db < knowledge_base/schema.sql
```

### 2. Initialize Project Info

```bash
sqlite3 knowledge_base/agent_kb.db "
INSERT OR REPLACE INTO kb_project (key, value, category) VALUES
    ('project_name', 'Your Project Name', 'config'),
    ('project_version', '1.0.0', 'config'),
    ('created_at', datetime('now'), 'config');
"
```

### 3. Add Architecture Components

```bash
sqlite3 knowledge_base/agent_kb.db "
INSERT INTO kb_architecture (component, display_name, language, framework, description) VALUES
    ('backend', 'Backend API', 'Python', 'Flask', 'REST API server'),
    ('frontend', 'Web App', 'TypeScript', 'React', 'User interface');
"
```

## Database Schema

### Core Tables

#### kb_project
Stores project configuration.
```sql
CREATE TABLE kb_project (
    id INTEGER PRIMARY KEY,
    key TEXT UNIQUE NOT NULL,
    value TEXT,
    category TEXT,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### kb_tasks
Tracks all work items.
```sql
CREATE TABLE kb_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT UNIQUE NOT NULL,      -- e.g., T001, T002
    title TEXT NOT NULL,
    description TEXT,
    full_specification TEXT,
    status TEXT DEFAULT 'backlog',     -- backlog, in_progress, done, cancelled
    priority TEXT DEFAULT 'medium',    -- critical, high, medium, low
    assigned_to TEXT,
    requested_by TEXT,
    tags TEXT,                         -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

#### kb_research
Stores research entries.
```sql
CREATE TABLE kb_research (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    research_id TEXT UNIQUE,           -- e.g., R001, R002
    topic TEXT NOT NULL,
    query TEXT,
    summary TEXT,
    findings TEXT,                     -- Accumulated findings with timestamps
    sources TEXT,                      -- JSON array of sources
    related_task_id TEXT,
    status TEXT DEFAULT 'in_progress', -- in_progress, completed
    researcher TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### kb_decisions
Records architectural decisions.
```sql
CREATE TABLE kb_decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_id TEXT UNIQUE,           -- e.g., D001, D002
    title TEXT NOT NULL,
    context TEXT,
    decision TEXT NOT NULL,
    alternatives TEXT,                 -- JSON array
    rationale TEXT,
    category TEXT,
    made_by TEXT,
    made_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### kb_messages
Inter-agent communication.
```sql
CREATE TABLE kb_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT,
    from_agent TEXT NOT NULL,
    to_agent TEXT,                     -- NULL = broadcast
    message_type TEXT NOT NULL,        -- request, response, update, announcement
    subject TEXT,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### kb_session_context
Persists session context.
```sql
CREATE TABLE kb_session_context (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    context_type TEXT NOT NULL,        -- focus, memory, preference
    context_key TEXT,
    content TEXT,
    is_persistent INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### kb_conversations
Stores important conversation points.
```sql
CREATE TABLE kb_conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    role TEXT,                         -- user, assistant
    content TEXT,
    summary TEXT,
    importance INTEGER DEFAULT 1,      -- 1=normal, 2=important, 3=critical
    tags TEXT,                         -- JSON array
    related_task_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## API Endpoints

The KB is accessible via REST API at `/kb/*`:

### Session Management
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/kb/resume` | GET | Load full session context |
| `/kb/project` | GET | Get project info |
| `/kb/context` | GET/POST | Get/save session context |

### Tasks
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/kb/tasks` | GET | List tasks (filter: status, priority, assigned_to) |
| `/kb/tasks` | POST | Create task |
| `/kb/tasks/<id>` | GET | Get specific task |
| `/kb/tasks/<id>` | PUT | Update task |

### Research
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/kb/research` | GET | List research entries |
| `/kb/research` | POST | Create research |
| `/kb/research/<id>` | GET | Get research |
| `/kb/research/<id>` | PUT | Update research |
| `/kb/research/<id>/findings` | POST | Add finding |
| `/kb/research/<id>/sources` | POST | Add source |

### Decisions
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/kb/decisions` | GET | List decisions |
| `/kb/decisions` | POST | Record decision |

### Messages
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/kb/messages` | GET | List messages |
| `/kb/messages` | POST | Send message |

### Other
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/kb/architecture` | GET/POST | View/update components |
| `/kb/conversations` | POST | Save conversation point |
| `/kb/activity` | GET/POST | View/log activity |

## Usage Examples

### Create a Task via API

```bash
curl -X POST http://localhost:5050/kb/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implement user authentication",
    "description": "Add JWT-based auth to API",
    "priority": "high",
    "assigned_to": "developer_agent"
  }'
```

### Start Research

```bash
# Create research entry
curl -X POST http://localhost:5050/kb/research \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "OAuth 2.0 vs JWT",
    "query": "Best authentication method for API",
    "related_task_id": "T001",
    "researcher": "research_agent"
  }'

# Add findings as you research
curl -X POST http://localhost:5050/kb/research/R001/findings \
  -H "Content-Type: application/json" \
  -d '{"finding": "JWT is stateless, better for microservices"}'

# Add sources
curl -X POST http://localhost:5050/kb/research/R001/sources \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://jwt.io/introduction",
    "title": "JWT Introduction",
    "type": "documentation"
  }'
```

### Record a Decision

```bash
curl -X POST http://localhost:5050/kb/decisions \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Use JWT for Authentication",
    "context": "Need stateless auth for microservices",
    "decision": "Implement JWT with refresh tokens",
    "rationale": "Stateless, scalable, industry standard",
    "category": "security",
    "made_by": "architect_agent"
  }'
```

### Save Session Context

```bash
# Save current focus
curl -X POST http://localhost:5050/kb/context \
  -H "Content-Type: application/json" \
  -d '{
    "type": "focus",
    "key": "current_topic",
    "content": "Implementing authentication system"
  }'

# Save recent work
curl -X POST http://localhost:5050/kb/context \
  -H "Content-Type: application/json" \
  -d '{
    "type": "focus",
    "key": "recent_work",
    "content": "Created JWT middleware, added login endpoint"
  }'
```

### Resume Session

```bash
# Get full context to resume work
curl http://localhost:5050/kb/resume | jq .
```

## Claude Code Integration

### Slash Commands

Create `.claude/commands/resume.md`:
```markdown
# Resume Session

Load context from knowledge base to continue work.

1. Call GET /kb/resume
2. Display project info, active tasks, recent decisions
3. Show current focus and important context
```

Create `.claude/commands/save-context.md`:
```markdown
# Save Context

Save current session state to knowledge base.

1. Update current topic in kb_session_context
2. Save recent work summary
3. Record any important decisions made
```

### Agent Prompts

Store reusable prompts in `kb_documents`:

```bash
sqlite3 knowledge_base/agent_kb.db "
INSERT INTO kb_documents (doc_id, title, doc_type, category, content_text) VALUES
    ('P001', 'Code Review Prompt', 'prompt', 'review',
     'Review this code for:
      1. Security vulnerabilities
      2. Performance issues
      3. Best practices
      4. Error handling'),
    ('P002', 'Research Prompt', 'prompt', 'research',
     'Research this topic:
      - Find official documentation
      - Compare alternatives
      - Identify best practices
      - Note any trade-offs');
"
```

## Multi-Agent Coordination

### Agent Registry

Agents register with the KB to coordinate work across terminals.

#### Tables
- **kb_agents** — Agent registry with status, focus, locked files, heartbeat
- **kb_work_logs** — What each agent completed, files changed, commit hashes

#### API Endpoints

```bash
KB_URL=http://localhost:5050/kb

# Register agent
curl -X POST "$KB_URL/agents/MY_AGENT" \
  -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" \
  -d '{"role": "developer", "focus": "what you do", "repo": "repo_name", "capabilities": ["dart", "flutter"]}'

# List all agents
curl -s -H "X-API-Key: $API_KEY" "$KB_URL/agents"

# Update status and lock files
curl -X PUT "$KB_URL/agents/MY_AGENT" \
  -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" \
  -d '{"status": "busy", "working_on": "T230", "locked_files": ["lib/main.dart"]}'

# Heartbeat (send every few minutes)
curl -X POST "$KB_URL/agents/MY_AGENT/heartbeat" -H "X-API-Key: $API_KEY"

# Deregister when done
curl -X DELETE "$KB_URL/agents/MY_AGENT" -H "X-API-Key: $API_KEY"
```

### Work Logging

Every agent logs what they complete for audit trail and coordination.

```bash
# Log completed work
curl -X POST "$KB_URL/work-logs" \
  -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" \
  -d '{"agent_id": "MY_AGENT", "task_id": "T230", "action": "completed", "summary": "description of work", "files_changed": ["file1.dart", "file2.dart"], "commit_hash": "abc123"}'

# View work logs
curl -s -H "X-API-Key: $API_KEY" "$KB_URL/work-logs?agent_id=MY_AGENT"
```

### Team Dashboard

Single endpoint for full coordination overview.

```bash
curl -s -H "X-API-Key: $API_KEY" "$KB_URL/team/status"
```

Returns: all agents, locked files, task summary, active tasks, available tasks, recent work logs, recent activity.

### Coordination Workflow

1. **Register** → `POST /kb/agents/NAME`
2. **Check dashboard** → `GET /kb/team/status` (see locked files, available tasks)
3. **Claim task** → `PUT /kb/tasks/T###` with `status: in_progress, assigned_to: NAME`
4. **Preflight** → `GET /kb/preflight/T###` (check lessons, conflicts, warnings)
5. **Lock files** → `PUT /kb/agents/NAME` with `locked_files: [...]`
6. **Do work** → Edit files, commit (don't push)
7. **Log work** → `POST /kb/work-logs` (with `retrospective` and `lesson_learned`)
8. **Release** → `PUT /kb/agents/NAME` with `locked_files: []`
9. **Mark done** → `PUT /kb/tasks/T###` with `status: done`
10. **Health check** → `POST /kb/health-check`

### Rules
- Check `locked_files` before editing ANY file another agent might touch
- Only Master terminal pushes to remote
- All agents commit with `[T###]` prefix in commit messages
- Always run preflight before starting a task
- Always log retrospective when completing work

## Evolution Features (v2.0)

### Preflight Check
```bash
# Returns relevant lessons, decisions, conflicts, and warnings before starting a task
curl -s -H "X-API-Key: $API_KEY" "$KB_URL/preflight/T001"
```

### Lessons Lookup
```bash
# Search past lessons by keyword, topic, or tags
curl -s -H "X-API-Key: $API_KEY" "$KB_URL/lessons?keyword=authentication"
curl -s -H "X-API-Key: $API_KEY" "$KB_URL/lessons?tags=bug,critical"
```

### Task Conflict Detection
```bash
# Check for file locks, blocking dependencies, agent overlap
curl -s -H "X-API-Key: $API_KEY" "$KB_URL/tasks/T001/conflicts"
```

### Retrospectives & Auto-Learning
```bash
# Work logs now support retrospective and lesson_learned fields
# lesson_learned auto-creates a research entry in the KB
# tags auto-update the agent's skill matrix
curl -X POST "$KB_URL/work-logs" \
  -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" \
  -d '{"agent_id": "DEV", "task_id": "T001", "action": "completed",
       "summary": "What was done", "retrospective": "What went well/badly",
       "lesson_learned": "Key insight", "tags": ["python", "api"]}'
```

### Agent Skill Matrix
```bash
# Scores auto-update when work is logged with tags
curl -s -H "X-API-Key: $API_KEY" "$KB_URL/skills/matrix"
curl -s -H "X-API-Key: $API_KEY" "$KB_URL/agents/DEV/skills"

# Manually update a skill score
curl -X POST "$KB_URL/agents/DEV/skills" \
  -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" \
  -d '{"skill": "react", "score": 8.0}'
```

### Per-Agent Memory (Cross-Session)
```bash
# Save persistent memory for an agent
curl -X POST "$KB_URL/memory/DEV" \
  -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" \
  -d '{"key": "preferred_workflow", "content": "Always run tests before committing", "category": "preferences"}'

# Load agent memory
curl -s -H "X-API-Key: $API_KEY" "$KB_URL/memory/DEV"
```

### Post-Task Health Check
```bash
# Verify task completion quality
curl -X POST "$KB_URL/health-check" \
  -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" \
  -d '{"agent_id": "DEV", "task_id": "T001",
       "checks": [{"type": "task_complete"}, {"type": "files_unlocked"},
                   {"type": "work_logged"}, {"type": "retrospective"}]}'
```

## Best Practices

### 1. Task Management
- Create tasks with clear, actionable titles
- Use consistent status values: `backlog`, `pending`, `in_progress`, `done`, `cancelled`
- Link related research to tasks via `related_task_id`

### 2. Decision Recording
- Always include context and rationale
- List alternatives considered
- Reference related tasks or research

### 3. Context Persistence
- Save context before ending sessions
- Use `/resume` at start of new sessions
- Mark important conversations with `importance >= 2`

### 4. Research Tracking
- Create research entry before starting investigation
- Add findings incrementally with timestamps
- Include all sources with proper attribution

## Backup & Sync

### Local Backup
```bash
cp knowledge_base/agent_kb.db knowledge_base/agent_kb_backup_$(date +%Y%m%d).db
```

### Sync to Cloud
```bash
scp knowledge_base/agent_kb.db user@server:~/project/knowledge_base/
```

## Troubleshooting

### Database locked
```bash
# Find and close connections
lsof | grep agent_kb.db
```

### Reset database
```bash
rm knowledge_base/agent_kb.db
sqlite3 knowledge_base/agent_kb.db < knowledge_base/schema.sql
```

### Check database status
```bash
sqlite3 knowledge_base/agent_kb.db "
SELECT 'Tasks' as table_name, COUNT(*) as count FROM kb_tasks
UNION ALL
SELECT 'Research', COUNT(*) FROM kb_research
UNION ALL
SELECT 'Decisions', COUNT(*) FROM kb_decisions
UNION ALL
SELECT 'Messages', COUNT(*) FROM kb_messages;
"
```
