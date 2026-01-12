# Backup Commands

Create and manage project backups.

## Quick Backup

Create a timestamped backup of critical files:

```bash
TIMESTAMP=$(date +%Y%m%d%H%M%S)
mkdir -p .agents/backups
tar -czf .agents/backups/manual_backup_$TIMESTAMP.tar.gz \
    .agents/*.db \
    .agents/sessions/ \
    CHANGELOG.md \
    VERSION 2>/dev/null || true
echo "Backup created: .agents/backups/manual_backup_$TIMESTAMP.tar.gz"
```

## List Backups

```bash
ls -lah .agents/backups/
```

## Restore Backup

```bash
# List available backups
ls .agents/backups/

# Extract specific backup (be careful!)
tar -xzf .agents/backups/backup_FILENAME.tar.gz -C /tmp/restore_test/

# Review before overwriting
ls /tmp/restore_test/
```

## Backup Contents

Standard backup includes:
- `.agents/*.db` - Agent databases
- `.agents/sessions/` - Session logs and reports
- `CHANGELOG.md` - Project changelog
- `VERSION` - Version file

## Full Project Backup

For a complete backup including code:

```bash
TIMESTAMP=$(date +%Y%m%d%H%M%S)
PROJECT_NAME=$(basename $(pwd))
tar -czf ../${PROJECT_NAME}_full_backup_$TIMESTAMP.tar.gz \
    --exclude='.git' \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='node_modules' \
    .
echo "Full backup: ../${PROJECT_NAME}_full_backup_$TIMESTAMP.tar.gz"
```

## Cleanup Old Backups

Keep only the last 10 backups:

```bash
ls -t .agents/backups/backup_*.tar.gz | tail -n +11 | xargs rm -f 2>/dev/null || true
echo "Cleaned up old backups, kept last 10"
```

## Quick Actions

Based on user request:
- "backup" → Create quick backup
- "list backups" → Show available backups
- "full backup" → Create complete project backup
- "cleanup backups" → Remove old backups
