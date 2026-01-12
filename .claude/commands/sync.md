# Sync Commands

Synchronize project data across locations.

## Git Sync

```bash
# Push to remote
git push

# Pull from remote
git pull

# Check sync status
git status
git rev-list --count @{u}..HEAD  # Commits ahead of remote
```

## Cloud Sync

If cloud sync script exists:
```bash
./scripts/sync_to_cloud.sh
```

## SD Card Sync

If SD card is mounted:
```bash
./scripts/sync_to_sdcard.sh
```

## Manual Sync Options

### Rsync to Cloud
```bash
rsync -avz --exclude='.git' --exclude='venv' --exclude='__pycache__' \
    ./ user@server:/path/to/project/
```

### Copy to SD Card
```bash
rsync -avz --exclude='.git' --exclude='venv' --exclude='__pycache__' \
    ./ /Volumes/SDCARD/project_backup/
```

## Sync Status

Check what needs syncing:
```bash
# Git status
git status

# Check if cloud script exists
ls -la scripts/sync_to_cloud.sh

# Check for mounted SD cards
ls /Volumes/
```

## Quick Actions

Based on user request:
- "sync" or "push" → Run git push
- "sync to cloud" → Run cloud sync script
- "sync to sd card" → Run SD card sync script
- "sync status" → Show what needs syncing
