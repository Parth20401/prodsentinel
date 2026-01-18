#!/bin/bash
set -e
export C_FORCE_ROOT=true

# 1. Run migrations for Backend
echo "Running migrations..."
cd /app/prodsentinel-backend
PYTHONPATH=. alembic upgrade head

# 2. Start Celery Worker (Pipeline) in background
# Optimized for free tier: Concurrency=1 to save RAM
echo "Starting Celery Worker..."
cd /app/prodsentinel-pipeline
PYTHONPATH=. celery -A app.celery_app worker --loglevel=error --concurrency=1 &

# 3. Start Fake Services (DISABLED for Cloud Hybrid Mode)
# We run these locally to save cloud memory (Hybrid Architecture)
echo "Skipping Fake Services (Hybrid Mode - Run these locally)..."
# cd /app/prodsentinel-fake-services
# export PRODSENTINEL_URL=http://localhost:8000 
# PYTHONPATH=. uvicorn app.api-gateway.main:app --port 8003 --workers 1 --loop asyncio &
# sleep 5
# ...

# 4. Start Backend API (Foreground - Must be last)
echo "Starting Backend API..."
cd /app/prodsentinel-backend
# Use exec to replace the shell process with uvicorn, saving a tiny bit of RAM (approx 1-2MB)
export PYTHONPATH=.
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1

