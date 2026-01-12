# Messaging Commands

Inter-agent communication system.

## List Messages

```bash
python3 .agents/tools/agent_registry.py msg list
```

## Send Message

```bash
python3 .agents/tools/agent_registry.py msg send FROM_AGENT TO_AGENT "Subject" "Message content"
```

## Broadcast Message

Send to all agents:
```bash
python3 .agents/tools/agent_registry.py msg broadcast FROM_AGENT "Subject" "Message content"
```

## Read Message

```bash
python3 .agents/tools/agent_registry.py msg read MESSAGE_ID
```

## Message Types

- **Direct**: Agent to agent
- **Broadcast**: To all agents
- **Task Assignment**: When assigning tasks
- **Status Update**: Progress notifications
- **Alert**: Urgent notifications

## Quick Actions

Based on user request:
- "check messages" → List all messages
- "send to X: Y" → Send message Y to agent X
- "broadcast: Y" → Broadcast message Y to all
- "read message X" → Read specific message
