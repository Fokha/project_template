# Lessons Learned: Multi-Agent System Architecture

## 1. Agent Organization

### Agent Roles & Responsibilities
| Agent | Role | Language | Primary Function |
|-------|------|----------|------------------|
| **CLAUDE_CODE** | Orchestrator | Natural Language | Code generation, planning, coordination |
| **US_PY** | ML Engine | Python | Predictions, API server, data processing |
| **AI_STUDIO** | Frontend | Flutter/Dart | User interface, visualization |
| **MT5_EA** | Trading | MQL5 | Trade execution, market data |
| **N8N** | Automation | Node.js/JSON | Workflows, scheduling, notifications |
| **CLOUD** | Infrastructure | Docker/Bash | Deployment, scaling, monitoring |

### Key Insight: Single Source of Truth
- **Problem**: Agents worked in silos, duplicating context, losing decisions
- **Solution**: Shared Knowledge Base (SQLite) accessible by ALL agents
- **Result**: Any agent can resume work, see decisions, check tasks

---

## 2. Communication Architecture

### What Worked
```
┌─────────────────────────────────────────────────────────┐
│                    KNOWLEDGE BASE                        │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │  Tasks  │ │Research │ │Decisions│ │Messages │       │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘       │
│       └──────────┼──────────┼──────────┘               │
│                  │   REST API (/kb/*)                   │
└──────────────────┼──────────────────────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
┌───┴───┐    ┌────┴────┐    ┌────┴────┐
│Claude │    │ Python  │    │ Flutter │
│ Code  │    │   API   │    │   App   │
└───────┘    └─────────┘    └─────────┘
    │              │              │
┌───┴───┐    ┌────┴────┐    ┌────┴────┐
│  MT5  │    │   n8n   │    │  Cloud  │
│  EA   │    │Workflows│    │ Server  │
└───────┘    └─────────┘    └─────────┘
```

### Communication Patterns
1. **Direct API** - HTTP REST for structured data
2. **Broadcast Messages** - `to_agent: null` for announcements
3. **Point-to-Point** - Specific agent targeting
4. **Activity Logging** - Audit trail for all actions

---

## 3. Knowledge Base Design

### Core Tables (Minimum Viable KB)
```sql
-- 1. Tasks - Track all work
kb_tasks (task_id, title, status, priority, assigned_to)

-- 2. Decisions - Record architectural choices
kb_decisions (decision_id, title, decision, rationale, made_by)

-- 3. Messages - Inter-agent communication
kb_messages (from_agent, to_agent, content, message_type)

-- 4. Context - Session persistence
kb_session_context (context_type, context_key, content)

-- 5. Activity - Audit log
kb_activity_log (action, entity_type, entity_id, actor)
```

### Access Pattern for Each Agent
```
Agent Startup:
1. GET /kb/resume → Load full context
2. GET /kb/messages?to_agent=ME → Check inbox
3. GET /kb/tasks?assigned_to=ME → My work items

During Work:
4. POST /kb/activity → Log actions
5. PUT /kb/tasks/{id} → Update progress

End of Session:
6. POST /kb/context → Save current focus
7. POST /kb/conversations → Save important points
```

---

## 4. Project Structure

### Recommended Directory Layout
```
project/
├── .claude/
│   └── commands/           # Slash commands
│       ├── resume.md       # /resume - Load context
│       └── save-context.md # /save-context - Persist state
├── knowledge_base/
│   ├── schema.sql          # Database schema
│   ├── agent_kb.db         # SQLite database
│   └── migrations/         # Schema updates
├── docs/
│   ├── AGENT_COMMS.md      # Task tracking
│   ├── AGENT_KB_ACCESS.md  # Unified access guide
│   └── ARCHITECTURE.md     # System design
├── config/
│   ├── .env.example        # Environment template
│   └── credentials/        # Encrypted secrets
└── [language-specific dirs]
    ├── python_ml/          # Python components
    ├── lib/                # Flutter components
    └── mql5/               # MT5 components
```

---

## 5. Environment & Tools

### Essential Tools
| Tool | Purpose | Why It Works |
|------|---------|--------------|
| **SQLite** | Knowledge Base | No server needed, portable, fast |
| **Flask** | API Server | Simple, Python native, Blueprint support |
| **n8n** | Automation | Visual workflows, HTTP integrations |
| **Docker** | Deployment | Consistent environments, easy scaling |

### Development Environment
```bash
# Local Development
- Python 3.11+ with venv
- Flutter 3.x for mobile/desktop
- SQLite (built-in)
- n8n (Docker or npm)

# Cloud Deployment
- Docker Compose for services
- Nginx for reverse proxy
- SQLite for persistence (or PostgreSQL for scale)
```

---

## 6. Prompt Engineering Insights

### Agent System Prompts Should Include
```markdown
## Context Recovery
On session start:
1. Read /kb/resume for full context
2. Check messages addressed to you
3. Review assigned tasks
4. Note recent decisions

## Session Management
Before ending:
1. Save current focus to /kb/context
2. Log significant actions to /kb/activity
3. Update task statuses
4. Send messages for handoffs

## Communication Protocol
- Use structured messages (type, subject, content)
- Log all significant actions
- Reference task IDs in updates
- Broadcast important decisions
```

### Task Tracking Format (AGENT_COMMS.md)
```markdown
| Task ID | Description | Assigned | Status |
|---------|-------------|----------|--------|
| T001 | Create KB API | US_PY | ✅ DONE |
| T002 | Add Flutter widget | AI_STUDIO | 🔄 IN PROGRESS |
| T003 | Deploy to cloud | CLOUD | 📋 BACKLOG |
```

---

## 7. Key Patterns

### Pattern 1: Unified Access Document
Create ONE file that shows ALL agents how to access shared resources:
```
docs/AGENT_KB_ACCESS.md
├── Claude Code (sqlite3, curl)
├── Python (direct db, requests)
├── Flutter (Service class)
├── MT5 (WebRequest)
├── n8n (HTTP Request node)
└── Cloud (curl with different host)
```

### Pattern 2: Test Connection Everywhere
Every interface should have a "Test Connection" button:
- Flutter: Button with status indicator
- API: `/health` endpoint
- n8n: Status check workflow

### Pattern 3: Conversation Persistence
```python
# Save important context before session ends
POST /kb/context
{
  "type": "focus",
  "key": "current_topic",
  "content": "What you were working on"
}

POST /kb/conversations
{
  "summary": "Key points from this session",
  "importance": 2  # 1=normal, 2=important, 3=critical
}
```

### Pattern 4: Activity Logging
```python
# Log all significant actions
POST /kb/activity
{
  "action": "task_completed",
  "entity_type": "task",
  "entity_id": "T123",
  "actor": "AGENT_NAME",
  "details": {"notes": "Additional context"}
}
```

---

## 8. Common Pitfalls & Solutions

| Pitfall | Solution |
|---------|----------|
| Context lost between sessions | Use KB context persistence |
| Agents duplicate work | Check KB before starting tasks |
| Decisions forgotten | Record in kb_decisions with rationale |
| No audit trail | Log all actions to kb_activity_log |
| Different access methods | Create unified access guide |
| Port conflicts | Use health checks, process management |
| Stale data | Add refresh/test buttons, cache expiry |

---

## 9. Minimum Viable Multi-Agent Setup

### Step 1: Create Database
```bash
sqlite3 knowledge_base/agent_kb.db < knowledge_base/schema.sql
```

### Step 2: Add API Endpoints
```python
# In your main API server
from utils.kb_api import kb_bp
app.register_blueprint(kb_bp)
```

### Step 3: Create Access Guide
One markdown file with code examples for each agent type.

### Step 4: Add Slash Commands
```markdown
# .claude/commands/resume.md
Load context from KB: GET /kb/resume
Display project, tasks, decisions, focus
```

### Step 5: Test Everything
- Test connection button in UI
- Health check endpoint
- Telegram /status command

---

## 10. Future Improvements

1. **Real-time sync** - WebSocket for live updates
2. **Conflict resolution** - Handle concurrent edits
3. **Encryption** - Secure sensitive data
4. **Versioning** - Track changes over time
5. **Search** - Full-text search across KB
6. **Analytics** - Dashboard for agent performance
