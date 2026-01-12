#!/bin/bash

# ============================================
# FOKHA PROJECT TEMPLATE - INITIALIZATION SCRIPT
# ============================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get project name
PROJECT_NAME=${1:-"my_project"}
PROJECT_DIR=$(pwd)

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  FOKHA PROJECT TEMPLATE - INITIALIZATION${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Project Name:${NC} $PROJECT_NAME"
echo -e "${YELLOW}Project Dir:${NC}  $PROJECT_DIR"
echo ""

# ----------------------------------------
# Create directory structure
# ----------------------------------------
echo -e "${GREEN}[1/7] Creating directory structure...${NC}"

mkdir -p api/utils
mkdir -p knowledge_base/documents/{specs,designs,references,outputs}
mkdir -p knowledge_base/attachments/{images,pdfs,logs}
mkdir -p knowledge_base/exports
mkdir -p automation/workflows
mkdir -p infrastructure/cloud
mkdir -p cli/.claude/commands
mkdir -p app
mkdir -p logs
mkdir -p data

echo "  ✓ Directories created"

# ----------------------------------------
# Initialize Knowledge Base
# ----------------------------------------
echo -e "${GREEN}[2/7] Initializing Knowledge Base...${NC}"

if [ -f "knowledge_base/schema.sql" ]; then
    sqlite3 knowledge_base/kb.db < knowledge_base/schema.sql
    echo "  ✓ Database created: knowledge_base/kb.db"

    # Set project name in config
    sqlite3 knowledge_base/kb.db "UPDATE kb_project SET value='$PROJECT_NAME' WHERE key='project_name';"
    echo "  ✓ Project name set: $PROJECT_NAME"
else
    echo -e "${YELLOW}  ⚠ schema.sql not found, skipping database creation${NC}"
fi

# ----------------------------------------
# Create .env file
# ----------------------------------------
echo -e "${GREEN}[3/7] Creating environment file...${NC}"

if [ ! -f "api/.env" ]; then
    cat > api/.env << EOF
# ============================================
# $PROJECT_NAME - Environment Configuration
# ============================================

# Project
PROJECT_NAME=$PROJECT_NAME
VERSION=1.0.0

# API Server
API_PORT=5050
FLASK_ENV=development
LOG_LEVEL=INFO

# Database
DATABASE_PATH=./data/kb.db

# n8n Automation
N8N_PORT=5678
N8N_USER=admin
N8N_PASSWORD=$(openssl rand -hex 12)
N8N_HOST=localhost

# PostgreSQL (for n8n)
POSTGRES_PASSWORD=$(openssl rand -hex 16)

# Redis (optional)
REDIS_PORT=6379

# Cloud/Deploy
PUBLIC_IP=localhost
TIMEZONE=UTC

# API Keys (add your keys here)
# OPENAI_API_KEY=
# ANTHROPIC_API_KEY=
# TAVILY_API_KEY=

EOF
    echo "  ✓ Created api/.env"
else
    echo "  ⚠ api/.env already exists, skipping"
fi

# ----------------------------------------
# Create .gitignore
# ----------------------------------------
echo -e "${GREEN}[4/7] Creating .gitignore...${NC}"

cat > .gitignore << 'EOF'
# Environment
.env
.env.local
*.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/

# Databases
*.db
*.sqlite
*.sqlite3

# Logs
*.log
logs/

# IDE
.idea/
.vscode/
*.swp
*.swo
.DS_Store

# Build
build/
dist/
*.egg-info/

# Docker
.docker/

# Secrets
*.pem
*.key
credentials.json

# Knowledge Base (keep structure, ignore content)
knowledge_base/attachments/*
!knowledge_base/attachments/.gitkeep
knowledge_base/exports/*
!knowledge_base/exports/.gitkeep

# Data
data/*
!data/.gitkeep

EOF

# Create .gitkeep files
touch knowledge_base/attachments/.gitkeep
touch knowledge_base/exports/.gitkeep
touch data/.gitkeep
touch logs/.gitkeep

echo "  ✓ Created .gitignore"

# ----------------------------------------
# Create CLAUDE.md
# ----------------------------------------
echo -e "${GREEN}[5/7] Creating CLAUDE.md (project context)...${NC}"

cat > CLAUDE.md << EOF
# $PROJECT_NAME

## Project Overview
[Describe your project here]

## Architecture
- **API**: Python Flask server (port 5050)
- **Automation**: n8n workflows (port 5678)
- **Knowledge Base**: SQLite database
- **Infrastructure**: Docker Compose

## Getting Started
\`\`\`bash
# Start services
docker-compose -f infrastructure/docker-compose.yml up -d

# Check health
curl http://localhost:5050/health
\`\`\`

## Agent System
This project uses a multi-agent system. See \`agents/AGENT_SYSTEM.md\` for details.

## Commands
- \`/agent-comms\` - View agent activity
- \`/research <topic>\` - Research a topic
- \`/parallel-tasks\` - Run parallel tasks

## Conventions
- Python: Use type hints, docstrings required
- API: RESTful endpoints, JSON responses
- Git: Meaningful commit messages with emoji

EOF

echo "  ✓ Created CLAUDE.md"

# ----------------------------------------
# Create VERSION file
# ----------------------------------------
echo -e "${GREEN}[6/7] Creating VERSION file...${NC}"

echo "1.0.0" > VERSION
echo "  ✓ Created VERSION (1.0.0)"

# ----------------------------------------
# Summary
# ----------------------------------------
echo -e "${GREEN}[7/7] Initialization complete!${NC}"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✓ PROJECT INITIALIZED SUCCESSFULLY${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "Next steps:"
echo ""
echo "  1. Edit api/.env with your configuration"
echo "  2. Edit CLAUDE.md with project description"
echo "  3. Start services:"
echo ""
echo "     cd infrastructure"
echo "     docker-compose up -d"
echo ""
echo "  4. Access:"
echo "     - API:  http://localhost:5050"
echo "     - n8n:  http://localhost:5678"
echo ""
echo -e "${YELLOW}Happy coding! 🚀${NC}"
