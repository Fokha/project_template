# Multi-Agent System Architecture v2.0

## Overview

This template provides a **hierarchical multi-agent system** where specialized AI agents work together on complex projects. The architecture follows a clear chain of command: User → Assistant → Master → Specialists.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    HIERARCHICAL AGENT ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   LAYER 1: USER INTERFACE                                               │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                      THE_ASSISTANT                               │  │
│   │  • Receives all user requests                                    │  │
│   │  • Handles simple queries directly                               │  │
│   │  • Delegates complex tasks                                       │  │
│   │  • Reports back to user                                          │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                │                                         │
│   LAYER 2: STRATEGIC                                                    │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                       THE_MASTER                                 │  │
│   │  • Architecture decisions                                        │  │
│   │  • Feature planning                                              │  │
│   │  • Technology choices                                            │  │
│   │  • Cross-system coordination                                     │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                │                                         │
│   LAYER 3: IMPLEMENTATION                                               │
│   ┌──────────┬──────────┬──────────┬──────────┬──────────┐            │
│   │ BACKEND  │ FRONTEND │ AUTOMATION│  DEVOPS  │RESEARCHER│            │
│   │   DEV    │   DEV    │          │          │          │            │
│   └──────────┴──────────┴──────────┴──────────┴──────────┘            │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Agent Types

### 1. THE_ASSISTANT (Supervisor)

**Role:** User's direct interface and task router

**Responsibilities:**
- Parse user requests and determine action
- Execute simple queries directly
- Delegate complex tasks to MASTER or specialists
- Track task progress across all agents
- Report final results to user

**Decision Matrix:**
```
User Request Type          → Action
─────────────────────────────────────
Simple status query        → Execute directly
Known technical task       → Delegate to specialist
Strategic question         → Delegate to MASTER
Unknown/complex            → Research then delegate
```

### 2. THE_MASTER (Strategic Architect)

**Role:** Strategic decision-maker and planner

**Responsibilities:**
- Design system architecture
- Plan multi-step feature implementations
- Make technology and framework choices
- Analyze trade-offs and risks
- Coordinate cross-system changes
- Create implementation plans for specialists

**Invoked When:**
- Architecture changes needed
- New major features
- Technology decisions required
- Cross-system design work
- Performance/scalability concerns

### 3. BACKEND_DEV (Backend Specialist)

**Role:** Backend code and API development

**Responsibilities:**
- Implement API endpoints
- Database operations
- Server-side business logic
- Backend testing
- API documentation

### 4. FRONTEND_DEV (Frontend Specialist)

**Role:** User interface development

**Responsibilities:**
- UI component development
- State management
- Frontend testing
- UX implementation
- Cross-platform support

### 5. AUTOMATION (Workflow Specialist)

**Role:** Automation and workflow development

**Responsibilities:**
- Workflow automation
- Scheduled tasks
- Notification systems
- Integration pipelines
- Event-driven automation

### 6. DEVOPS (Infrastructure Specialist)

**Role:** Infrastructure and deployment

**Responsibilities:**
- Cloud infrastructure
- Docker/containerization
- CI/CD pipelines
- Monitoring and alerting
- Backup and recovery
- Security configuration

### 7. RESEARCHER (Research Specialist)

**Role:** Information gathering and analysis

**Responsibilities:**
- Technology research
- Best practices analysis
- Competitor analysis
- Documentation review
- Proof of concept evaluation

### 8. REVIEWER (Quality Specialist)

**Role:** Code review and quality assurance

**Responsibilities:**
- Code review
- Security vulnerability detection
- Performance review
- Standards compliance
- Test coverage analysis

---

## Communication Protocol

### Message Format

```json
{
  "message_id": "msg_001",
  "from_agent": "THE_ASSISTANT",
  "to_agent": "BACKEND_DEV",
  "task_id": "T001",
  "type": "task_assignment",
  "priority": "high",
  "content": {
    "action": "implement_endpoint",
    "description": "Add user authentication endpoint",
    "context": "...",
    "deliverables": ["auth.py", "tests/test_auth.py"]
  },
  "timestamp": "2026-01-12T10:00:00Z"
}
```

### Message Types

| Type | Description | From → To |
|------|-------------|-----------|
| `task_assignment` | Assign new task | ASSISTANT/MASTER → Any |
| `task_update` | Progress update | Any → ASSISTANT |
| `task_complete` | Task finished | Any → ASSISTANT |
| `task_blocked` | Task is blocked | Any → ASSISTANT |
| `question` | Need clarification | Any → Any |
| `answer` | Response to question | Any → Any |
| `strategic_request` | Need architecture decision | ASSISTANT → MASTER |
| `implementation_plan` | Plan for specialists | MASTER → ASSISTANT |

---

## Task Lifecycle

```
┌─────────────┐
│  RECEIVED   │ ◄── User request arrives
└──────┬──────┘
       │ classify
       ▼
┌─────────────┐
│   ROUTED    │ ◄── Determine handler (direct/specialist/master)
└──────┬──────┘
       │ assign
       ▼
┌─────────────┐
│ IN_PROGRESS │◄──────┐
└──────┬──────┘       │
       │              │ blocked/needs_info
       ▼              │
┌─────────────┐       │
│  IN_REVIEW  │───────┘
└──────┬──────┘  issues_found
       │ approved
       ▼
┌─────────────┐
│  COMPLETED  │ ◄── Report to user
└─────────────┘
```

### Task Status Values

| Status | Meaning |
|--------|---------|
| `received` | Request received, not yet classified |
| `routed` | Handler determined, being assigned |
| `in_progress` | Agent actively working |
| `blocked` | Waiting on external dependency |
| `in_review` | Work complete, being verified |
| `completed` | Finished and reported |

---

## Delegation Patterns

### Pattern 1: Direct Execution
```
User → THE_ASSISTANT → Execute → User
```
For simple queries that don't require specialist knowledge.

### Pattern 2: Single Specialist
```
User → THE_ASSISTANT → Specialist → THE_ASSISTANT → User
```
For domain-specific tasks within one area.

### Pattern 3: Strategic Planning
```
User → THE_ASSISTANT → THE_MASTER → (plan) → THE_ASSISTANT → Specialists → THE_ASSISTANT → User
```
For complex features requiring architecture decisions.

### Pattern 4: Multi-Specialist Coordination
```
User → THE_ASSISTANT → THE_MASTER → (plan) → [Specialist A, Specialist B, ...] → THE_ASSISTANT → User
```
For cross-system features touching multiple domains.

---

## Agent Configuration

```yaml
# agent_config.yaml

agents:
  the_assistant:
    model: "claude-opus-4-5-20251101"
    role: "supervisor"
    capabilities:
      - task_routing
      - status_reporting
      - user_communication
    tools:
      - Read
      - Write
      - Edit
      - Bash
      - WebSearch
      - Task
    system_prompt: "prompts/THE_ASSISTANT.md"

  the_master:
    model: "claude-opus-4-5-20251101"
    role: "architect"
    capabilities:
      - architecture_design
      - technology_decisions
      - feature_planning
    tools:
      - Read
      - Write
      - Edit
      - Bash
      - WebSearch
      - Task
    system_prompt: "prompts/THE_MASTER.md"

  backend_dev:
    model: "claude-sonnet-4-5-20250929"
    role: "implementer"
    capabilities:
      - code_generation
      - api_development
      - database_operations
    tools:
      - Read
      - Write
      - Edit
      - Bash
    system_prompt: "prompts/BACKEND_DEV_AGENT.md"

  frontend_dev:
    model: "claude-sonnet-4-5-20250929"
    role: "implementer"
    capabilities:
      - ui_development
      - state_management
      - cross_platform
    tools:
      - Read
      - Write
      - Edit
      - Bash
    system_prompt: "prompts/FRONTEND_DEV_AGENT.md"

  devops:
    model: "claude-sonnet-4-5-20250929"
    role: "infrastructure"
    capabilities:
      - deployment
      - containerization
      - monitoring
    tools:
      - Read
      - Write
      - Edit
      - Bash
    system_prompt: "prompts/DEVOPS_AGENT.md"

communication:
  method: "knowledge_base"
  database: ".agents/project_kb.db"
  broadcast_channel: "all_agents"

task_management:
  auto_assign: false  # ASSISTANT routes manually
  max_concurrent_per_agent: 1
  priority_levels: ["critical", "high", "medium", "low"]
```

---

## Parallel vs Sequential Execution

### CAN Run in Parallel
- Different specialists on unrelated tasks
- Reading different parts of codebase
- Independent API calls
- Separate file modifications
- Research tasks

### MUST Run Sequentially
- Tasks with dependencies
- Same file modifications
- Git operations on same branch
- Database migrations
- Deployment steps

---

## ReAct Reasoning Pattern

All agents use ReAct (Reasoning + Acting) for complex tasks:

```
Thought: I need to understand the current architecture before planning
Action: Read the existing codebase structure
Observation: Found 3 main modules: api, models, services

Thought: The user wants to add authentication, need to check dependencies
Action: Check if any auth library exists
Observation: No auth library found, need to add one

Thought: I can now plan the implementation
Final Answer: [Detailed implementation plan]
```

---

## Integration Points

### 1. Knowledge Base
All agents read/write to shared SQLite database:
```python
# Agent stores task update
INSERT INTO tasks (title, status, assigned_to) VALUES (...)

# Agent reads project context
SELECT * FROM activity_log WHERE session_id = ?
```

### 2. File-Based Communication
For cross-session handoffs:
```
.agents/sessions/
├── BACKEND_DEV_handoff_20260112.md
├── MASTER_architecture_decision_001.md
└── current_sprint.md
```

### 3. Claude Code Skills
Slash commands invoke agents:
```
/assistant <request>  → THE_ASSISTANT handles
/status              → System status check
/deploy              → DEVOPS handles
```

---

## Best Practices

### 1. Clear Task Definitions
Always include:
- What needs to be done
- Success criteria
- Files/systems affected
- Priority level

### 2. Context Sharing
- Use KB to share context between agents
- Include relevant file paths
- Reference related tasks

### 3. Error Handling
- Agents report blockers immediately
- Include what was tried
- Suggest alternative approaches

### 4. Incremental Updates
- Frequent small updates
- Log progress to session
- Don't batch completions

### 5. Decision Logging
- Record architecture decisions
- Include reasoning
- Note alternatives considered

---

## Example Workflow

### User Request: "Add user authentication"

```
1. User → THE_ASSISTANT
   Request: "Add user authentication"

2. THE_ASSISTANT analyzes:
   - This is a major feature
   - Touches backend, frontend, database
   - Needs architecture decision
   → Delegates to THE_MASTER

3. THE_MASTER plans:
   - Reviews existing auth patterns
   - Chooses JWT + session approach
   - Creates implementation plan:
     * BACKEND_DEV: API endpoints
     * FRONTEND_DEV: Login UI
     * DEVOPS: Secure configuration
   → Returns plan to THE_ASSISTANT

4. THE_ASSISTANT coordinates:
   - Assigns BACKEND_DEV first (API needed before UI)
   - Monitors progress
   - Assigns FRONTEND_DEV when API ready
   - Assigns DEVOPS for final security

5. Each specialist:
   - Implements their part
   - Reports completion
   - THE_ASSISTANT tracks progress

6. THE_ASSISTANT → User:
   - Reports completion
   - Lists what was done
   - Notes any follow-up needed
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2026-01-12 | Hierarchical architecture (ASSISTANT/MASTER/Specialists) |
| 1.0.0 | 2025-12-30 | Initial flat structure |

---

*Multi-Agent System Architecture v2.0 - Hierarchical Pattern for Complex Projects*
