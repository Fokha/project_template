# Project Template - Setup Guide

## Quick Start (5 minutes)

### 1. Copy Template

```bash
# Option A: Copy to new location
cp -r project_template/ ~/projects/my_new_project/
cd ~/projects/my_new_project/

# Option B: Use for existing project
cp -r project_template/* ~/existing_project/
cd ~/existing_project/
```

### 2. Initialize

```bash
chmod +x scripts/*.sh
./scripts/init_project.sh "My Project Name"
```

### 3. Configure

Edit `api/.env` with your settings:
```bash
nano api/.env
```

Key settings:
- `PROJECT_NAME` - Your project name
- `API_PORT` - API server port (default: 5050)
- `N8N_PASSWORD` - Change the auto-generated password if needed

### 4. Start Services

```bash
cd infrastructure
docker-compose up -d
```

### 5. Verify

```bash
# Check API
curl http://localhost:5050/health

# Check n8n
curl http://localhost:5678
```

---

## Component Setup

### Python API

```bash
cd api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run locally (development)
python api_server.py
```

### Knowledge Base

```bash
# Initialize database
sqlite3 knowledge_base/kb.db < knowledge_base/schema.sql

# Verify
sqlite3 knowledge_base/kb.db "SELECT * FROM kb_project;"
```

### n8n Workflows

1. Access n8n at http://localhost:5678
2. Login with credentials from `.env`
3. Import workflows from `automation/workflows/`

### Claude Code Integration

```bash
# Copy commands to your project
cp -r cli/.claude/ ~/your_project/

# Now you can use:
# /agent-comms
# /research <topic>
# /parallel-tasks
```

---

## Cloud Deployment

### Option 1: Manual Deploy

```bash
# SSH to your server
ssh user@your-server

# Clone/copy project
git clone your-repo

# Run docker-compose
cd infrastructure
docker-compose up -d
```

### Option 2: Sync Script

```bash
# Edit cloud/sync.sh with your server details
nano infrastructure/cloud/sync.sh

# Run sync
./infrastructure/cloud/sync.sh
```

### Option 3: CI/CD

Use the GitHub Actions workflow in `.github/workflows/` (if included).

---

## Directory Structure After Setup

```
my_project/
├── .env                    # ✓ Generated
├── .gitignore             # ✓ Generated
├── CLAUDE.md              # ✓ Generated (edit this!)
├── VERSION                # ✓ Generated
│
├── api/
│   ├── .env               # ✓ Generated
│   ├── api_server.py      # Template API
│   └── requirements.txt
│
├── knowledge_base/
│   ├── kb.db              # ✓ Created
│   ├── schema.sql
│   └── documents/         # ✓ Created
│
├── infrastructure/
│   └── docker-compose.yml
│
└── scripts/
    └── init_project.sh
```

---

## Troubleshooting

### Docker issues

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs api
docker-compose logs n8n

# Restart all
docker-compose restart
```

### Database issues

```bash
# Reset database
rm knowledge_base/kb.db
sqlite3 knowledge_base/kb.db < knowledge_base/schema.sql
```

### Port conflicts

Edit ports in `api/.env`:
```
API_PORT=5051
N8N_PORT=5679
```

Then restart: `docker-compose up -d`

---

## Next Steps

1. **Edit CLAUDE.md** - Add your project description
2. **Add API endpoints** - Extend `api/api_server.py`
3. **Create workflows** - Build n8n automations
4. **Document decisions** - Use the knowledge base
5. **Configure agents** - Customize `agents/agent_config.yaml`

---

## Support

- Template docs: `project_template/README.md`
- Agent system: `agents/AGENT_SYSTEM.md`
- Knowledge base: `knowledge_base/schema.sql` (comments)
