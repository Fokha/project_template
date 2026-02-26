# Agent Preflight Check

Run before starting any task to check for warnings, relevant lessons, and conflicts.

## Run Preflight
```bash
curl -s -H "X-API-Key: $API_KEY" http://localhost:5050/kb/preflight/T### | python3 -m json.tool
```

## What Preflight Returns
- **warnings** — Blocking dependencies, locked files, relevant lessons
- **relevant_lessons** — Past lessons learned related to this task's keywords
- **relevant_decisions** — Architecture decisions that apply
- **locked_files** — Files currently locked by other agents
- **blocked_by** — Dependency tasks not yet completed
- **preflight_status** — `CLEAR` or `BLOCKED`

## Search Past Lessons
```bash
# By keyword
curl -s -H "X-API-Key: $API_KEY" "http://localhost:5050/kb/lessons?keyword=authentication" | python3 -m json.tool

# By tags
curl -s -H "X-API-Key: $API_KEY" "http://localhost:5050/kb/lessons?tags=bug,critical" | python3 -m json.tool
```

## After Preflight
1. Review all warnings
2. Read relevant lessons (learn from past mistakes)
3. Check if any files you need are locked
4. If BLOCKED — resolve dependencies first
5. If CLEAR — proceed with the task
