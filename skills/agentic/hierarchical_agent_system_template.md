# Hierarchical Agent System Template

**Pattern:** Multi-layer agent architecture with supervisor, architect, and specialists
**Category:** Architecture
**Complexity:** ⭐⭐⭐⭐

---

## Overview

The Hierarchical Agent System is an architectural pattern for organizing multiple AI agents into a clear chain of command. It provides:

- **Single point of contact** for users (THE_ASSISTANT)
- **Strategic decision-making** layer (THE_MASTER)
- **Domain-specific execution** (Specialists)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    HIERARCHICAL AGENT ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│                            👤 USER                                       │
│                                │                                         │
│                                │ Natural language                        │
│                                ▼                                         │
│                    ┌─────────────────────┐                              │
│                    │   THE_ASSISTANT     │  ◄── LAYER 1: User Interface │
│                    │    (Supervisor)     │                              │
│                    └──────────┬──────────┘                              │
│                               │                                          │
│            ┌──────────────────┼──────────────────┐                      │
│            │                  │                  │                      │
│            ▼                  ▼                  ▼                      │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                │
│   │   MASTER    │    │   Direct    │    │   Direct    │                │
│   │  (Architect)│    │  Execution  │    │   Queries   │                │
│   └──────┬──────┘    └─────────────┘    └─────────────┘                │
│          │                                               ◄── LAYER 2   │
│          │ Delegates implementation                                     │
│          │                                                              │
│   ┌──────┴──────┬───────────┬───────────┐                              │
│   ▼             ▼           ▼           ▼              ◄── LAYER 3    │
│ ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐                         │
│ │BACKEND │  │FRONTEND│  │ DEVOPS │  │  ...   │     Specialists         │
│ └────────┘  └────────┘  └────────┘  └────────┘                         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## When to Use

✅ **Use this pattern when:**
- Project has multiple distinct domains (backend, frontend, devops, etc.)
- Tasks range from simple queries to complex multi-step features
- Different tasks require different expertise levels
- You need consistent user experience across all operations
- Clear accountability for decisions is needed

❌ **Don't use when:**
- Single-domain project with simple tasks
- All tasks are similar in complexity
- You need maximum speed over structure

---

## Agent Roles

### Layer 1: THE_ASSISTANT (Supervisor)

```yaml
Role: User Interface
Model: Claude Opus 4.5 (best comprehension)
Capabilities:
  - All tools available
  - Can delegate to any agent
  - Tracks task progress
  - Reports to user

Responsibilities:
  - Receive all user requests
  - Classify request type
  - Execute simple queries directly
  - Delegate complex tasks
  - Track progress
  - Report results

Does NOT:
  - Make architecture decisions
  - Write extensive code
  - Research unfamiliar topics
```

### Layer 2: THE_MASTER (Strategic Architect)

```yaml
Role: Strategic Decision Maker
Model: Claude Opus 4.5 (best reasoning)
Capabilities:
  - All tools available
  - Can create implementation plans
  - Can research technologies

Responsibilities:
  - Architecture decisions
  - Feature planning
  - Technology choices
  - Risk analysis
  - Multi-system coordination

Invoked When:
  - Architecture changes needed
  - Major new features
  - Technology decisions
  - Cross-system design
  - Performance concerns
```

### Layer 3: Specialists

```yaml
Role: Domain Expert
Model: Claude Sonnet 4 (good balance) or Haiku (speed)
Capabilities:
  - Domain-specific tools
  - Can implement code
  - Can run tests

Specialists:
  - BACKEND_DEV: APIs, databases, server logic
  - FRONTEND_DEV: UI, state management, UX
  - DEVOPS: Infrastructure, deployment, monitoring
  - AUTOMATION: Workflows, scheduled tasks
  - RESEARCHER: Information gathering
  - REVIEWER: Code review, QA
```

---

## Communication Flow

### Request Routing

```python
def route_request(request: str) -> str:
    """Route user request to appropriate handler."""

    if is_simple_query(request):
        # Direct execution
        return execute_directly(request)

    elif is_strategic_question(request):
        # Delegate to MASTER
        plan = delegate_to_master(request)
        return coordinate_execution(plan)

    elif is_technical_task(request):
        # Delegate to specialist
        specialist = identify_specialist(request)
        return delegate_to_specialist(specialist, request)

    else:
        # Research then route
        context = research_context(request)
        return route_request(request + context)
```

### Delegation Patterns

#### Pattern 1: Direct Execution
```
User → ASSISTANT → Execute → User
```
For: Status checks, simple queries, known commands

#### Pattern 2: Single Specialist
```
User → ASSISTANT → Specialist → ASSISTANT → User
```
For: Domain-specific tasks in one area

#### Pattern 3: Strategic Planning
```
User → ASSISTANT → MASTER → (plan) → ASSISTANT → Specialists → User
```
For: Complex features requiring architecture decisions

#### Pattern 4: Multi-Specialist
```
User → ASSISTANT → MASTER → (plan) → [Specialist A, B, C] → ASSISTANT → User
```
For: Cross-system features touching multiple domains

---

## Implementation

### 1. Agent Prompt Structure

Each agent needs a prompt file with:

```markdown
# {{AGENT_NAME}} - System Prompt

## IDENTITY
Who the agent is and what it owns

## CORE RESPONSIBILITIES
5-7 key responsibilities

## DECISION FRAMEWORK
When to act vs delegate

## COMMUNICATION
Who it receives from / sends to

## RESPONSE FORMATS
Structured output templates

## REMEMBER
Key points for the agent
```

### 2. Knowledge Base Schema

```sql
-- Agents table
CREATE TABLE agents (
    id TEXT PRIMARY KEY,
    role TEXT NOT NULL,
    status TEXT DEFAULT 'idle',
    focus TEXT,
    working_on TEXT,
    updated_at TIMESTAMP
);

-- Messages table
CREATE TABLE messages (
    id TEXT PRIMARY KEY,
    from_agent TEXT,
    to_agent TEXT,
    subject TEXT,
    content TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP
);

-- Tasks table
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    title TEXT,
    description TEXT,
    status TEXT DEFAULT 'pending',
    priority TEXT DEFAULT 'medium',
    assigned_to TEXT,
    created_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

### 3. Session Lifecycle

```python
class AgentSession:
    """Manage agent session lifecycle."""

    def __init__(self, role: str, kb_path: str):
        self.role = role
        self.kb = KnowledgeBase(kb_path)
        self.session_id = None

    def start(self, focus: str):
        """Register and start session."""
        self.kb.register_agent(self.role, focus)
        self.session_id = self.kb.start_session(self.role)

    def log(self, action: str, details: str = None):
        """Log activity."""
        self.kb.log_activity(self.session_id, action, details)

    def end(self, summary: str):
        """End session with summary."""
        self.kb.end_session(self.session_id, summary)
        self.kb.leave_agent(self.role)
```

---

## Best Practices

### For THE_ASSISTANT
- Always verify before reporting
- Use structured response formats
- Track all delegated tasks
- Don't attempt everything yourself

### For THE_MASTER
- Think long-term
- Document all decisions
- Consider trade-offs
- Create clear implementation plans

### For Specialists
- Own your domain completely
- Follow coding standards
- Update documentation
- Report blockers immediately

### For All Agents
- Use ReAct pattern for complex tasks
- Be concise but complete
- Log significant actions
- Coordinate through KB

---

## Example Implementation

### Handling "Add user authentication"

```
1. User → THE_ASSISTANT
   Request: "Add user authentication"

2. THE_ASSISTANT:
   Thought: Major feature, touches multiple systems
   Action: Delegate to THE_MASTER

3. THE_MASTER:
   Thought: Need auth architecture
   Action: Research auth patterns
   Observation: JWT + refresh tokens recommended

   Plan:
   - BACKEND_DEV: Auth endpoints, JWT handling
   - FRONTEND_DEV: Login UI, token storage
   - DEVOPS: Secure configuration

4. THE_ASSISTANT coordinates:
   - Assigns BACKEND_DEV first (API before UI)
   - Monitors progress
   - Assigns FRONTEND_DEV when API ready
   - Assigns DEVOPS for security config

5. Each specialist implements their part

6. THE_ASSISTANT → User:
   "Authentication implemented:
   - JWT-based auth with refresh tokens
   - Login/logout/register endpoints
   - Secure token storage
   - Password requirements configured"
```

---

## Files Needed

```
project/
├── agents/
│   ├── README.md                    # Agent roster & overview
│   ├── AGENT_SYSTEM.md              # Architecture documentation
│   └── prompts/
│       ├── THE_ASSISTANT.md         # Supervisor prompt
│       ├── THE_MASTER.md            # Architect prompt
│       ├── BACKEND_DEV_AGENT.md     # Backend specialist
│       ├── FRONTEND_DEV_AGENT.md    # Frontend specialist
│       ├── DEVOPS_AGENT.md          # DevOps specialist
│       └── [OTHER]_AGENT.md         # Other specialists
│
└── .agents/
    ├── project_kb.db                # SQLite knowledge base
    ├── agent_tools.py               # CLI tools
    ├── sessions/                    # Handoff reports
    └── logs/                        # Activity logs
```

---

## Quick Commands

```bash
# Initialize agents
./init_agents.sh /path/to/project full

# Register agent
python3 .agents/agent_tools.py register BACKEND_DEV --focus "API development"

# Start session
python3 .agents/agent_tools.py session start BACKEND_DEV

# Send message
python3 .agents/agent_tools.py msg send BACKEND_DEV ASSISTANT "Done" "Auth complete"

# End session
python3 .agents/agent_tools.py session end SESSION_ID "Completed auth endpoints"
```

---

## Related Patterns

- **Orchestrator-Workers** (`orchestrator_template.py`) - Simpler coordination
- **Hierarchical** (`hierarchical_template.py`) - Individual task delegation
- **Routing** (`routing_template.py`) - Request classification
- **Planning (ReAct)** (`react_planning_template.py`) - Multi-step reasoning

---

*Hierarchical Agent System - Architecture Pattern for Multi-Agent Collaboration*
