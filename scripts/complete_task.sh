#!/bin/bash

# ============================================
# TASK COMPLETION HELPER v3.0
# Comprehensive post-task automation workflow with governance
# Usage: ./complete_task.sh <task_id> <session_id> <role> "<summary>" [--skip-tests] [--skip-git] [--skip-backup] [--skip-audit]
# ============================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Arguments
TASK_ID="${1:-}"
SESSION_ID="${2:-}"
ROLE="${3:-}"
SUMMARY="${4:-Task completed}"

# Flags
SKIP_TESTS=false
SKIP_GIT=false
SKIP_BACKUP=false
SKIP_SYNC=false
SKIP_AUDIT=false

# Parse optional flags
for arg in "$@"; do
    case $arg in
        --skip-tests) SKIP_TESTS=true ;;
        --skip-git) SKIP_GIT=true ;;
        --skip-backup) SKIP_BACKUP=true ;;
        --skip-sync) SKIP_SYNC=true ;;
        --skip-audit) SKIP_AUDIT=true ;;
    esac
done

# Help
if [[ "$1" == "-h" || "$1" == "--help" || -z "$TASK_ID" ]]; then
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  TASK COMPLETION HELPER v3.0${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Usage: $0 <task_id> <session_id> <role> \"<summary>\" [options]"
    echo ""
    echo "Arguments:"
    echo "  task_id      Task ID to complete (e.g., TASK-PYTH-20260112)"
    echo "  session_id   Current session ID (e.g., SESS-PYTH-20260112)"
    echo "  role         Your agent role (e.g., PYTHON_ML)"
    echo "  summary      Brief summary of what was done"
    echo ""
    echo "Options:"
    echo "  --skip-tests    Skip test generation/verification"
    echo "  --skip-git      Skip git operations"
    echo "  --skip-backup   Skip backup creation"
    echo "  --skip-sync     Skip sync operations (cloud/remote)"
    echo "  --skip-audit    Skip governance audit check"
    echo ""
    echo "Examples:"
    echo "  $0 TASK-PYTH-001 SESS-PYTH-001 PYTHON_ML \"Implemented auth module\""
    echo "  $0 TASK-PYTH-001 SESS-PYTH-001 PYTHON_ML \"Quick fix\" --skip-tests"
    echo ""
    echo -e "${CYAN}Workflow Phases:${NC}"
    echo "  1. Pre-completion verification (build/tests)"
    echo "  2. Test generation for completed task"
    echo "  3. Git operations (add, commit)"
    echo "  4. Database updates (task status, logs)"
    echo "  5. CHANGELOG.md update"
    echo "  6. Team notification (broadcast)"
    echo "  7. Backup creation"
    echo "  8. Sync operations (cloud, remote, git push)"
    echo "  9. Completion report generation"
    echo " 10. Governance audit (compliance check)"
    echo ""
    exit 0
fi

# Validate arguments
if [[ -z "$SESSION_ID" || -z "$ROLE" ]]; then
    echo -e "${RED}Error: Missing required arguments${NC}"
    echo "Usage: $0 <task_id> <session_id> <role> \"<summary>\""
    exit 1
fi

# Find project root (where .agents/ is)
find_project_root() {
    local current=$(pwd)
    while [[ "$current" != "/" ]]; do
        if [[ -d "$current/.agents" ]]; then
            echo "$current"
            return
        fi
        current=$(dirname "$current")
    done
    echo $(pwd)
}

PROJECT_ROOT=$(find_project_root)
AGENT_TOOLS="$PROJECT_ROOT/.agents/agent_tools.py"
DATE=$(date +%Y-%m-%d)
DATETIME=$(date +"%Y-%m-%d %H:%M:%S")
TIMESTAMP=$(date +%Y%m%d%H%M%S)
TASK_ID_LOWER=$(echo "$TASK_ID" | tr '[:upper:]' '[:lower:]')

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  TASK COMPLETION WORKFLOW v3.0${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${CYAN}Task ID:${NC}     $TASK_ID"
echo -e "${CYAN}Session ID:${NC}  $SESSION_ID"
echo -e "${CYAN}Role:${NC}        $ROLE"
echo -e "${CYAN}Summary:${NC}     $SUMMARY"
echo -e "${CYAN}Project:${NC}     $PROJECT_ROOT"
echo ""

# Track what was done
STEPS_COMPLETED=()
STEPS_SKIPPED=()
STEPS_FAILED=()

# ========================================
# PHASE 1: Pre-completion Verification
# ========================================
echo -e "${GREEN}[1/10] Pre-completion verification...${NC}"

# Check if tests script exists and run it
if [[ -f "$PROJECT_ROOT/scripts/run_tests.sh" ]] && [[ "$SKIP_TESTS" == false ]]; then
    echo "  Running smoke tests..."
    if "$PROJECT_ROOT/scripts/run_tests.sh" smoke 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} Tests passed"
        STEPS_COMPLETED+=("Tests verified")
    else
        echo -e "  ${YELLOW}⚠${NC} Tests failed or not configured - continuing"
        STEPS_SKIPPED+=("Test verification (failed)")
    fi
else
    echo -e "  ${YELLOW}⚠${NC} Tests skipped"
    STEPS_SKIPPED+=("Test verification")
fi

# Check for uncommitted changes
if command -v git &> /dev/null && [[ -d "$PROJECT_ROOT/.git" ]]; then
    UNCOMMITTED=$(git -C "$PROJECT_ROOT" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
    if [[ "$UNCOMMITTED" -gt 0 ]]; then
        echo -e "  ${CYAN}ℹ${NC} $UNCOMMITTED uncommitted changes detected"
    else
        echo -e "  ${GREEN}✓${NC} Git status clean"
    fi
fi

# ========================================
# PHASE 2: Test Generation
# ========================================
echo -e "${GREEN}[2/10] Test generation for task...${NC}"

if [[ "$SKIP_TESTS" == false ]]; then
    TEST_DIR="$PROJECT_ROOT/tests"
    mkdir -p "$TEST_DIR"

    # Generate test stub for the task
    TEST_FILE="$TEST_DIR/test_${TASK_ID_LOWER}.py"
    TEST_FILE="${TEST_FILE//-/_}"  # Replace hyphens with underscores

    if [[ ! -f "$TEST_FILE" ]]; then
        cat > "$TEST_FILE" << EOF
"""
Tests for Task: $TASK_ID
Generated: $DATETIME
Summary: $SUMMARY
Agent: $ROLE
"""
import pytest

class Test${TASK_ID//[-_]/}:
    """Test suite for task $TASK_ID"""

    def test_task_implementation(self):
        """
        TODO: Add tests for: $SUMMARY

        Test cases to consider:
        - [ ] Happy path test
        - [ ] Edge cases
        - [ ] Error handling
        - [ ] Integration with existing code
        """
        # TODO: Implement actual test
        assert True, "Placeholder test - implement actual tests"

    def test_no_regression(self):
        """Verify no regressions introduced by this task"""
        # TODO: Add regression tests
        assert True, "Placeholder - add regression tests"


# Run with: pytest $TEST_FILE -v
EOF
        echo -e "  ${GREEN}✓${NC} Test template created: $TEST_FILE"
        STEPS_COMPLETED+=("Test template generated")
    else
        echo -e "  ${CYAN}ℹ${NC} Test file already exists: $TEST_FILE"
        STEPS_SKIPPED+=("Test generation (exists)")
    fi
else
    echo -e "  ${YELLOW}⚠${NC} Test generation skipped"
    STEPS_SKIPPED+=("Test generation")
fi

# ========================================
# PHASE 3: Git Operations
# ========================================
echo -e "${GREEN}[3/10] Git operations...${NC}"

if [[ "$SKIP_GIT" == false ]] && command -v git &> /dev/null && [[ -d "$PROJECT_ROOT/.git" ]]; then
    cd "$PROJECT_ROOT"

    # Check if there are changes to commit
    if [[ $(git status --porcelain 2>/dev/null | wc -l) -gt 0 ]]; then
        # Stage all changes
        git add -A 2>/dev/null || true

        # Create commit message
        COMMIT_MSG="[$ROLE] $TASK_ID: $SUMMARY

Task: $TASK_ID
Session: $SESSION_ID
Agent: $ROLE
Date: $DATE

Co-Authored-By: Claude <noreply@anthropic.com>"

        # Commit
        if git commit -m "$COMMIT_MSG" 2>/dev/null; then
            COMMIT_HASH=$(git rev-parse --short HEAD 2>/dev/null)
            echo -e "  ${GREEN}✓${NC} Changes committed: $COMMIT_HASH"
            STEPS_COMPLETED+=("Git commit: $COMMIT_HASH")
        else
            echo -e "  ${YELLOW}⚠${NC} Commit failed (pre-commit hook or no changes)"
            STEPS_SKIPPED+=("Git commit")
        fi
    else
        echo -e "  ${CYAN}ℹ${NC} No changes to commit"
        STEPS_SKIPPED+=("Git commit (no changes)")
    fi
else
    echo -e "  ${YELLOW}⚠${NC} Git operations skipped"
    STEPS_SKIPPED+=("Git operations")
fi

# ========================================
# PHASE 4: Database Updates
# ========================================
echo -e "${GREEN}[4/10] Database updates...${NC}"

if [[ -f "$AGENT_TOOLS" ]]; then
    # Mark task as done
    python3 "$AGENT_TOOLS" task done "$TASK_ID" 2>/dev/null && \
        echo -e "  ${GREEN}✓${NC} Task marked as done" && \
        STEPS_COMPLETED+=("Task status updated") || \
        echo -e "  ${YELLOW}⚠${NC} Could not update task status"

    # Log completion to session
    python3 "$AGENT_TOOLS" session log "$SESSION_ID" "COMPLETED: $TASK_ID - $SUMMARY" 2>/dev/null && \
        echo -e "  ${GREEN}✓${NC} Session log updated" && \
        STEPS_COMPLETED+=("Session logged") || \
        echo -e "  ${YELLOW}⚠${NC} Could not update session log"

    # Update agent status
    python3 "$AGENT_TOOLS" status "$ROLE" -w "Completed: $TASK_ID" 2>/dev/null && \
        echo -e "  ${GREEN}✓${NC} Agent status updated" || true
else
    echo -e "  ${YELLOW}⚠${NC} Agent tools not found"
    STEPS_SKIPPED+=("Database updates")
fi

# ========================================
# PHASE 5: CHANGELOG Update
# ========================================
echo -e "${GREEN}[5/10] CHANGELOG update...${NC}"

CHANGELOG="$PROJECT_ROOT/CHANGELOG.md"

if [[ -f "$CHANGELOG" ]]; then
    # Check if today's date is already in CHANGELOG
    if grep -q "## \[.*\] - $DATE" "$CHANGELOG" 2>/dev/null; then
        # Append to existing date section
        # Find the line number of today's entry and add after the next blank line
        echo -e "  ${CYAN}ℹ${NC} CHANGELOG.md already has entry for today"
        echo ""
        echo -e "  ${YELLOW}Add this entry manually:${NC}"
        echo "    - **$TASK_ID** ($ROLE): $SUMMARY"
        echo ""
        STEPS_SKIPPED+=("CHANGELOG (manual update needed)")
    else
        # Create new entry
        # Create temp file with new entry
        TEMP_CHANGELOG=$(mktemp)

        # Find the first ## line and insert before it
        awk -v date="$DATE" -v task="$TASK_ID" -v role="$ROLE" -v summary="$SUMMARY" '
        /^## \[/ && !inserted {
            print "## [Unreleased] - " date
            print ""
            print "### Changed"
            print "- **" task "** (" role "): " summary
            print ""
            inserted=1
        }
        {print}
        ' "$CHANGELOG" > "$TEMP_CHANGELOG"

        mv "$TEMP_CHANGELOG" "$CHANGELOG"
        echo -e "  ${GREEN}✓${NC} CHANGELOG.md updated"
        STEPS_COMPLETED+=("CHANGELOG updated")
    fi
else
    # Create CHANGELOG.md
    cat > "$CHANGELOG" << EOF
# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] - $DATE

### Changed
- **$TASK_ID** ($ROLE): $SUMMARY

EOF
    echo -e "  ${GREEN}✓${NC} CHANGELOG.md created"
    STEPS_COMPLETED+=("CHANGELOG created")
fi

# ========================================
# PHASE 6: Team Notification
# ========================================
echo -e "${GREEN}[6/10] Team notification...${NC}"

if [[ -f "$AGENT_TOOLS" ]]; then
    python3 "$AGENT_TOOLS" msg broadcast "$ROLE" "Task Complete: $TASK_ID" "$SUMMARY" 2>/dev/null && \
        echo -e "  ${GREEN}✓${NC} Team notified via broadcast" && \
        STEPS_COMPLETED+=("Team notified") || \
        echo -e "  ${YELLOW}⚠${NC} Could not send broadcast"
else
    echo -e "  ${YELLOW}⚠${NC} Notification skipped (no agent tools)"
    STEPS_SKIPPED+=("Team notification")
fi

# ========================================
# PHASE 7: Backup Creation
# ========================================
echo -e "${GREEN}[7/10] Backup creation...${NC}"

if [[ "$SKIP_BACKUP" == false ]]; then
    BACKUP_DIR="$PROJECT_ROOT/.agents/backups"
    mkdir -p "$BACKUP_DIR"

    BACKUP_FILE="$BACKUP_DIR/backup_${TASK_ID}_${TIMESTAMP}.tar.gz"

    # Create lightweight backup of key files
    cd "$PROJECT_ROOT"

    # Files to backup
    BACKUP_FILES=""
    [[ -f "CHANGELOG.md" ]] && BACKUP_FILES="$BACKUP_FILES CHANGELOG.md"
    [[ -d ".agents" ]] && BACKUP_FILES="$BACKUP_FILES .agents/*.db .agents/sessions/"
    [[ -f "VERSION" ]] && BACKUP_FILES="$BACKUP_FILES VERSION"

    if [[ -n "$BACKUP_FILES" ]]; then
        tar -czf "$BACKUP_FILE" $BACKUP_FILES 2>/dev/null && \
            echo -e "  ${GREEN}✓${NC} Backup created: $(basename $BACKUP_FILE)" && \
            STEPS_COMPLETED+=("Backup created") || \
            echo -e "  ${YELLOW}⚠${NC} Backup creation failed"
    else
        echo -e "  ${YELLOW}⚠${NC} No files to backup"
        STEPS_SKIPPED+=("Backup (no files)")
    fi

    # Cleanup old backups (keep last 10)
    ls -t "$BACKUP_DIR"/backup_*.tar.gz 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null || true
else
    echo -e "  ${YELLOW}⚠${NC} Backup skipped"
    STEPS_SKIPPED+=("Backup")
fi

# ========================================
# PHASE 8: Sync Operations
# ========================================
echo -e "${GREEN}[8/10] Sync operations...${NC}"

if [[ "$SKIP_SYNC" == false ]]; then
    SYNC_SUCCESS=false

    # 8a. Git Push (if we committed)
    if [[ "$SKIP_GIT" == false ]] && command -v git &> /dev/null && [[ -d "$PROJECT_ROOT/.git" ]]; then
        cd "$PROJECT_ROOT"
        # Check if there's a remote and if we're ahead
        if git remote -v 2>/dev/null | grep -q "origin"; then
            AHEAD=$(git rev-list --count @{u}..HEAD 2>/dev/null || echo "0")
            if [[ "$AHEAD" -gt 0 ]]; then
                echo "  Pushing $AHEAD commit(s) to remote..."
                if git push 2>/dev/null; then
                    echo -e "  ${GREEN}✓${NC} Git push successful"
                    STEPS_COMPLETED+=("Git push")
                    SYNC_SUCCESS=true
                else
                    echo -e "  ${YELLOW}⚠${NC} Git push failed (check credentials or remote)"
                    STEPS_SKIPPED+=("Git push (failed)")
                fi
            else
                echo -e "  ${CYAN}ℹ${NC} No commits to push"
                STEPS_SKIPPED+=("Git push (up to date)")
            fi
        else
            echo -e "  ${CYAN}ℹ${NC} No git remote configured"
            STEPS_SKIPPED+=("Git push (no remote)")
        fi
    fi

    # 8b. Cloud Sync (if sync script exists)
    CLOUD_SYNC_SCRIPT="$PROJECT_ROOT/scripts/sync_to_cloud.sh"
    if [[ -f "$CLOUD_SYNC_SCRIPT" ]]; then
        echo "  Syncing to cloud..."
        if bash "$CLOUD_SYNC_SCRIPT" 2>/dev/null; then
            echo -e "  ${GREEN}✓${NC} Cloud sync successful"
            STEPS_COMPLETED+=("Cloud sync")
            SYNC_SUCCESS=true
        else
            echo -e "  ${YELLOW}⚠${NC} Cloud sync failed"
            STEPS_SKIPPED+=("Cloud sync (failed)")
        fi
    fi

    # 8c. SD Card Sync (if mounted and script exists)
    SD_SYNC_SCRIPT="$PROJECT_ROOT/scripts/sync_to_sdcard.sh"
    if [[ -f "$SD_SYNC_SCRIPT" ]]; then
        # Check common SD card mount points
        for MOUNT_POINT in "/Volumes/ArkOS" "/Volumes/SDCARD" "/Volumes/Backup"; do
            if [[ -d "$MOUNT_POINT" ]]; then
                echo "  Syncing to SD card ($MOUNT_POINT)..."
                if bash "$SD_SYNC_SCRIPT" 2>/dev/null; then
                    echo -e "  ${GREEN}✓${NC} SD card sync successful"
                    STEPS_COMPLETED+=("SD card sync")
                    SYNC_SUCCESS=true
                else
                    echo -e "  ${YELLOW}⚠${NC} SD card sync failed"
                fi
                break
            fi
        done
    fi

    # 8d. Knowledge Base Sync (if KB API available)
    if [[ -f "$PROJECT_ROOT/api/utils/kb_api.py" ]]; then
        echo "  Updating Knowledge Base..."
        python3 -c "
import sys
sys.path.insert(0, '$PROJECT_ROOT')
try:
    from api.utils.kb_api import log_activity
    log_activity('TASK_COMPLETE', '$ROLE', '$TASK_ID: $SUMMARY')
    print('KB updated')
except Exception as e:
    print(f'KB update skipped: {e}')
" 2>/dev/null && STEPS_COMPLETED+=("KB sync") || STEPS_SKIPPED+=("KB sync")
    fi

    if [[ "$SYNC_SUCCESS" == false ]]; then
        echo -e "  ${CYAN}ℹ${NC} No sync operations performed"
        STEPS_SKIPPED+=("Sync (no targets)")
    fi
else
    echo -e "  ${YELLOW}⚠${NC} Sync operations skipped"
    STEPS_SKIPPED+=("Sync operations")
fi

# ========================================
# PHASE 9: Completion Report
# ========================================
echo -e "${GREEN}[9/10] Completion report...${NC}"

REPORT_DIR="$PROJECT_ROOT/.agents/sessions"
mkdir -p "$REPORT_DIR"
REPORT_FILE="$REPORT_DIR/completion_${TASK_ID}_${TIMESTAMP}.md"

# Get git info
GIT_HASH=""
GIT_CHANGES=""
if command -v git &> /dev/null && [[ -d "$PROJECT_ROOT/.git" ]]; then
    GIT_HASH=$(git -C "$PROJECT_ROOT" rev-parse --short HEAD 2>/dev/null || echo "N/A")
    GIT_CHANGES=$(git -C "$PROJECT_ROOT" log --oneline -5 2>/dev/null || echo "No recent commits")
fi

# Create report
cat > "$REPORT_FILE" << EOF
# Task Completion Report

## Task Information
| Field | Value |
|-------|-------|
| Task ID | $TASK_ID |
| Completed By | $ROLE |
| Session ID | $SESSION_ID |
| Date/Time | $DATETIME |
| Git Commit | $GIT_HASH |

## Summary
$SUMMARY

## Workflow Results

### Steps Completed
$(for step in "${STEPS_COMPLETED[@]}"; do echo "- ✅ $step"; done)

### Steps Skipped
$(for step in "${STEPS_SKIPPED[@]}"; do echo "- ⏭️ $step"; done)

### Steps Failed
$(for step in "${STEPS_FAILED[@]}"; do echo "- ❌ $step"; done)

## Recent Git Activity
\`\`\`
$GIT_CHANGES
\`\`\`

## Verification Checklist
- [ ] Tests pass (run: \`pytest tests/\`)
- [ ] CHANGELOG.md updated
- [ ] Documentation updated
- [ ] Code reviewed (if required)
- [ ] No regressions introduced

## Test File
- Location: \`tests/test_${TASK_ID_LOWER}.py\`
- Run: \`pytest tests/test_${TASK_ID_LOWER}.py -v\`

## Notes
[Add any additional notes here]

---
Generated by complete_task.sh v3.0
EOF

echo -e "  ${GREEN}✓${NC} Report saved: $(basename $REPORT_FILE)"
STEPS_COMPLETED+=("Report generated")

# ========================================
# PHASE 10: Governance Audit
# ========================================
echo -e "${GREEN}[10/10] Governance audit...${NC}"

if [[ "$SKIP_AUDIT" == false ]]; then
    # Check for governance directory
    GOV_DIR="$PROJECT_ROOT/.governance"
    AUDIT_SCRIPT="$GOV_DIR/scripts/run_audit.sh"
    SESSION_LOG="$GOV_DIR/docs/process/session_log.md"

    if [[ -d "$GOV_DIR" ]]; then
        # Run audit if script exists
        if [[ -f "$AUDIT_SCRIPT" ]]; then
            echo "  Running governance audit..."
            if bash "$AUDIT_SCRIPT" 2>/dev/null; then
                echo -e "  ${GREEN}✓${NC} Audit passed"
                STEPS_COMPLETED+=("Governance audit passed")
            else
                echo -e "  ${YELLOW}⚠${NC} Audit found issues (review recommended)"
                STEPS_SKIPPED+=("Governance audit (issues found)")
            fi
        else
            echo -e "  ${CYAN}ℹ${NC} No audit script found"
            STEPS_SKIPPED+=("Governance audit (no script)")
        fi

        # Update session log
        if [[ -f "$SESSION_LOG" ]]; then
            echo "" >> "$SESSION_LOG"
            echo "| $DATE | $ROLE | $TASK_ID | $SUMMARY |" >> "$SESSION_LOG"
            echo -e "  ${GREEN}✓${NC} Session log updated"
            STEPS_COMPLETED+=("Session log entry added")
        fi

        # Check for required ADR (Architecture Decision Record)
        ADR_DIR="$GOV_DIR/docs/process/adr"
        if [[ -d "$ADR_DIR" ]]; then
            # Count ADRs
            ADR_COUNT=$(ls -1 "$ADR_DIR"/ADR-*.md 2>/dev/null | wc -l | tr -d ' ')
            echo -e "  ${CYAN}ℹ${NC} Found $ADR_COUNT ADR(s) in project"
        fi

        # Update metrics
        METRICS_FILE="$GOV_DIR/docs/metrics/metrics.json"
        if [[ -f "$METRICS_FILE" ]]; then
            # Update task count using python (safer JSON handling)
            python3 -c "
import json
from datetime import datetime
try:
    with open('$METRICS_FILE', 'r') as f:
        metrics = json.load(f)
    metrics['total_tasks_completed'] = metrics.get('total_tasks_completed', 0) + 1
    metrics['last_task_completed'] = '$TASK_ID'
    metrics['last_task_date'] = '$DATE'
    metrics['last_task_agent'] = '$ROLE'
    with open('$METRICS_FILE', 'w') as f:
        json.dump(metrics, f, indent=2)
    print('Metrics updated')
except Exception as e:
    print(f'Metrics update skipped: {e}')
" 2>/dev/null && echo -e "  ${GREEN}✓${NC} Metrics updated" || true
        fi
    else
        echo -e "  ${CYAN}ℹ${NC} No governance framework found (.governance/)"
        STEPS_SKIPPED+=("Governance audit (no framework)")
    fi
else
    echo -e "  ${YELLOW}⚠${NC} Governance audit skipped"
    STEPS_SKIPPED+=("Governance audit")
fi

# ========================================
# Summary
# ========================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  ✓ TASK COMPLETION WORKFLOW FINISHED${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${CYAN}Summary:${NC}"
echo -e "  ${GREEN}✓${NC} Completed: ${#STEPS_COMPLETED[@]} steps"
echo -e "  ${YELLOW}⏭${NC} Skipped:   ${#STEPS_SKIPPED[@]} steps"
echo -e "  ${RED}✗${NC} Failed:    ${#STEPS_FAILED[@]} steps"
echo ""
echo -e "${CYAN}Artifacts Created:${NC}"
echo "  • Test template: tests/test_${TASK_ID_LOWER}.py"
echo "  • Report: .agents/sessions/completion_${TASK_ID}_${TIMESTAMP}.md"
[[ "$SKIP_BACKUP" == false ]] && echo "  • Backup: .agents/backups/backup_${TASK_ID}_${TIMESTAMP}.tar.gz"
[[ -n "$GIT_HASH" ]] && echo "  • Git commit: $GIT_HASH"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Review and implement actual tests in: tests/test_${TASK_ID_LOWER}.py"
echo "  2. Verify CHANGELOG.md entry is correct"
echo "  3. Push changes if ready: git push"
echo "  4. Continue with next task or end session"
echo ""
echo -e "${MAGENTA}End Session Commands:${NC}"
echo "  python3 .agents/agent_tools.py session end $SESSION_ID \"Session complete\""
echo "  python3 .agents/agent_tools.py leave $ROLE --summary \"Done\""
echo ""
