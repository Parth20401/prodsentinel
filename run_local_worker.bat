@echo off
echo ===================================================
echo   ProdSentinel - Local Worker (Split Stack Mode)
echo ===================================================
echo.
echo This script runs the HEAVY AI Pipeline locally.
echo It connects to your Cloud Redis/Postgres to process tasks.
echo.

set /p REDIS_URL="Paste your UPSTASH REDIS_URL: "
set /p DATABASE_URL="Paste your NEON DATABASE_URL: "
set /p GOOGLE_API_KEY="Paste your GOOGLE_API_KEY: "

echo.
echo Setting up environment...
set REDIS_URL=%REDIS_URL%
set DATABASE_URL=%DATABASE_URL%
set GOOGLE_API_KEY=%GOOGLE_API_KEY%

echo.
echo [1/1] Starting Celery Worker (Pipeline)...
echo.
echo     Waiting for tasks from Cloud Backend...
echo.

cd prodsentinel-pipeline
set PYTHONPATH=.
uv run celery -A app.celery_app worker --loglevel=info --pool=solo

pause
