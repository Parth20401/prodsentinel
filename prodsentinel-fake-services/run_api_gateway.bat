@echo off
REM Run API Gateway with correct Python path
cd /d "%~dp0app\api-gateway"
set PYTHONPATH=%~dp0app
uvicorn main:app --reload --port 8003
