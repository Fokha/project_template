#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# BACKUP SCRIPT - {{PROJECT_NAME}}
# Automated backup of critical data to remote server
# ═══════════════════════════════════════════════════════════════
#
# Usage:
# 1. Copy to your project: cp backup_template.sh ~/project/scripts/backup.sh
# 2. Replace placeholders
# 3. Make executable: chmod +x backup.sh
# 4. Run: ./backup.sh
#
# Schedule with cron:
#   0 2 * * * /path/to/backup.sh >> /var/log/backup.log 2>&1
#
# ═══════════════════════════════════════════════════════════════

set -e  # Exit on error

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

PROJECT_NAME="{{PROJECT_NAME}}"
PROJECT_DIR="{{PROJECT_DIR}}"

# Remote server
REMOTE_USER="{{CLOUD_USER}}"
REMOTE_HOST="{{CLOUD_IP}}"
REMOTE_DIR="/home/${REMOTE_USER}/${PROJECT_NAME}-backups"
SSH_KEY="{{SSH_KEY_PATH}}"

# What to backup
BACKUP_DIRS=(
    "data"           # Databases
    "models"         # ML models
    "config"         # Configuration
    "n8n_data"       # N8N workflows
)

# Retention
KEEP_BACKUPS=5

# Timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="${PROJECT_NAME}_backup_${TIMESTAMP}"

# ═══════════════════════════════════════════════════════════════
# FUNCTIONS
# ═══════════════════════════════════════════════════════════════

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

check_requirements() {
    log "Checking requirements..."

    if ! command -v rsync &> /dev/null; then
        log "ERROR: rsync is required but not installed"
        exit 1
    fi

    if ! command -v ssh &> /dev/null; then
        log "ERROR: ssh is required but not installed"
        exit 1
    fi

    if [ ! -f "$SSH_KEY" ]; then
        log "ERROR: SSH key not found: $SSH_KEY"
        exit 1
    fi
}

create_backup() {
    log "Creating backup: $BACKUP_NAME"

    # Create temp directory
    TEMP_DIR=$(mktemp -d)
    BACKUP_DIR="${TEMP_DIR}/${BACKUP_NAME}"
    mkdir -p "$BACKUP_DIR"

    # Copy directories
    for dir in "${BACKUP_DIRS[@]}"; do
        if [ -d "${PROJECT_DIR}/${dir}" ]; then
            log "  Copying ${dir}..."
            cp -r "${PROJECT_DIR}/${dir}" "${BACKUP_DIR}/"
        else
            log "  Warning: ${dir} not found, skipping"
        fi
    done

    # Create manifest
    cat > "${BACKUP_DIR}/manifest.txt" << EOF
Backup: ${BACKUP_NAME}
Created: $(date)
Project: ${PROJECT_NAME}
Directories: ${BACKUP_DIRS[*]}
EOF

    log "Backup created: ${BACKUP_DIR}"
    echo "$BACKUP_DIR"
}

upload_backup() {
    local backup_dir="$1"

    log "Uploading to remote server..."

    # Ensure remote directory exists
    ssh -i "$SSH_KEY" "${REMOTE_USER}@${REMOTE_HOST}" "mkdir -p ${REMOTE_DIR}"

    # Upload with rsync
    rsync -avz --progress \
        -e "ssh -i ${SSH_KEY}" \
        "${backup_dir}/" \
        "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/${BACKUP_NAME}/"

    log "Upload complete"
}

cleanup_old_backups() {
    log "Cleaning up old backups (keeping ${KEEP_BACKUPS})..."

    # Remote cleanup
    ssh -i "$SSH_KEY" "${REMOTE_USER}@${REMOTE_HOST}" "
        cd ${REMOTE_DIR} && \
        ls -1t | tail -n +$((KEEP_BACKUPS + 1)) | xargs -r rm -rf
    "

    # Local temp cleanup
    rm -rf "$TEMP_DIR"

    log "Cleanup complete"
}

send_notification() {
    local status="$1"
    local message="$2"

    # Telegram notification (optional)
    if [ -n "{{TELEGRAM_BOT_TOKEN}}" ] && [ -n "{{TELEGRAM_CHAT_ID}}" ]; then
        curl -s -X POST "https://api.telegram.org/bot{{TELEGRAM_BOT_TOKEN}}/sendMessage" \
            -d chat_id="{{TELEGRAM_CHAT_ID}}" \
            -d text="🔄 Backup ${status}: ${message}"
    fi
}

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

main() {
    log "═══════════════════════════════════════════════════════════"
    log "Starting backup: ${PROJECT_NAME}"
    log "═══════════════════════════════════════════════════════════"

    check_requirements

    # Create backup
    backup_dir=$(create_backup)

    # Upload to remote
    if upload_backup "$backup_dir"; then
        cleanup_old_backups
        send_notification "SUCCESS" "${BACKUP_NAME} uploaded to ${REMOTE_HOST}"
        log "═══════════════════════════════════════════════════════════"
        log "Backup completed successfully!"
        log "═══════════════════════════════════════════════════════════"
        exit 0
    else
        send_notification "FAILED" "Upload failed for ${BACKUP_NAME}"
        log "ERROR: Backup failed!"
        exit 1
    fi
}

# ═══════════════════════════════════════════════════════════════
# OPTIONS
# ═══════════════════════════════════════════════════════════════

case "$1" in
    --dry-run)
        log "DRY RUN - No changes will be made"
        check_requirements
        log "Would backup: ${BACKUP_DIRS[*]}"
        log "Would upload to: ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}"
        ;;
    --list)
        log "Remote backups:"
        ssh -i "$SSH_KEY" "${REMOTE_USER}@${REMOTE_HOST}" "ls -lh ${REMOTE_DIR}"
        ;;
    --restore)
        if [ -z "$2" ]; then
            log "Usage: $0 --restore <backup_name>"
            exit 1
        fi
        log "Restoring: $2"
        rsync -avz --progress \
            -e "ssh -i ${SSH_KEY}" \
            "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/$2/" \
            "${PROJECT_DIR}/"
        log "Restore complete"
        ;;
    --help)
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  (none)      Run backup"
        echo "  --dry-run   Show what would be done"
        echo "  --list      List remote backups"
        echo "  --restore   Restore a backup"
        echo "  --help      Show this help"
        ;;
    *)
        main
        ;;
esac
