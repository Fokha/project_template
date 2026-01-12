# Definition of Done Checklist

**Run this checklist before marking ANY task complete.**

## Pre-Completion Checks

### 1. Code Quality
- [ ] File exists with **>50 lines** of production code
- [ ] Code compiles: `flutter analyze` passes
- [ ] No placeholder/TODO comments added (keep existing ones)
- [ ] All imports are valid and resolved
- [ ] Error handling included
- [ ] Follows existing naming conventions

### 2. Integration
- [ ] Exports added to barrel file (e.g., `services.dart`, `widgets.dart`)
- [ ] Dependencies added to `pubspec.yaml` if needed
- [ ] No breaking changes to existing APIs

### 3. Documentation
- [ ] CHANGELOG.md updated with new entry
- [ ] Complex logic has inline comments
- [ ] Public API documented with `///` comments

### 4. Verification
- [ ] Run `./scripts/check-status.sh` - task shows ✅
- [ ] Tested basic functionality (manual or unit test)
- [ ] No regression in existing features

## Quick Commands

```bash
# Check if task is actually done
./scripts/check-status.sh | grep T###

# Verify code compiles
flutter analyze lib/path/to/file.dart

# Check exports
grep "export" lib/services/services.dart
```

## Common Mistakes to Avoid

❌ Marking task done based on task list (lists get stale)
❌ Creating stub files (<50 lines) and marking done
❌ Forgetting to export new files
❌ Not updating CHANGELOG.md
❌ Breaking existing imports

## Task Status Definitions

| Status | Meaning |
|--------|---------|
| ✅ DONE | File exists, >50 lines, compiles, exported |
| ⚠️ PARTIAL | File exists but <50 lines (stub only) |
| ❌ MISSING | File does not exist |
| 🔄 IN PROGRESS | Currently being worked on |

## After Marking Done

1. Run preflight: `./scripts/agent-preflight.sh`
2. Commit changes: `git add . && git commit -m "Complete T###: description"`
3. Update AGENT_COMMS.md task status (if using)
