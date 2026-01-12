# Preflight Check

Run before starting any significant task.

## Environment Check

```bash
# Check services are running
curl -s http://localhost:{{PORT}}/health > /dev/null && echo "✓ API running" || echo "✗ API down"

# Check git status
git status --short

# Check current branch
git branch --show-current

# Check for uncommitted changes
git diff --stat
```

## Pre-Task Checklist

- [ ] Services running
- [ ] On correct git branch
- [ ] No uncommitted changes (or changes are intentional)
- [ ] Understand the task requirements
- [ ] Identified files to modify
- [ ] Tests exist for affected code

## Quick Start

If services not running:
```bash
./scripts/dev-start.sh
```

## Context Questions

Before starting, answer:
1. What is the task?
2. Which files will be affected?
3. Are there tests to run?
4. Does documentation need updating?
5. Are there dependencies on other tasks?
