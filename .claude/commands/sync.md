# KB Sync Commands

Synchronize state with the Knowledge Base and other agents.

## Check Team Status
```bash
curl -s -H "X-API-Key: $API_KEY" http://localhost:5050/kb/team/status | python3 -m json.tool
```

## Save Current Context
```bash
curl -X POST http://localhost:5050/kb/context \
  -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" \
  -d '{"type": "focus", "key": "current_topic", "content": "What you are working on"}'
```

## Send Message to Another Agent
```bash
curl -X POST http://localhost:5050/kb/messages \
  -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" \
  -d '{"from_agent": "YOUR_AGENT", "to_agent": "TARGET_AGENT",
       "message_type": "update", "subject": "Status Update",
       "content": "Message content here"}'
```

## Check Messages
```bash
curl -s -H "X-API-Key: $API_KEY" "http://localhost:5050/kb/messages?to_agent=YOUR_AGENT" | python3 -m json.tool
```

## Record Decision
```bash
curl -X POST http://localhost:5050/kb/decisions \
  -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" \
  -d '{"title": "Decision title", "context": "Why this was needed",
       "decision": "What was decided", "rationale": "Why this choice",
       "category": "architecture", "made_by": "YOUR_AGENT"}'
```

## Post-Task Health Check
```bash
curl -X POST http://localhost:5050/kb/health-check \
  -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" \
  -d '{"agent_id": "YOUR_AGENT", "task_id": "T###",
       "checks": [{"type": "task_complete"}, {"type": "files_unlocked"},
                   {"type": "work_logged"}, {"type": "retrospective"}]}'
```

## Git Sync
```bash
git push
git pull
git status
```

## Quick Actions
- "sync" → GET /kb/team/status
- "save context" → POST /kb/context
- "message AGENT" → POST /kb/messages
- "health check" → POST /kb/health-check
