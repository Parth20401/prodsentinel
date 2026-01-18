@echo off
echo ===================================================
echo   ProdSentinel - Local Worker (Split Stack Mode)
echo ===================================================
echo.
echo This script runs the HEAVY AI Pipeline locally.
echo It will pick up credentials from prodsentinel-pipeline/.env
echo.

REM Ensure we are in the correct directory if launched from elsewhere
cd /d "%~dp0"

echo [1/1] Starting Celery Worker (Pipeline)...
echo.
echo     Waiting for tasks from Cloud Backend...
echo.

cd prodsentinel-pipeline
set PYTHONPATH=.
.venv\Scripts\python.exe -m celery -A app.celery_app worker --loglevel=info --pool=solo

pause
