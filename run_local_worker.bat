@echo off
setlocal enabledelayedexpansion
echo ===================================================
echo   ProdSentinel - Local Worker (Split Stack Mode)
echo ===================================================
echo.
echo This script runs the HEAVY AI Pipeline locally.
echo It will pick up credentials from prodsentinel-pipeline/.env
echo.

REM Get the absolute path of this script's directory
set "ROOT_DIR=%~dp0"
cd /d "!ROOT_DIR!prodsentinel-pipeline"

echo [1/1] Starting Celery Worker (Pipeline)...
echo.
echo     Waiting for tasks from Cloud Backend...
echo.

set PYTHONPATH=.
"!ROOT_DIR!prodsentinel-pipeline\.venv\Scripts\python.exe" -m celery -A app.celery_app worker --loglevel=info --pool=solo

pause
