#!/bin/bash
# ============================================================
# PROJECT TEMPLATE - TMUX DEV ENVIRONMENT
# ============================================================
# Customize the variables below for your project
# Usage: ./scripts/dev-start.sh
# ============================================================

# ============================================================
# CONFIGURATION - CUSTOMIZE THESE FOR YOUR PROJECT
# ============================================================
SESSION="myproject"                                    # tmux session name
PROJECT_DIR="$HOME/my_project"                         # project root
API_CMD="source venv/bin/activate && python api_server.py"  # API start command
CLOUD_HOST="your-server.com"                           # cloud server IP/hostname
CLOUD_USER="ubuntu"                                    # cloud SSH user
SSH_KEY="~/.ssh/id_rsa"                               # SSH key path

# ============================================================
# KILL EXISTING SESSION
# ============================================================
tmux kill-session -t $SESSION 2>/dev/null

# ============================================================
# CREATE SESSION & PANES
# ============================================================
# Layout:
#  ┌─────────────┬─────────────┬─────────────┐
#  │  0: API     │  1: DOCKER  │  2: CLOUD   │
#  ├─────────────┼─────────────┼─────────────┤
#  │  3: LOGS    │  4: CLAUDE  │  5: SHELL   │
#  └─────────────┴─────────────┴─────────────┘

tmux new-session -d -s $SESSION -n "dev" -c "$PROJECT_DIR"

# Create 6 panes
tmux split-window -v -t $SESSION:0
tmux split-window -h -t $SESSION:0.0
tmux split-window -h -t $SESSION:0.0
tmux split-window -h -t $SESSION:0.3
tmux split-window -h -t $SESSION:0.3
tmux select-layout -t $SESSION:0 tiled

# ============================================================
# START SERVICES
# ============================================================

# Pane 0: API Server
tmux send-keys -t $SESSION:0.0 "cd $PROJECT_DIR && echo '=== API Server ===' && $API_CMD" C-m

# Pane 1: Docker/N8N status
tmux send-keys -t $SESSION:0.1 "echo '=== Docker Services ===' && docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | head -10" C-m

# Pane 2: Cloud SSH (ready to connect)
tmux send-keys -t $SESSION:0.2 "echo '=== Cloud Server ===' && echo 'Connect: ssh -i $SSH_KEY $CLOUD_USER@$CLOUD_HOST'" C-m

# Pane 3: Logs
tmux send-keys -t $SESSION:0.3 "cd $PROJECT_DIR && echo '=== Logs ===' && tail -f logs/*.log 2>/dev/null || echo 'No logs yet'" C-m

# Pane 4: Claude Code
tmux send-keys -t $SESSION:0.4 "cd $PROJECT_DIR && echo '=== Claude Code ===' && echo 'Run: claude'" C-m

# Pane 5: Free shell
tmux send-keys -t $SESSION:0.5 "cd $PROJECT_DIR && echo '=== Shell ===' && echo 'Ready'" C-m

# ============================================================
# ATTACH
# ============================================================
tmux select-pane -t $SESSION:0.4

echo "╔═══════════════════════════════════════════════════════╗"
echo "║           DEV ENVIRONMENT STARTED                     ║"
echo "╠═══════════════════════════════════════════════════════╣"
echo "║  Session: $SESSION                                    "
echo "║                                                       ║"
echo "║  Panes:                                               ║"
echo "║    0: API        1: Docker      2: Cloud SSH          ║"
echo "║    3: Logs       4: Claude      5: Shell              ║"
echo "║                                                       ║"
echo "║  Shortcuts (Ctrl+B prefix):                           ║"
echo "║    ←→↑↓  Navigate    z  Zoom    d  Detach             ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

tmux attach -t $SESSION
