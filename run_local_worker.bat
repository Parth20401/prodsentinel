@echo off
echo ===================================================
echo   ProdSentinel - Local Worker (Split Stack Mode)
echo ===================================================
echo.
echo This script runs the HEAVY AI Pipeline locally.
echo It will pick up credentials from prodsentinel-pipeline/.env
echo.

echo [1/1] Starting Celery Worker (Pipeline)...
echo.
echo     Waiting for tasks from Cloud Backend...
echo.

cd prodsentinel-pipeline
set PYTHONPATH=.
uv run celery -A app.celery_app worker --loglevel=info --pool=solo

pause
