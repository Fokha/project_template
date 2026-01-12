# DevOps Skills

**Extracted from:** Fokha 3-Site Architecture (Mac + SD Card + Windows/Cloud)

---

## Patterns in This Directory

| Pattern | Template | Purpose |
|---------|----------|---------|
| Docker Compose | `docker-compose.template.yml` | Multi-service setup |
| Dockerfile API | `Dockerfile.api.template` | Python API container |
| Nginx Config | `nginx.template.conf` | Reverse proxy |
| Backup Script | `backup_template.sh` | Automated backups |
| Sync Script | `sync_template.sh` | Local-cloud sync |
| Health Monitor | `health_monitor_template.py` | Service watchdog |
| LaunchAgent | `launchagent_template.plist` | macOS scheduling |
| Cron Setup | `cron_template.sh` | Linux scheduling |
| Deploy Script | `deploy_template.sh` | Deployment automation |
| Failover Script | `failover_template.sh` | Active-active failover |

---

## 3-Site Architecture Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                 3-SITE REDUNDANCY PATTERN                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   [Primary]  ←───sync───→  [Portable]  ←──deploy──→  [Secondary]
│   (Mac Dev)               (SD Card)               (Win/Cloud)
│                                                              │
│   Services:               Backup:                 Services:   │
│   - API (5050)           - ML Models             - API (5050)│
│   - N8N (5678)           - Databases             - N8N (5678)│
│   - WebSocket            - Configs               - Native MT5│
│                          - SSH Keys                          │
│                                                              │
│   Benefits:                                                  │
│   - Development          - Portable              - 24/7      │
│   - Testing             - Offline backup         - Production│
│                         - Disaster recovery                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Start

```bash
# Start all services
docker-compose up -d

# Check health
./scripts/health_check.sh

# Backup to remote
./scripts/backup.sh

# Sync to cloud
./scripts/sync_to_cloud.sh
```

---

## Backup Strategy

| Schedule | Action | Retention |
|----------|--------|-----------|
| Daily 2AM | Full backup to cloud | 5 days |
| Every 6h | Sync to SD card | Latest |
| Weekly | Test restore | - |

---

## Placeholder Reference

| Placeholder | Replace With |
|-------------|--------------|
| `{{PROJECT_NAME}}` | Your project name |
| `{{CLOUD_IP}}` | Cloud server IP |
| `{{CLOUD_USER}}` | SSH username |
| `{{API_PORT}}` | API port (5050) |
| `{{DB_PATH}}` | Database path |
