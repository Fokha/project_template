# Task Completion Command

Complete a task with the full KB-integrated workflow.

## Quick Completion

```bash
AGENT="YOUR_AGENT"
TASK="T###"

# 1. Log work with retrospective
curl -X POST http://localhost:5050/kb/work-logs \
  -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" \
  -d "{\"agent_id\": \"$AGENT\", \"task_id\": \"$TASK\", \"action\": \"completed\",
       \"summary\": \"Summary of work done\",
       \"files_changed\": [\"file1.py\", \"file2.py\"],
       \"retrospective\": \"What went well and what could be improved\",
       \"lesson_learned\": \"Key takeaway for future reference\",
       \"tags\": [\"skill1\", \"skill2\"]}"

# 2. Release locks and mark done
curl -X PUT http://localhost:5050/kb/agents/$AGENT \
  -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" \
  -d '{"locked_files": [], "working_on_task_id": null}'

curl -X PUT http://localhost:5050/kb/tasks/$TASK \
  -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" \
  -d '{"status": "done"}'

# 3. Health check
curl -s -X POST http://localhost:5050/kb/health-check \
  -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" \
  -d "{\"agent_id\": \"$AGENT\", \"task_id\": \"$TASK\",
       \"checks\": [{\"type\": \"task_complete\"}, {\"type\": \"files_unlocked\"},
                     {\"type\": \"work_logged\"}, {\"type\": \"retrospective\"}]}" | python3 -m json.tool

# 4. Git commit
git add -A && git commit -m "[$TASK] Task description"
```

## Required Information

Before completing, ensure you have:
- **AGENT** — Your agent name (e.g., BACKEND_DEV, MASTER)
- **TASK** — Task ID (e.g., T001)
- **Summary** — What was accomplished
- **Retrospective** — What went well/badly
- **Lesson** — Key takeaway (auto-saved to lessons DB)

## Workflow Phases

1. Log work with retrospective → auto-captures lesson + updates skill matrix
2. Release file locks → allows other agents to edit
3. Mark task done → updates status with completion timestamp
4. Health check → verifies everything is clean
5. Git commit → persist changes with task reference
