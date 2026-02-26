# Task Management

Create, track, and manage tasks via the Knowledge Base API.

## List Tasks
```bash
# All active tasks
curl -s -H "X-API-Key: $API_KEY" "http://localhost:5050/kb/tasks?status=pending" | python3 -m json.tool

# By assignee
curl -s -H "X-API-Key: $API_KEY" "http://localhost:5050/kb/tasks?assigned_to=AGENT_NAME" | python3 -m json.tool

# By priority
curl -s -H "X-API-Key: $API_KEY" "http://localhost:5050/kb/tasks?priority=high" | python3 -m json.tool
```

## Create Task
```bash
curl -X POST http://localhost:5050/kb/tasks \
  -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" \
  -d '{"title": "Task title", "description": "Details", "assigned_to": "AGENT", "priority": "medium", "status": "backlog"}'
```

## Update Task
```bash
# Start working
curl -X PUT http://localhost:5050/kb/tasks/T### \
  -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" \
  -d '{"status": "in_progress", "assigned_to": "AGENT"}'

# Mark done
curl -X PUT http://localhost:5050/kb/tasks/T### \
  -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" \
  -d '{"status": "done"}'
```

## Preflight Check (before starting a task)
```bash
curl -s -H "X-API-Key: $API_KEY" http://localhost:5050/kb/preflight/T### | python3 -m json.tool
```

## Check Conflicts
```bash
curl -s -H "X-API-Key: $API_KEY" http://localhost:5050/kb/tasks/T###/conflicts | python3 -m json.tool
```

## Task Statuses
| Status | Meaning |
|--------|---------|
| `backlog` | Not started |
| `pending` | Ready to work on |
| `in_progress` | Being worked on |
| `done` | Completed |
| `cancelled` | No longer needed |

## Quick Actions

Based on user request:
- "list tasks" → GET /kb/tasks
- "add task: X" → POST /kb/tasks
- "start T###" → PUT /kb/tasks/T### status=in_progress
- "done T###" → PUT /kb/tasks/T### status=done
- "preflight T###" → GET /kb/preflight/T###
