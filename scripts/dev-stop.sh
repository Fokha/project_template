#!/bin/bash
# ============================================================
# STOP DEV ENVIRONMENT
# ============================================================
SESSION="myproject"  # Match SESSION in dev-start.sh

echo "Stopping tmux session: $SESSION"
tmux kill-session -t $SESSION 2>/dev/null && echo "Session stopped" || echo "Session not running"
