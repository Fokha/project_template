# Session Log Command

Generate a comprehensive report of the current session's work.

## Usage

```
/session-log [format]
```

Where `format` is optional: `summary` (default), `detailed`, or `markdown`.

## Report Contents

### 1. Session Overview
- Session start time
- Duration
- Project(s) worked on
- Primary objectives

### 2. Tasks Completed
- List all tasks accomplished
- Status of each (completed, in-progress, blocked)
- Link to relevant commits

### 3. Files Changed
- New files created
- Files modified
- Files deleted
- Total lines added/removed

### 4. Git Activity
- Commits made (hash, message, files)
- Branches created/merged
- Push/pull operations

### 5. Documentation Updated
- CHANGELOG.md entries
- README updates
- API docs
- User guides
- Code comments/docstrings

### 6. Tests
- Tests run
- Pass/fail counts
- New tests added

### 7. Issues & Blockers
- Problems encountered
- How they were resolved
- Pending issues

### 8. Next Steps
- Remaining work
- Recommendations
- Follow-up tasks

## Output Format

### Summary (Default)
```
SESSION REPORT - [Date]
━━━━━━━━━━━━━━━━━━━━━━━━

Duration: X hours Y minutes
Project: [project_name]

COMPLETED:
✅ Task 1 - Description
✅ Task 2 - Description

FILES: +X new, ~Y modified, -Z deleted
COMMITS: N commits pushed
TESTS: X/Y passed

NEXT STEPS:
→ Follow-up task 1
→ Follow-up task 2
```

### Detailed
Includes full file lists, commit details, code snippets.

### Markdown
Exportable markdown file for documentation.

## Auto-Generated Sections

The report automatically captures:

```
## Session: [DATE] [TIME]

### Objective
[What user asked for]

### Work Done

#### 1. [First Major Task]
- Description of work
- Files: `file1.dart`, `file2.py`
- Commit: `abc123` - "commit message"

#### 2. [Second Major Task]
- Description of work
- Files: `file3.dart`
- Commit: `def456` - "commit message"

### Changes Summary

| Type | Count | Details |
|------|-------|---------|
| Files Created | X | list... |
| Files Modified | Y | list... |
| Files Deleted | Z | list... |
| Lines Added | +N | |
| Lines Removed | -M | |

### Commits

| Hash | Message | Files |
|------|---------|-------|
| abc123 | feat: Add feature | 5 |
| def456 | fix: Fix bug | 2 |

### Documentation Updated

- [x] CHANGELOG.md - v1.2.3 release notes
- [x] README.md - Added new feature section
- [x] API_REFERENCE.md - New endpoint docs
- [ ] USER_MANUAL.md - Pending

### Tests

- Total: X tests
- Passed: Y ✅
- Failed: Z ❌
- New: N tests added

### Issues Encountered

1. **Issue**: Description
   **Resolution**: How it was fixed

### Next Steps

1. [ ] Pending task 1
2. [ ] Pending task 2
3. [ ] Recommendation

### Session Stats

- Duration: X hours Y minutes
- Tokens used: ~N
- Tools called: M
```

## Save Report

Reports can be saved to:
- `docs/session-logs/YYYY-MM-DD-HH-MM.md`
- `SESSION_LOG.md` (overwrite current)
- Clipboard (for pasting elsewhere)

## Examples

```
User: /session-log

Claude:
SESSION REPORT - January 18, 2026
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Duration: 2 hours 15 minutes
Project: ai_studio

COMPLETED:
✅ Applied data_layer template to AI_STUDIO
✅ Created fokha_data Dart package (23 files)
✅ Created data_layer Python module (47 files)
✅ Updated documentation (VERSION, CHANGELOG, PROJECT_STRUCTURE)
✅ Created /release skill

FILES: +72 new, ~5 modified
COMMITS: 3 commits pushed
TESTS: 30/30 Dart tests passed, Python imports verified

DOCS UPDATED:
- CHANGELOG.md (v2.3.9)
- VERSION (2.3.8 → 2.3.9)
- PROJECT_STRUCTURE.md

NEXT STEPS:
→ Integrate fokha_data with existing models
→ Add more storage implementations
→ Create migration guide
```

## Integration

Session logs can be:
- Appended to project's SESSION_HISTORY.md
- Sent to team via notification
- Used for time tracking
- Referenced in standup reports

## Commands

| Command | Description |
|---------|-------------|
| `/session-log` | Summary report |
| `/session-log detailed` | Full details |
| `/session-log markdown` | Exportable MD |
| `/session-log save` | Save to file |
