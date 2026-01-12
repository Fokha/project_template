# Task Management Commands

Create, track, and manage tasks.

## List Tasks

```bash
python3 .agents/tools/agent_registry.py task list
```

## Add Task

```bash
python3 .agents/tools/agent_registry.py task add "Task title" ASSIGNED_TO --priority high|medium|low --from CREATOR
```

## Mark Task Done

Simple completion:
```bash
python3 .agents/tools/agent_registry.py task done TASK_ID
```

Full completion workflow:
```bash
python3 .agents/tools/agent_registry.py task complete TASK_ID SESSION_ID ROLE "Summary"
```

## Assign Task

```bash
python3 .agents/tools/agent_registry.py task assign TASK_ID ASSIGNED_TO --from FROM_AGENT
```

## Update Status

```bash
python3 .agents/tools/agent_registry.py task status TASK_ID open|in_progress|done|blocked
```

## Task Assignment Rules

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
| Unclear | ORCHESTRATOR |

## Quick Actions

Based on user request:
- "list tasks" → Show all tasks
- "add task: X" → Create task with title X
- "done TASK_ID" → Mark task complete
- "assign TASK_ID to X" → Assign task to agent X
