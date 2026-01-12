# Session Management Commands

Manage agent work sessions.

## Start Session

```bash
python3 .agents/tools/agent_registry.py session start ROLE
```

**Important**: Save the returned SESSION_ID as `$SID` for use in other commands.

## Log Activity

```bash
python3 .agents/tools/agent_registry.py session log SESSION_ID "Description of what was done"
```

## End Session

```bash
python3 .agents/tools/agent_registry.py session end SESSION_ID "Summary of session work"
```

## List Sessions

```bash
python3 .agents/tools/agent_registry.py session list
```

## Session Workflow

1. **Start**: Begin session and get SESSION_ID
2. **Log**: Record important actions throughout
3. **End**: Close session with summary

## Quick Actions

Based on user request:
- "start session as X" → Run session start with role X, tell user the SESSION_ID
- "log: Y" → Run session log with the message Y
- "end session" → Run session end with summary
- "list sessions" → Show all sessions
