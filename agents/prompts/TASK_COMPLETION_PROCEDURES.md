# Task Completion Procedures v2.0

**Version:** 2.0
**Updated:** 2026-01-12

Comprehensive 9-phase workflow for completing tasks, including tests, git, backup, sync, and reporting.

---

## Quick Reference

```
┌─────────────────────────────────────────────────────────────────┐
│           TASK COMPLETION WORKFLOW v2.0 (9 PHASES)              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PHASES:                                                        │
│  1. Pre-completion verification (build/tests)                   │
│  2. Test generation for completed task                          │
│  3. Git operations (add, commit)                                │
│  4. Database updates (task status, logs)                        │
│  5. CHANGELOG.md update                                         │
│  6. Team notification (broadcast)                               │
│  7. Backup creation                                             │
│  8. Sync operations (cloud, remote, git push)                   │
│  9. Completion report generation                                │
│                                                                 │
│  RECOMMENDED COMMAND (runs all 9 phases):                       │
│  ./scripts/complete_task.sh TASK_ID $SID ROLE "Summary"         │
│                                                                 │
│  QUICK COMMAND (7 phases, no test gen):                         │
│  python3 .agents/agent_tools.py task complete TASK_ID $SID ROLE "Summary"│
│                                                                 │
│  OPTIONS:                                                       │
│  --skip-tests    Skip test generation/verification              │
│  --skip-git      Skip git operations                            │
│  --skip-backup   Skip backup creation                           │
│  --skip-sync     Skip sync operations                           │
│                                                                 │
│  SESSION END:                                                   │
│  1. python3 .agents/agent_tools.py session end $SID "Summary"   │
│  2. python3 .agents/agent_tools.py leave ROLE --summary "Done"  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Pre-Completion Verification

### 1.1 Code Quality Gates

Before marking any task complete, verify:

```bash
# 1. Code compiles/runs
{{BUILD_CMD}}  # e.g., flutter build, python -m py_compile, npm run build

# 2. Tests pass
{{TEST_CMD}}   # e.g., pytest, flutter test, npm test

# 3. Linting passes
{{LINT_CMD}}   # e.g., flake8, dart analyze, eslint

# 4. No new errors in logs
tail -50 logs/*.log | grep -i error
```

### 1.2 Verification Checklist

| Check | Command | Expected |
|-------|---------|----------|
| Build | `{{BUILD_CMD}}` | Success, 0 errors |
| Tests | `{{TEST_CMD}}` | All pass |
| Lint | `{{LINT_CMD}}` | 0 warnings/errors |
| Type Check | `{{TYPE_CMD}}` | 0 errors |

### 1.3 Deliverables Verification

Confirm all expected outputs exist:

```bash
# Check files created/modified
git status

# Verify specific deliverables
ls -la {{EXPECTED_FILE_1}}
ls -la {{EXPECTED_FILE_2}}

# Check file contents are non-empty
wc -l {{EXPECTED_FILE_1}}
```

---

## Phase 2: Test Generation

### 2.1 Automatic Test Template

The completion workflow automatically generates a test template for each task:

```bash
# Test file location
tests/test_task_xxxx_xxxxxx.py

# Generated template includes:
# - Test class named after task ID
# - Placeholder tests for implementation
# - Regression test placeholder
# - TODO comments for test cases
```

### 2.2 Test Template Structure

```python
"""
Tests for Task: TASK-XXXX-XXXXXX
Generated: YYYY-MM-DD HH:MM:SS
Summary: [Task summary]
Agent: [ROLE]
"""
import pytest

class TestTASKXXXXXXXXXX:
    """Test suite for task TASK-XXXX-XXXXXX"""

    def test_task_implementation(self):
        """
        TODO: Add tests for the implemented feature

        Test cases to consider:
        - [ ] Happy path test
        - [ ] Edge cases
        - [ ] Error handling
        - [ ] Integration with existing code
        """
        assert True, "Placeholder - implement actual tests"

    def test_no_regression(self):
        """Verify no regressions introduced by this task"""
        assert True, "Placeholder - add regression tests"
```

### 2.3 Implementing Tests

After completion, review and implement actual tests:

```bash
# Run the generated test
pytest tests/test_task_xxxx_xxxxxx.py -v

# Add to CI/CD pipeline
# Update tests/conftest.py if needed
```

---

## Phase 3: Git Operations

### 3.1 Stage and Commit

```bash
# Stage all changes
git add -A

# Create commit with task context
git commit -m "[$ROLE] $TASK_ID: $SUMMARY

Task: $TASK_ID
Session: $SESSION_ID
Agent: $ROLE

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### 3.2 Commit Message Format

```
[ROLE] TASK-ID: Brief summary

Task: TASK-XXXX-XXXXXX
Session: SESS-XXXX-XXXXXX
Agent: ROLE_NAME

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Phase 4: Documentation Updates

### 4.1 Required Documentation

| Document | When to Update | What to Add |
|----------|----------------|-------------|
| `CHANGELOG.md` | Any code change | Version, date, changes |
| `README.md` | New features | Usage, examples |
| `CLAUDE.md` | Architecture changes | Updated sections |
| `API_REFERENCE.md` | New endpoints | Endpoint docs |

### 2.2 CHANGELOG Entry Format

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- **FeatureName** (`path/to/file`) - Description of new feature

### Changed
- **ComponentName** - What was modified and why

### Fixed
- **BugName** - What was broken and how it was fixed

### Files Modified
- `path/to/file1` - What changed
- `path/to/file2` - What changed
```

### 2.3 Version Bump Rules

| Change Type | Bump | Example |
|-------------|------|---------|
| Breaking change | MAJOR | 1.0.0 → 2.0.0 |
| New feature | MINOR | 1.0.0 → 1.1.0 |
| Bug fix | PATCH | 1.0.0 → 1.0.1 |
| Documentation only | None | No version change |

---

## Phase 5: Database & Task Updates

### 5.1 Mark Task Done

```bash
# 1. Update task status
python3 .agents/agent_tools.py task done TASK_ID

# 2. Log the completion
python3 .agents/agent_tools.py session log $SID "COMPLETED: [Task Title] - [Brief summary of what was done]"

# 3. Update your status
python3 .agents/agent_tools.py status YOUR_ROLE -w "Task complete, available"
```

### 3.2 Create Completion Report

For significant tasks, create a completion report:

```markdown
# TASK COMPLETION REPORT

## Task Information
- **Task ID:** TASK-XXXX-XXXXXX
- **Title:** [Task title]
- **Assigned To:** [ROLE]
- **Completed:** [DATE TIME]

## Summary
[2-3 sentences describing what was accomplished]

## Deliverables
| Deliverable | Status | Location |
|-------------|--------|----------|
| [File/Feature 1] | ✅ Done | `path/to/file` |
| [File/Feature 2] | ✅ Done | `path/to/file` |
| [Tests] | ✅ Pass | `tests/test_*.py` |

## Changes Made
### Files Created
- `path/to/new_file.py` - [Purpose]

### Files Modified
- `path/to/existing.py` - [What changed]

### Configuration Changes
- [Any config changes]

## Testing
- [x] Unit tests pass
- [x] Integration tests pass
- [x] Manual testing done
- [ ] Performance testing (if applicable)

## Documentation Updated
- [x] CHANGELOG.md
- [x] README.md (if applicable)
- [ ] API docs (if applicable)

## Known Issues / Follow-ups
- [Any known issues or future improvements]

## Verification Commands
```bash
# How to verify this task is complete
{{VERIFICATION_CMD}}
```
```

### 3.3 Notify Team

```bash
# Broadcast completion
python3 .agents/agent_tools.py msg broadcast YOUR_ROLE \
    "Task Complete: TASK_ID" \
    "Completed [task description]. Files: [list]. Ready for review."

# If specific agent needs to know
python3 .agents/agent_tools.py msg send YOUR_ROLE TARGET_AGENT \
    "Task Complete" \
    "[Details relevant to them]"
```

---

## Phase 6: Team Notification

### 6.1 Broadcast Completion

```bash
# Notify all agents
python3 .agents/agent_tools.py msg broadcast YOUR_ROLE \
    "Task Complete: TASK_ID" \
    "Completed [task description]. Files: [list]. Ready for review."

# If specific agent needs to know
python3 .agents/agent_tools.py msg send YOUR_ROLE TARGET_AGENT \
    "Task Complete" \
    "[Details relevant to them]"
```

---

## Phase 7: Backup Creation

### 7.1 Automatic Backup

The completion workflow creates a backup of critical files:

```bash
# Backup location
.agents/backups/backup_TASK_ID_TIMESTAMP.tar.gz

# Contents:
# - .agents/*.db (databases)
# - .agents/sessions/ (session logs)
# - CHANGELOG.md
# - VERSION file
```

### 7.2 Manual Backup

```bash
# Create manual backup
TIMESTAMP=$(date +%Y%m%d%H%M%S)
tar -czf .agents/backups/manual_backup_$TIMESTAMP.tar.gz \
    .agents/*.db \
    .agents/sessions/ \
    CHANGELOG.md \
    VERSION

# Cleanup old backups (keep last 10)
ls -t .agents/backups/backup_*.tar.gz | tail -n +11 | xargs rm -f
```

---

## Phase 8: Sync Operations

### 8.1 Git Push

```bash
# Check if ahead of remote
AHEAD=$(git rev-list --count @{u}..HEAD 2>/dev/null || echo "0")

# Push if there are commits
if [ "$AHEAD" -gt 0 ]; then
    git push
fi
```

### 8.2 Cloud Sync

```bash
# If sync script exists
./scripts/sync_to_cloud.sh

# Or manual rsync
rsync -avz --exclude='.git' --exclude='venv' \
    ./ user@cloud-server:/path/to/project/
```

### 8.3 SD Card / Backup Drive Sync

```bash
# If mounted and script exists
./scripts/sync_to_sdcard.sh

# Common mount points checked:
# - /Volumes/ArkOS
# - /Volumes/SDCARD
# - /Volumes/Backup
```

### 8.4 Knowledge Base Sync

```bash
# Log to KB API if available
python3 -c "
from api.utils.kb_api import log_activity
log_activity('TASK_COMPLETE', 'ROLE', 'TASK_ID: Summary')
"
```

---

## Phase 9: Review Request (If Required)

### 9.1 Request Review

```bash
# Send review request
python3 .agents/agent_tools.py msg send YOUR_ROLE REVIEWER \
    "Review Request: [Feature/Fix Name]" \
    "Please review changes in [files]. Task ID: TASK_ID. Summary: [brief]"

# Update task status
python3 .agents/agent_tools.py task status TASK_ID in_review
```

### 4.2 Review Checklist (For Reviewer)

```markdown
## Code Review Checklist

### Code Quality
- [ ] Code follows project conventions
- [ ] No obvious bugs or errors
- [ ] Error handling is appropriate
- [ ] No hardcoded values that should be configurable

### Testing
- [ ] Tests exist for new functionality
- [ ] Tests pass
- [ ] Edge cases covered

### Documentation
- [ ] Code comments where needed
- [ ] CHANGELOG updated
- [ ] README updated (if applicable)

### Security
- [ ] No exposed secrets
- [ ] Input validation present
- [ ] No SQL injection / XSS vulnerabilities

### Performance
- [ ] No obvious performance issues
- [ ] No unnecessary loops or queries
```

### 4.3 Handle Review Feedback

```bash
# If changes requested
python3 .agents/agent_tools.py task status TASK_ID in_progress
python3 .agents/agent_tools.py session log $SID "Addressing review feedback: [summary]"

# After fixing
python3 .agents/agent_tools.py msg send YOUR_ROLE REVIEWER \
    "Review Updates Complete" \
    "Addressed feedback: [list changes]. Ready for re-review."
```

---

## Phase 10: Session End Procedures

### 10.1 Standard Session End

```bash
# 1. Final log entry
python3 .agents/agent_tools.py session log $SID "SESSION END: [Summary of all work done]"

# 2. End session officially
python3 .agents/agent_tools.py session end $SID "[Comprehensive summary]"

# 3. Leave agent registry
python3 .agents/agent_tools.py leave YOUR_ROLE --summary "[What was accomplished]"
```

### 5.2 Session End Checklist

```markdown
## Session End Checklist

### Code Status
- [ ] All changes committed (or intentionally uncommitted)
- [ ] No work-in-progress left hanging
- [ ] Build still passes
- [ ] Tests still pass

### Documentation
- [ ] CHANGELOG.md updated for any changes
- [ ] Any decisions documented
- [ ] Any blockers documented

### Communication
- [ ] Team notified of completion/status
- [ ] Handoff created if work continues
- [ ] Blockers escalated if any

### Cleanup
- [ ] Temporary files removed
- [ ] Debug code removed
- [ ] Console.log/print statements removed
```

### 5.3 Session Summary Format

```
SESSION SUMMARY - [ROLE] - [DATE]
═══════════════════════════════════════

Duration: [X hours/minutes]
Session ID: [SID]

COMPLETED:
✓ [Task 1 description]
✓ [Task 2 description]

IN PROGRESS:
◐ [Task 3 - 80% complete, needs X]

BLOCKED:
✗ [Task 4 - blocked by Y]

FILES MODIFIED:
• path/to/file1.py (created)
• path/to/file2.py (modified)

DECISIONS MADE:
• Chose approach A over B because [reason]

FOLLOW-UPS NEEDED:
• [Item 1 for next session]
• [Item 2 for another agent]
```

---

## Phase 11: Handoff Procedures

### 11.1 When to Create Handoff

| Situation | Handoff Required |
|-----------|------------------|
| Context running low (<10%) | Yes - before /compact |
| Switching to different task | Yes - if returning later |
| End of work session | Yes - if work continues |
| Blocked, need different agent | Yes - with blocker details |
| Task complete, needs review | Optional - review request instead |

### 6.2 Handoff Report Template

```markdown
# HANDOFF REPORT

## Session Information
| Field | Value |
|-------|-------|
| Agent | [YOUR_ROLE] |
| Session ID | [SID] |
| Date/Time | [DATETIME] |
| Reason | [Context low / Session end / Blocked / Reassignment] |

## Work Status

### Completed
| Task | Status | Files |
|------|--------|-------|
| [Task 1] | ✅ Done | `file1.py`, `file2.py` |
| [Task 2] | ✅ Done | `file3.py` |

### In Progress
| Task | Progress | Current State |
|------|----------|---------------|
| [Task 3] | 70% | Working on [specific part] |

### Not Started
| Task | Priority | Notes |
|------|----------|-------|
| [Task 4] | High | Blocked by Task 3 |

## Current State

### Files Being Modified
```
path/to/file1.py - Line 150, implementing function X
path/to/file2.py - Adding new class Y
```

### Uncommitted Changes
```bash
git status
# [paste output]
```

### Open Issues / Blockers
1. [Issue 1]: [Description and status]
2. [Issue 2]: [Description and status]

## Context to Preserve

### Key Decisions Made
1. **[Decision]**: Chose [option] because [reason]
2. **[Decision]**: [details]

### Important Information Discovered
1. [Info 1]: [Details]
2. [Info 2]: [Details]

### Dependencies / Related Work
- [Dependency 1]: [Status]
- [Related task]: [How it relates]

## Next Steps

### Immediate (Continue From Here)
1. [Specific action to take next]
2. [Following action]
3. [After that]

### Commands to Run
```bash
# Start here
cd [directory]
[command 1]
[command 2]
```

### Files to Focus On
- `path/to/file.py` - [What to do with it]

## Continuation Prompt

Copy this to start the next session:

```
Continue as [ROLE] agent on [PROJECT_NAME].

Previous session completed:
- [Summary item 1]
- [Summary item 2]

Current task: [Task name/description]
Status: [X% complete]

Next action: [Specific next step]

Key context:
- [Critical info 1]
- [Critical info 2]

Files to focus on: [file1.py, file2.py]
```
```

### 6.3 Save and Broadcast Handoff

```bash
# Save handoff report
HANDOFF_FILE=".agents/sessions/handoff_$(date +%Y%m%d_%H%M%S)_${YOUR_ROLE}.md"
cat > $HANDOFF_FILE << 'EOF'
[PASTE HANDOFF REPORT]
EOF

# Log the handoff
python3 .agents/agent_tools.py session log $SID "Handoff created: $HANDOFF_FILE"

# Broadcast to team
python3 .agents/agent_tools.py msg broadcast YOUR_ROLE \
    "Handoff Report Created" \
    "Session ending. Handoff saved to $HANDOFF_FILE. [Brief summary]"

# If specific agent should continue
python3 .agents/agent_tools.py msg send YOUR_ROLE NEXT_AGENT \
    "Please Continue: [Task Name]" \
    "Handoff at $HANDOFF_FILE. Next step: [specific action]"
```

---

## Phase 12: Archive & Export (Optional)

### 7.1 Create Deliverables Archive

For completed features/releases:

```bash
# Create archive with project name, version, and serial
PROJECT_NAME="my_project"
VERSION=$(cat VERSION)
SERIAL=$(date +%Y%m%d%H%M%S)
ARCHIVE_NAME="${PROJECT_NAME}-v${VERSION}-${SERIAL}.zip"

# Create archive
zip -r $ARCHIVE_NAME \
    src/ \
    docs/ \
    tests/ \
    README.md \
    CHANGELOG.md \
    -x "*.pyc" -x "__pycache__/*" -x ".git/*" -x "venv/*"

echo "Created: $ARCHIVE_NAME"
```

### 7.2 Export Task History

```bash
# Export completed tasks
sqlite3 .agents/project_kb.db "SELECT * FROM tasks WHERE status='done'" > completed_tasks.csv

# Export session logs
sqlite3 .agents/project_kb.db "SELECT * FROM activity_log ORDER BY created_at DESC LIMIT 100" > recent_activity.csv
```

---

## Error Handling & Rollback

### If Task Completion Fails

```bash
# Revert task status
python3 .agents/agent_tools.py task status TASK_ID in_progress

# Log the issue
python3 .agents/agent_tools.py session log $SID "ROLLBACK: Task TASK_ID - [reason]"

# Notify team
python3 .agents/agent_tools.py msg broadcast YOUR_ROLE \
    "Task Rollback: TASK_ID" \
    "Reverting completion. Issue: [description]"
```

### If Build/Tests Break After Completion

```bash
# 1. Immediately notify
python3 .agents/agent_tools.py msg broadcast YOUR_ROLE \
    "⚠️ Build/Test Failure" \
    "After completing TASK_ID, [build/tests] failing. Investigating."

# 2. Revert task status
python3 .agents/agent_tools.py task status TASK_ID in_progress

# 3. Document the issue
python3 .agents/agent_tools.py session log $SID "ISSUE: Post-completion failure - [details]"

# 4. Fix and re-verify before marking complete again
```

---

## Special Procedures

### Context Emergency (<5%)

When context is critically low:

```bash
# 1. STOP current work
# 2. Save current state
git stash  # or commit WIP

# 3. Create emergency handoff
python3 .agents/agent_tools.py session log $SID "CONTEXT CRITICAL: Creating emergency handoff"

# 4. Quick handoff (abbreviated)
cat > .agents/sessions/emergency_handoff_$(date +%s).md << EOF
# EMERGENCY HANDOFF - [ROLE]
Context: <5%
Task: [current task]
State: [what's done, what's not]
Next: [immediate next step]
Files: [files being worked on]
EOF

# 5. Broadcast
python3 .agents/agent_tools.py msg broadcast YOUR_ROLE "Context Critical" "Emergency handoff created. Compacting."

# 6. Compact
/compact
```

### Blocked Task Procedure

```bash
# 1. Update task status
python3 .agents/agent_tools.py task status TASK_ID blocked

# 2. Document blocker
python3 .agents/agent_tools.py session log $SID "BLOCKED: TASK_ID - [blocker description]"

# 3. Notify orchestrator
python3 .agents/agent_tools.py msg send YOUR_ROLE ORCHESTRATOR \
    "Task Blocked: TASK_ID" \
    "Blocked by: [description]. Need: [what's needed to unblock]"

# 4. Move to different task or wait
```

---

## Summary Commands

### Task Complete (Unified Command - RECOMMENDED)
```bash
# Single command that does everything:
python3 .agents/agent_tools.py task complete TASK_ID $SID YOUR_ROLE "Summary"

# Or use the shell script for extended verification:
./scripts/complete_task.sh TASK_ID $SID YOUR_ROLE "Summary"
```

### Task Complete (Manual Steps)
```bash
python3 .agents/agent_tools.py task done TASK_ID && \
python3 .agents/agent_tools.py session log $SID "Done: TASK_ID" && \
python3 .agents/agent_tools.py msg broadcast ROLE "Task Done" "Completed TASK_ID"
```

### Session End (Quick)
```bash
python3 .agents/agent_tools.py session end $SID "Summary" && \
python3 .agents/agent_tools.py leave ROLE --summary "Session complete"
```

### Full Completion Flow
```bash
# 1. Verify
{{TEST_CMD}} && {{LINT_CMD}}

# 2. Complete
python3 .agents/agent_tools.py task done TASK_ID
python3 .agents/agent_tools.py session log $SID "Completed: [task]"

# 3. Document
# Update CHANGELOG.md

# 4. Notify
python3 .agents/agent_tools.py msg broadcast ROLE "Done" "[summary]"

# 5. End session
python3 .agents/agent_tools.py session end $SID "[summary]"
python3 .agents/agent_tools.py leave ROLE --summary "Done"
```
