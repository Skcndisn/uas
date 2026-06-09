#!/bin/bash
set -e

# Start AI service in background on port 5001
cd signlearn-ai/ai-service
python app.py &
AI_PID=$!

# Start backend (serves frontend + API) on port 5000
cd ../backend
python app.py
