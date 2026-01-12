# Project Tools Index

All available tools and scripts in this project.

## Agent Tools (python3 .agents/tools/agent_registry.py)

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
| `task assign TASK_ID AGENT` | Assign task |
| `task status TASK_ID STATUS` | Update task status |

## Scripts (./scripts/)

| Script | Description |
|--------|-------------|
| `complete_task.sh` | Full 9-phase task completion workflow |
| `create_project.sh` | Create new project from template |
| `run_tests.sh` | Run test suite (smoke, all, coverage) |
| `sync_to_cloud.sh` | Sync to cloud server |
| `sync_to_sdcard.sh` | Sync to SD card backup |

## Slash Commands

| Command | Description |
|---------|-------------|
| `/agent` | Agent management |
| `/session` | Session management |
| `/task` | Task management |
| `/msg` | Messaging |
| `/complete` | Complete a task |
| `/status` | Project status overview |
| `/sync` | Sync operations |
| `/backup` | Backup operations |
| `/tools` | This tools index |

## Quick Reference

```bash
# Start working
python3 .agents/tools/agent_registry.py register ROLE --focus "My focus"
python3 .agents/tools/agent_registry.py session start ROLE
# Note the SESSION_ID!

# During work
python3 .agents/tools/agent_registry.py session log $SID "What I did"
python3 .agents/tools/agent_registry.py msg broadcast ROLE "Update" "Progress note"

# Complete task
./scripts/complete_task.sh TASK_ID $SID ROLE "Summary"

# End session
python3 .agents/tools/agent_registry.py session end $SID "Session summary"
python3 .agents/tools/agent_registry.py leave ROLE --summary "Done"
```
