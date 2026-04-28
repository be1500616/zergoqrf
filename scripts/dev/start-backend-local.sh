#!/bin/bash

# Change to project root directory (two levels up from scripts/dev/)
cd "$(dirname "$0")/../.."

echo "Starting PostgreSQL and Redis using Docker Compose..."
docker compose up -d db redis
echo "Waiting for database and Redis to initialize..."
sleep 5

echo "Navigating to backend directory and installing dependencies..."
cd apps/backend || exit

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate
echo "Virtual environment activated. Installing/ensuring development dependencies are installed..."
make install-dev

echo "Setting PYTHONPATH for correct module imports..."
export PYTHONPATH="$(pwd):$PYTHONPATH"

echo "Checking for processes on port 8000 and killing them if found..."
PID=$(lsof -t -i:8000 -sTCP:LISTEN)
if [ -n "$PID" ]; then
    echo "Killing process $PID on port 8000..."
    kill -9 "$PID"
else
    echo "No process found on port 8000."
fi

echo "Starting FastAPI application..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload