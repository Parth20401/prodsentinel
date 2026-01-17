#!/bin/bash
set -e

# 1. Start Celery Worker (Pipeline) in background
echo "Starting Celery Worker..."
celery -A app.celery_app worker --loglevel=info --pool=solo &

# 2. Start Fake Services (in background)
# We run them on different ports but inside the same container.
# NOTE: In this "Fat Container" model, they talk to "localhost" because they are in the same network namespace.

echo "Starting Fake Gateway..."
cd /app/prodsentinel-fake-services
# Set PRODSENTINEL_URL to localhost:8000 because Backend is in the SAME container
export PRODSENTINEL_URL=http://localhost:8000 
uvicorn app.api-gateway.main:app --port 8003 &

echo "Starting Fake Payment..."
uvicorn app.payment-service.main:app --port 8004 &

echo "Starting Fake Inventory..."
uvicorn app.inventory-service.main:app --port 8002 &

# 3. Start Backend API (Foreground - keeps container alive)
echo "Starting Backend API..."
cd /app/prodsentinel-backend
# Run migrations before starting
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000
