# Project Tools Index

## Knowledge Base API (http://localhost:5050/kb/)

All agent coordination goes through the KB REST API.

### Core Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/kb/resume` | GET | Full session context |
| `/kb/team/status` | GET | Team dashboard |
| `/kb/project` | GET | Project info |
| `/kb/context` | GET/POST | Session context |

### Task Management
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/kb/tasks` | GET/POST | List/create tasks |
| `/kb/tasks/<id>` | GET/PUT | Get/update task |
| `/kb/preflight/<id>` | GET | Pre-task check |
| `/kb/tasks/<id>/conflicts` | GET | Conflict detection |
| `/kb/lessons` | GET | Search lessons |

### Agent Coordination
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/kb/agents/<id>` | POST/PUT/DELETE | Register/update/deregister |
| `/kb/agents/<id>/heartbeat` | POST | Keep-alive |
| `/kb/agents/<id>/skills` | GET/POST | Skill matrix |
| `/kb/memory/<id>` | GET/POST | Persistent memory |
| `/kb/skills/matrix` | GET | All agent skills |

### Communication
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/kb/messages` | GET/POST | Inter-agent messages |
| `/kb/decisions` | GET/POST | Architecture decisions |
| `/kb/research` | GET/POST | Research entries |
| `/kb/activity` | GET/POST | Activity log |

### Work & Quality
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/kb/work-logs` | GET/POST | Work logs with retrospectives |
| `/kb/health-check` | POST | Post-task verification |
| `/kb/conversations` | POST | Save conversation points |
| `/kb/architecture` | GET/POST | Component docs |

## Scripts (./scripts/)

| Script | Description |
|--------|-------------|
| `init_project.sh` | Initialize new project from template |
| `complete_task.sh` | Full task completion workflow |
| `create_project.sh` | Create new project from template |
| `dev-start.sh` | Start tmux dev environment |
| `dev-stop.sh` | Stop tmux dev environment |

## Slash Commands

| Command | Purpose |
|---------|---------|
| `/agent` | Agent registration and management |
| `/task` | Task CRUD and preflight |
| `/status` | Team dashboard and project status |
| `/session` | Session start/resume/end |
| `/preflight` | Pre-task check (lessons, conflicts) |
| `/done` | Definition of Done checklist |
| `/complete` | Full task completion workflow |
| `/sync` | KB sync, messages, decisions |
| `/msg` | Inter-agent messaging |
| `/infra` | Infrastructure commands |
| `/backup` | Backup operations |
| `/release` | Release management |

## Agent Workflow Quick Reference

```bash
KB="http://localhost:5050/kb"

# Start working
curl -X POST "$KB/agents/NAME" -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" \
  -d '{"role": "role", "focus": "focus area"}'
curl -s -H "X-API-Key: $API_KEY" "$KB/team/status" | python3 -m json.tool

# During work
curl -s -H "X-API-Key: $API_KEY" "$KB/preflight/T###" | python3 -m json.tool
curl -X PUT "$KB/agents/NAME" -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" \
  -d '{"working_on_task_id": "T###", "locked_files": ["file1.py"]}'

# Complete task
curl -X POST "$KB/work-logs" -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" \
  -d '{"agent_id": "NAME", "task_id": "T###", "action": "completed",
       "summary": "What was done", "retrospective": "Reflection",
       "lesson_learned": "Key insight", "tags": ["skill1"]}'

# Release and mark done
curl -X PUT "$KB/agents/NAME" -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" \
  -d '{"locked_files": [], "working_on_task_id": null}'
curl -X PUT "$KB/tasks/T###" -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" \
  -d '{"status": "done"}'

# End session
curl -X DELETE "$KB/agents/NAME" -H "X-API-Key: $API_KEY"
```
