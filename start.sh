#!/bin/bash

# Start AI service in background, detached from this shell
cd signlearn-ai/ai-service
nohup python app.py > /tmp/ai-service.log 2>&1 &
disown $!

# Wait for AI service to be ready
sleep 3

# Start backend (serves frontend + API) on port 5000
cd ../backend
exec python app.py
