# Infrastructure Commands

Quick reference for infrastructure and DevOps tasks.

## Claude Code Management

```bash
# Add Claude Code to existing project
/Users/fwez/Documents/development/ai_studio/project_template/scripts/add_claude_code.sh /path/to/project

# List global commands
ls ~/.claude/commands/

# List project commands
ls .claude/commands/

# Create new global command
cat > ~/.claude/commands/newcmd.md << 'EOF'
# Command Title
Description and usage
EOF
```

## Docker Operations

```bash
# Status
docker ps
docker-compose ps

# Logs
docker logs CONTAINER -f --tail 100

# Restart
docker-compose restart SERVICE

# Rebuild
docker-compose up -d --build SERVICE

# Clean up
docker system prune -f
```

## Cloud Deployment

```bash
# SSH to cloud
ssh ubuntu@34.173.17.40

# Sync to cloud
rsync -avz --exclude='venv' --exclude='__pycache__' \
  ./ ubuntu@SERVER:/path/

# Deploy
./cloud/deploy.sh

# Health check
curl http://SERVER:5050/health
```

## Backup Operations

```bash
# Quick backup
tar -czf backup_$(date +%Y%m%d).tar.gz \
  --exclude='venv' --exclude='__pycache__' --exclude='.git' .

# Cloud backup
./cloud/backup-critical-data.sh

# SD card sync
./scripts/sync_to_sdcard.sh

# List backups
ls -la .agents/backups/
```

## Health Checks

```bash
# Local
curl localhost:5050/health
curl localhost:5678/healthz

# Cloud
curl 34.173.17.40:5050/health

# Docker
docker ps --format "table {{.Names}}\t{{.Status}}"

# Disk
df -h
```

## Register as INFRASTRUCTURE Agent

```bash
python3 .agents/tools/agent_registry.py register INFRASTRUCTURE --focus "DevOps, Claude Code, backups"
python3 .agents/tools/agent_registry.py session start INFRASTRUCTURE
```

## Related Commands

| Command | Description |
|---------|-------------|
| `/backup` | Backup operations |
| `/sync` | Sync operations |
| `/status` | Project status |
| `/tools` | All tools index |
