@echo off
REM Run Payment Service with correct Python path
cd /d "%~dp0app\payment-service"
set PYTHONPATH=%~dp0app
uvicorn main:app --reload --port 8001
