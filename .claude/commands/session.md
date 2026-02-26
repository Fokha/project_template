# Session Management

Manage agent work sessions via the Knowledge Base API.

## Start Session (Register Agent)
```bash
AGENT="YOUR_AGENT_NAME"
curl -X POST http://localhost:5050/kb/agents/$AGENT \
  -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" \
  -d '{"role": "your_role", "focus": "your specialization", "repo": "repo_name"}'
```

## Check Team Status
```bash
curl -s -H "X-API-Key: $API_KEY" http://localhost:5050/kb/team/status | python3 -m json.tool
```

## Resume Previous Session
```bash
# Load full context
curl -s -H "X-API-Key: $API_KEY" http://localhost:5050/kb/resume | python3 -m json.tool

# Check your persistent memory
curl -s -H "X-API-Key: $API_KEY" http://localhost:5050/kb/memory/$AGENT | python3 -m json.tool
```

## Save Session Memory
```bash
curl -X POST http://localhost:5050/kb/memory/$AGENT \
  -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" \
  -d '{"key": "session_summary", "content": "What was accomplished this session", "category": "session"}'
```

## Log Work
```bash
curl -X POST http://localhost:5050/kb/work-logs \
  -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" \
  -d '{"agent_id": "AGENT", "task_id": "T###", "action": "completed",
       "summary": "What was done", "files_changed": ["file1.py"],
       "retrospective": "What went well/badly",
       "lesson_learned": "Key insight for future",
       "tags": ["python", "api"]}'
```

## End Session
```bash
# Release locks
curl -X PUT http://localhost:5050/kb/agents/$AGENT \
  -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" \
  -d '{"locked_files": [], "working_on_task_id": null}'

# Deregister
curl -X DELETE http://localhost:5050/kb/agents/$AGENT -H "X-API-Key: $API_KEY"
```

## Quick Actions
- "start session" → POST /kb/agents/NAME + GET /kb/resume
- "save context" → POST /kb/memory/NAME + POST /kb/context
- "end session" → Release locks + DELETE /kb/agents/NAME
- "resume" → GET /kb/resume + GET /kb/memory/NAME
