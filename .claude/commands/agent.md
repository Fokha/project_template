# Agent Management Commands

Access to the multi-agent system tools.

## Available Commands

Run these commands to interact with the agent system:

### Register Agent
```bash
python3 .agents/tools/agent_registry.py register ROLE --focus "Your specialization"
```

### List Agents
```bash
python3 .agents/tools/agent_registry.py list
```

### Update Status
```bash
python3 .agents/tools/agent_registry.py status ROLE -w "Current task description"
```

### Leave Session
```bash
python3 .agents/tools/agent_registry.py leave ROLE --summary "Session summary"
```

## Quick Actions

Based on user request, execute the appropriate command above.

If user says:
- "register as X" → Run register command with role X
- "list agents" or "who's online" → Run list command
- "update status" → Run status command
- "leave" or "sign off" → Run leave command
