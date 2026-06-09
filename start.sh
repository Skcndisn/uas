#!/bin/bash

# Get the directory where this script lives
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Start AI service in background
cd "$SCRIPT_DIR/signlearn-ai/ai-service"
echo "[start.sh] Starting AI service on port 5001..."
nohup python app.py > /tmp/ai-service.log 2>&1 &
AI_PID=$!
disown $AI_PID 2>/dev/null || true

# Wait for AI service to be ready
sleep 3

echo "[start.sh] Starting backend on port 5000..."
# Start backend (serves frontend + API) on port 5000
cd "$SCRIPT_DIR/signlearn-ai/backend"
exec python app.py
