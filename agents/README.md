# Multi-Agent Infrastructure for Claude Code

Project-agnostic agent system for Claude Code multi-agent collaboration.
Version: 2.0.0
Last Updated: January 2026

---

## Agent Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       AGENT HIERARCHY PATTERN                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│                            👤 USER                                       │
│                                │                                         │
│                                │ Natural language                        │
│                                ▼                                         │
│                    ┌─────────────────────┐                              │
│                    │   THE_ASSISTANT     │                              │
│                    │    (Supervisor)     │                              │
│                    │  ─────────────────  │                              │
│                    │  • Direct commands  │                              │
│                    │  • Status reports   │                              │
│                    │  • Task delegation  │                              │
│                    └──────────┬──────────┘                              │
│                               │                                          │
│            ┌──────────────────┼──────────────────┐                      │
│            │                  │                  │                      │
│            ▼                  ▼                  ▼                      │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                │
│   │   MASTER    │    │   Direct    │    │   Direct    │                │
│   │  (Architect)│    │  Execution  │    │   Queries   │                │
│   └──────┬──────┘    └─────────────┘    └─────────────┘                │
│          │                                                               │
│          │ Delegates implementation                                      │
│          │                                                               │
│   ┌──────┴──────┬───────────┬───────────┐                              │
│   ▼             ▼           ▼           ▼                              │
│ ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐                         │
│ │SPECIAL │  │SPECIAL │  │SPECIAL │  │SPECIAL │                         │
│ │  IST_1 │  │  IST_2 │  │  IST_3 │  │  IST_N │                         │
│ │────────│  │────────│  │────────│  │────────│                         │
│ │  Core  │  │ Domain │  │ Domain │  │ Domain │                         │
│ │  Code  │  │   A    │  │   B    │  │   C    │                         │
│ └────────┘  └────────┘  └────────┘  └────────┘                         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Initialize Any Project
```bash
./init_agents.sh /path/to/project [team_type]

# Team types:
# - full:       ASSISTANT + MASTER + 5 SPECIALISTS
# - backend:    ASSISTANT + BACKEND_DEV + DEVOPS + REVIEWER
# - frontend:   ASSISTANT + FRONTEND_DEV + BACKEND_DEV + REVIEWER
# - research:   ASSISTANT + MASTER + RESEARCHER + REVIEWER
# - automation: ASSISTANT + AUTOMATION + DEVOPS + BACKEND_DEV
# - minimal:    ASSISTANT + BACKEND_DEV + REVIEWER
# - docs:       ASSISTANT + RESEARCHER + DOCUMENTATION
# - custom:     Specify your own agents
```

### Directory Structure Created
```
project/
├── .agents/
│   ├── project_kb.db      # SQLite: agents, tasks, messages, sessions
│   ├── agent_tools.py     # CLI for registration, messaging, tasks
│   ├── QUICK_PROMPT.md    # Agent quick reference
│   ├── sessions/          # Handoff reports
│   └── logs/              # Activity logs
│
├── agents/
│   ├── README.md          # This file
│   ├── AGENT_SYSTEM.md    # Architecture documentation
│   └── prompts/           # Agent prompt files
│       ├── THE_ASSISTANT.md
│       ├── THE_MASTER.md
│       └── [SPECIALIST]_AGENT.md
```

---

## Agent Roles

### Core Agents (Always Present)

| Agent | Role | Emoji | Prompt File |
|-------|------|-------|-------------|
| **THE_ASSISTANT** | User Interface | 🎯 | `prompts/THE_ASSISTANT.md` |
| **THE_MASTER** | Strategic Architect | 🏛️ | `prompts/THE_MASTER.md` |

### Specialist Agents (Domain-Specific)

| Agent | Role | Emoji | Prompt File |
|-------|------|-------|-------------|
| **BACKEND_DEV** | Backend/API | 🐍 | `prompts/BACKEND_DEV_AGENT.md` |
| **FRONTEND_DEV** | Frontend/UI | 📱 | `prompts/FRONTEND_DEV_AGENT.md` |
| **AUTOMATION** | Workflow Automation | ⚡ | `prompts/AUTOMATION_AGENT.md` |
| **DEVOPS** | Infrastructure | 🚀 | `prompts/DEVOPS_AGENT.md` |
| **RESEARCHER** | Research & Analysis | 🔬 | `prompts/RESEARCHER_AGENT.md` |
| **REVIEWER** | Code Review & QA | 👁️ | `prompts/REVIEWER_AGENT.md` |
| **DOCUMENTATION** | Docs & Guides | 📚 | `prompts/DOCUMENTATION_AGENT.md` |

---

## Agent Responsibilities

### THE_ASSISTANT (Supervisor)
```
Level:      Top-level (user-facing)
Brain:      Claude Code (Opus 4.5 / Sonnet)

Purpose: User's direct command interface

Capabilities:
├── Execute commands across all systems
├── Generate status reports
├── Answer questions about any component
├── Delegate complex tasks to specialists
└── Track progress on ongoing work

Does NOT:
├── Make architectural decisions (→ MASTER)
├── Write extensive code (→ Specialists)
└── Research unfamiliar topics (→ RESEARCHER)
```

### THE_MASTER (Strategic Architect)
```
Level:      Strategic (above specialists)
Brain:      Claude Code (Opus 4.5 / Sonnet)

Purpose: Strategic decision-maker for architecture and design

Capabilities:
├── Design system architecture
├── Plan new features across components
├── Make technology choices
├── Conduct research and analysis
└── Orchestrate multi-agent implementations

Invoked For:
├── Architecture changes
├── Major features
├── Technology decisions
└── Cross-system design
```

### Specialists
```
Level:      Implementation
Brain:      Claude Code (Sonnet / Haiku)

Purpose: Domain-specific implementation

Each specialist:
├── Owns specific codebase area
├── Follows domain best practices
├── Coordinates with related agents
└── Reports completion to supervisor
```

---

## Communication Protocol

### Task Delegation Flow

```
User Request
     │
     ▼
THE_ASSISTANT
     │
     ├──► Simple query? ──► Execute directly, return result
     │
     ├──► Strategic decision? ──► Delegate to MASTER
     │                                   │
     │                                   ▼
     │                            MASTER analyzes
     │                                   │
     │                                   ▼
     │                            Delegates to specialists
     │
     └──► Technical task? ──► Delegate to appropriate specialist
                                   │
                                   └──► Returns completion report
```

### Inter-Agent Communication

| From | To | Channel | Example |
|------|----|---------|---------|
| THE_ASSISTANT | Any | Direct delegation | "Check API health" |
| MASTER | Specialists | Task assignment | "Implement feature X" |
| Specialist | Specialist | Knowledge Base | Share context, ask questions |
| Any | THE_ASSISTANT | Status updates | Task completion |

---

## Agent Tools Commands

### Registration
```bash
python3 .agents/agent_tools.py register ROLE --focus "description"
python3 .agents/agent_tools.py list
python3 .agents/agent_tools.py status ROLE -w "current task"
python3 .agents/agent_tools.py leave ROLE --summary "done"
```

### Messaging
```bash
python3 .agents/agent_tools.py msg list
python3 .agents/agent_tools.py msg send FROM TO "Subject" "Content"
python3 .agents/agent_tools.py msg broadcast FROM "Subject" "Content"
python3 .agents/agent_tools.py msg read MSG_ID
```

### Sessions
```bash
python3 .agents/agent_tools.py session start ROLE
python3 .agents/agent_tools.py session log SID "action"
python3 .agents/agent_tools.py session end SID "summary"
python3 .agents/agent_tools.py session list
```

### Tasks
```bash
python3 .agents/agent_tools.py task list
python3 .agents/agent_tools.py task add "title" ASSIGNED_TO --priority high
python3 .agents/agent_tools.py task done TASK_ID
python3 .agents/agent_tools.py task assign TASK_ID NEW_AGENT
python3 .agents/agent_tools.py task status TASK_ID in_progress
```

---

## Agent Workflow

### Session Lifecycle

```
┌─────────────┐
│  REGISTER   │ ◄── Agent joins session
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   START     │ ◄── Begin work session
│   SESSION   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    WORK     │ ◄── Execute tasks, log progress
│             │     Check messages, coordinate
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    END      │ ◄── Summary, handoff notes
│   SESSION   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   LEAVE     │ ◄── Deregister from system
└─────────────┘
```

### On Session Start:
1. Register: `python3 .agents/agent_tools.py register ROLE`
2. Start session: `python3 .agents/agent_tools.py session start ROLE`
3. Check messages: `python3 .agents/agent_tools.py msg list`
4. Check tasks: `python3 .agents/agent_tools.py task list`

### Before Code Changes:
1. Check what others are working on (avoid duplication)
2. Check git log for recent changes
3. Claim task with status update + broadcast

### Context Management:
- At ~10% context: Run `/compact`
- At ~5% context: Create handoff report in `.agents/sessions/`, then `/compact`

### On Session End:
1. Log work: `python3 .agents/agent_tools.py session log SID "summary"`
2. End session: `python3 .agents/agent_tools.py session end SID`
3. Leave registry: `python3 .agents/agent_tools.py leave ROLE`
4. Update CHANGELOG.md if code changed

---

## Capabilities Matrix

| Capability | ASSISTANT | MASTER | BACKEND | FRONTEND | DEVOPS | AUTOMATION |
|------------|:---------:|:------:|:-------:|:--------:|:------:|:----------:|
| Read Files | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Write Files | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Run Bash | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Web Search | ✅ | ✅ | ⚪ | ⚪ | ⚪ | ⚪ |
| API Calls | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Delegate | ✅ | ✅ | ⚪ | ⚪ | ⚪ | ⚪ |
| Strategic | ⚪ | ✅ | ⚪ | ⚪ | ⚪ | ⚪ |

✅ = Primary capability | ⚪ = Not primary focus

---

## Creating Custom Agents

### Step 1: Copy Template
```bash
cp prompts/AGENT_SYSTEM_PROMPT_TEMPLATE.md prompts/MY_AGENT.md
```

### Step 2: Define Identity
- Name and role
- Core responsibilities (5-7 items)
- Domain ownership (files, systems)

### Step 3: Document Communication
- Who sends work to this agent
- Who this agent sends to
- Communication channels (HTTP, files, etc.)

### Step 4: Add Common Tasks
- Step-by-step guides for frequent tasks
- Code examples
- Response formats

### Step 5: Register Agent
- Add to this README Agent Roster
- Update `init_agents.sh` team types
- Update capabilities matrix

---

## Database Schema

### Tables in project_kb.db:
- `agents` - Registered agents (agent_id, role, status, focus, working_on)
- `messages` - Inter-agent messages (from, to, subject, content, is_read)
- `sessions` - Session logs (session_id, agent_id, started_at, summary)
- `activity_log` - Action logs (session_id, action, details)
- `tasks` - Task tracking (task_id, title, status, priority, assigned_to)

---

## Key Files

| File | Purpose |
|------|---------|
| `init_agents.sh` | Main initializer script |
| `agent_tools.py` | CLI for agent operations |
| `prompts/AGENT_SYSTEM_PROMPT_TEMPLATE.md` | Template for new agents |
| `prompts/PROMPT_STYLE_GUIDE.md` | Styling conventions |
| `AGENT_SYSTEM.md` | Architecture documentation |

---

## Best Practices

### For THE_ASSISTANT
- Always check status before reporting
- Use structured response formats
- Delegate complex tasks, don't attempt everything

### For MASTER
- Think long-term (months/years)
- Document all decisions
- Consider trade-offs before recommending

### For Specialists
- Own your domain completely
- Follow coding standards for your language
- Update documentation when making changes
- Communicate blockers immediately

### For All Agents
- Use ReAct reasoning pattern when needed
- Be concise but complete
- Verify before reporting
- Track progress with todo lists

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2026-01-12 | Updated to hierarchical pattern (ASSISTANT/MASTER/Specialists) |
| 1.0.0 | 2025-12-30 | Initial template with flat structure |

---

*Multi-Agent Infrastructure for Claude Code - Hierarchical Agent Pattern v2.0*
