#!/bin/bash
set -e
export C_FORCE_ROOT=true

# 1. Run migrations for Backend
echo "Running migrations..."
cd /app/prodsentinel-backend
PYTHONPATH=. alembic upgrade head

# 2. Start Celery Worker (Pipeline) - REMOVED for Split Stack
# The AI Worker is too heavy for the free tier (500MB+ RAM).
# We now run this LOCALLY on your machine.
echo "Skipping Celery Worker (Run locally)..."

# 3. Start Fake Services - REMOVED for Split Stack
# We run these LOCALLY to generate traffic.
echo "Skipping Fake Services (Run locally)..."

# 4. Start Backend API (Foreground - The only cloud process)
echo "Starting Backend API (Lightweight Mode)..."
echo "Memory Usage Expected: <100MB"
cd /app/prodsentinel-backend
# Use exec to replace the shell process with uvicorn
export PYTHONPATH=.
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1

