# Agent Management

Manage agents via the Knowledge Base API.

## Register Agent
```bash
curl -X POST http://localhost:5050/kb/agents/$AGENT_ID \
  -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" \
  -d '{"role": "{{role}}", "focus": "{{focus}}", "repo": "{{repo}}", "capabilities": []}'
```

## List Active Agents
```bash
curl -s -H "X-API-Key: $API_KEY" http://localhost:5050/kb/agents | python3 -m json.tool
```

## Team Dashboard
```bash
curl -s -H "X-API-Key: $API_KEY" http://localhost:5050/kb/team/status | python3 -m json.tool
```

## Update Agent Status
```bash
curl -X PUT http://localhost:5050/kb/agents/$AGENT_ID \
  -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" \
  -d '{"status": "busy", "working_on": "description", "working_on_task_id": "T###", "locked_files": ["file1.py"]}'
```

## Send Heartbeat
```bash
curl -X POST http://localhost:5050/kb/agents/$AGENT_ID/heartbeat -H "X-API-Key: $API_KEY"
```

## Deregister Agent
```bash
curl -X DELETE http://localhost:5050/kb/agents/$AGENT_ID -H "X-API-Key: $API_KEY"
```

## Skill Matrix
```bash
# View all agent skills
curl -s -H "X-API-Key: $API_KEY" http://localhost:5050/kb/skills/matrix | python3 -m json.tool

# View one agent's skills
curl -s -H "X-API-Key: $API_KEY" http://localhost:5050/kb/agents/$AGENT_ID/skills | python3 -m json.tool
```

## Quick Actions

Based on user request:
- "register as X" → POST /kb/agents/X with role
- "list agents" or "who's online" → GET /kb/agents
- "team status" → GET /kb/team/status
- "update status" → PUT /kb/agents/X
- "leave" or "sign off" → DELETE /kb/agents/X
