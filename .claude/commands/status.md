# Project Status Command

Get comprehensive project status overview.

## Quick Status

Run these commands to get project status:

```bash
# Agent status
python3 .agents/tools/agent_registry.py list

# Task status
python3 .agents/tools/agent_registry.py task list

# Recent messages
python3 .agents/tools/agent_registry.py msg list

# Git status
git status

# Recent commits
git log --oneline -10
```

## Full Status Report

Generate a complete status report by running all of the above and summarizing:

1. **Agents Online**: Who is currently registered
2. **Active Tasks**: Tasks in progress
3. **Pending Tasks**: Tasks not yet started
4. **Blocked Tasks**: Tasks with blockers
5. **Recent Activity**: Last 5 commits
6. **Uncommitted Changes**: Files modified but not committed

## Health Checks

```bash
# Check if agent database exists
ls -la .agents/*.db

# Check recent session logs
ls -la .agents/sessions/

# Check backup status
ls -la .agents/backups/
```

## Quick Actions

When user asks for "status" or "project status":
1. Run agent list
2. Run task list
3. Run git status
4. Summarize findings in a clear report
