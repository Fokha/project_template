# Messaging Commands

Send and receive inter-agent messages via the Knowledge Base API.

## List Messages
```bash
# All recent messages
curl -s -H "X-API-Key: $API_KEY" http://localhost:5050/kb/messages | python3 -m json.tool

# Messages for a specific agent
curl -s -H "X-API-Key: $API_KEY" "http://localhost:5050/kb/messages?to_agent=YOUR_AGENT" | python3 -m json.tool

# Messages about a task
curl -s -H "X-API-Key: $API_KEY" "http://localhost:5050/kb/messages?task_id=T###" | python3 -m json.tool
```

## Send Message
```bash
curl -X POST http://localhost:5050/kb/messages \
  -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" \
  -d '{"from_agent": "YOUR_AGENT", "to_agent": "TARGET_AGENT",
       "message_type": "update", "subject": "Subject line",
       "content": "Message body", "task_id": "T###"}'
```

## Broadcast Message
```bash
# Send to all agents (to_agent = null)
curl -X POST http://localhost:5050/kb/messages \
  -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" \
  -d '{"from_agent": "YOUR_AGENT", "message_type": "announcement",
       "subject": "Important Update", "content": "Message for all agents"}'
```

## Message Types
| Type | Use For |
|------|---------|
| `request` | Asking another agent to do something |
| `response` | Replying to a request |
| `update` | Status update on a task |
| `announcement` | Broadcast to all agents |

## Quick Actions
- "list messages" → GET /kb/messages
- "message AGENT: content" → POST /kb/messages
- "broadcast: content" → POST /kb/messages (to_agent=null)
- "check messages" → GET /kb/messages?to_agent=YOUR_AGENT
