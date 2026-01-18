@echo off
echo ===================================================
echo   ProdSentinel - Local Agent Runner (Hybrid Mode)
echo ===================================================
echo.
echo This script runs the "Fake Services" locally.
echo It will pick up PRODSENTINEL_URL from .env
echo.

set PYTHONPATH=.

echo [1/3] Starting Inventory Service (Port 8002)...
start "Inventory Service" cmd /k "uv run uvicorn app.inventory-service.main:app --port 8002"
timeout /t 2 >nul

echo [2/3] Starting Payment Service (Port 8004)...
start "Payment Service" cmd /k "uv run uvicorn app.payment-service.main:app --port 8004"
timeout /t 2 >nul

echo [3/3] Starting API Gateway (Port 8003)...
start "API Gateway" cmd /k "uv run uvicorn app.api-gateway.main:app --port 8003" 

echo.
echo ===================================================
echo   AGENTS RUNNING! 
echo ===================================================
echo.
echo To generate traffic, open a new terminal and run:
echo curl -X POST http://localhost:8003/checkout/order-123
echo.
pause
