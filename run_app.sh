#!/bin/bash

echo "Starting Contrarian Stock Picker Web App..."

# Start Backend
echo "Starting Backend (FastAPI)..."

# Load .env if present
if [ -f .env ]; then
  export $(cat .env | xargs)
fi

./venv/bin/uvicorn backend.api:app --reload --port 18080 &
BACKEND_PID=$!

# Wait for backend to be ready (naive check)
sleep 3

# Start Frontend
echo "Starting Frontend (React)..."
cd frontend
npm run dev -- --open --port 15173

# Cleanup on exit
trap "kill $BACKEND_PID" EXIT

wait
