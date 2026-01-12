# Task Completion Command

Complete a task with the full 9-phase workflow.

## Usage

When user wants to complete a task, run:

```bash
./scripts/complete_task.sh TASK_ID SESSION_ID ROLE "Summary of work done"
```

## Workflow Phases

1. Pre-completion verification (tests)
2. Test generation for task
3. Git operations (add, commit)
4. Database updates (task status)
5. CHANGELOG.md update
6. Team notification
7. Backup creation
8. Sync operations (git push, cloud)
9. Completion report

## Options

- `--skip-tests` - Skip test generation/verification
- `--skip-git` - Skip git operations
- `--skip-backup` - Skip backup creation
- `--skip-sync` - Skip sync operations

## Quick Version

For a lighter completion without test generation:

```bash
python3 .agents/tools/agent_registry.py task complete TASK_ID SESSION_ID ROLE "Summary"
```

## Required Information

Before running, ensure you have:
- TASK_ID (e.g., TASK-PYTH-20260112-001)
- SESSION_ID (from session start, e.g., SESS-PYTH-20260112-001)
- ROLE (your agent role, e.g., PYTHON_ML)
- Summary (brief description of what was accomplished)

If any are missing, ask the user to provide them.
