# Definition of Done Checklist

**Run this checklist before marking ANY task complete.**

## Pre-Completion Checks

### 1. Code Quality
- [ ] Code compiles/runs without errors
- [ ] No placeholder/TODO comments added (keep existing ones)
- [ ] All imports are valid and resolved
- [ ] Error handling included
- [ ] Follows existing naming conventions

### 2. Integration
- [ ] No breaking changes to existing APIs
- [ ] Dependencies added if needed
- [ ] Exports/barrel files updated

### 3. Documentation
- [ ] CHANGELOG.md updated with new entry
- [ ] Complex logic has inline comments
- [ ] Public API documented

### 4. KB Verification
```bash
# Run preflight to confirm task exists
curl -s -H "X-API-Key: $API_KEY" http://localhost:5050/kb/preflight/T###

# Check for conflicts
curl -s -H "X-API-Key: $API_KEY" http://localhost:5050/kb/tasks/T###/conflicts
```

## Post-Task Workflow

```bash
# 1. Log work with retrospective
curl -X POST http://localhost:5050/kb/work-logs \
  -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" \
  -d '{"agent_id": "AGENT", "task_id": "T###", "action": "completed",
       "summary": "What was done", "files_changed": ["file1.py"],
       "retrospective": "What went well/badly",
       "lesson_learned": "Key insight for future tasks",
       "tags": ["relevant", "skills"]}'

# 2. Release file locks
curl -X PUT http://localhost:5050/kb/agents/AGENT \
  -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" \
  -d '{"locked_files": [], "working_on_task_id": null}'

# 3. Mark task done
curl -X PUT http://localhost:5050/kb/tasks/T### \
  -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" \
  -d '{"status": "done"}'

# 4. Run health check
curl -X POST http://localhost:5050/kb/health-check \
  -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" \
  -d '{"agent_id": "AGENT", "task_id": "T###",
       "checks": [{"type": "task_complete"}, {"type": "files_unlocked"},
                   {"type": "work_logged"}, {"type": "retrospective"}]}'

# 5. Commit changes
git add . && git commit -m "[T###] description of changes"
```

## Common Mistakes to Avoid

- Marking task done without logging work
- Forgetting to release file locks
- Skipping the retrospective (captures valuable lessons)
- Not running health check after completion
