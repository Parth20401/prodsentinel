#!/bin/bash
set -e

# 1. Run migrations for Backend
echo "Running migrations..."
cd /app/prodsentinel-backend
PYTHONPATH=. alembic upgrade head

# 2. Start Celery Worker (Pipeline) in background
echo "Starting Celery Worker..."
cd /app/prodsentinel-pipeline
PYTHONPATH=. celery -A app.celery_app worker --loglevel=info --pool=solo &

# 3. Start Fake Services (in background)
echo "Starting Fake Services..."
cd /app/prodsentinel-fake-services
export PRODSENTINEL_URL=http://localhost:8000 
PYTHONPATH=. uvicorn app.api-gateway.main:app --port 8003 &
PYTHONPATH=. uvicorn app.payment-service.main:app --port 8004 &
PYTHONPATH=. uvicorn app.inventory-service.main:app --port 8002 &

# 4. Start Backend API (Foreground)
echo "Starting Backend API..."
cd /app/prodsentinel-backend
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000

