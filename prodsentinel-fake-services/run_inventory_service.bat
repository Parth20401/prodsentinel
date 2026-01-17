@echo off
REM Run Inventory Service with correct Python path
cd /d "%~dp0app\inventory-service"
set PYTHONPATH=%~dp0app
uvicorn main:app --reload --port 8002
