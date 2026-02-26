# Project Status Command

Get comprehensive project status from the Knowledge Base API.

## Full Team Dashboard
```bash
curl -s -H "X-API-Key: $API_KEY" http://localhost:5050/kb/team/status | python3 -m json.tool
```

Returns: active agents, locked files, task summary, active tasks, available tasks, recent work logs, recent activity.

## Quick Status Checks

```bash
# Active agents
curl -s -H "X-API-Key: $API_KEY" http://localhost:5050/kb/agents | python3 -m json.tool

# Pending tasks
curl -s -H "X-API-Key: $API_KEY" "http://localhost:5050/kb/tasks?status=pending" | python3 -m json.tool

# In-progress tasks
curl -s -H "X-API-Key: $API_KEY" "http://localhost:5050/kb/tasks?status=in_progress" | python3 -m json.tool

# Recent decisions
curl -s -H "X-API-Key: $API_KEY" http://localhost:5050/kb/decisions | python3 -m json.tool

# Recent activity
curl -s -H "X-API-Key: $API_KEY" http://localhost:5050/kb/activity | python3 -m json.tool

# Skill matrix
curl -s -H "X-API-Key: $API_KEY" http://localhost:5050/kb/skills/matrix | python3 -m json.tool
```

## Health Check
```bash
# API health
curl -s http://localhost:5050/health | python3 -m json.tool

# KB resume (full context)
curl -s -H "X-API-Key: $API_KEY" http://localhost:5050/kb/resume | python3 -m json.tool
```

## Git Status
```bash
git status
git log --oneline -10
```

## Quick Actions

When user asks for "status":
1. Call GET /kb/team/status
2. Call GET /health
3. Run git status
4. Summarize findings in a clear report
