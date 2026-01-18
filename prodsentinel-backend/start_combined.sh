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

# 3. Start Fake Services (Optimized - Sequential or Minimal)
echo "Starting Fake Services..."
cd /app/prodsentinel-fake-services
export PRODSENTINEL_URL=http://localhost:8000 
# Running only API Gateway as entry point to save memory, 
# relying on direct service calls or just one background worker if essential.
# For now, let's run them all but with workers=1 and limited backlog if possible inside uvicorn defaults.
# We will sleep briefly between starts to avoid CPU spike OOM.
PYTHONPATH=. uvicorn app.api-gateway.main:app --port 8003 --workers 1 --loop asyncio &
sleep 2
PYTHONPATH=. uvicorn app.payment-service.main:app --port 8004 --workers 1 --loop asyncio &
sleep 2
PYTHONPATH=. uvicorn app.inventory-service.main:app --port 8002 --workers 1 --loop asyncio &
sleep 2

# 4. Start Backend API (Foreground)
echo "Starting Backend API..."
cd /app/prodsentinel-backend
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1

