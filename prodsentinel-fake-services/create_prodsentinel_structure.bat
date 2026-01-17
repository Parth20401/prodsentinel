@echo off
REM =====================================================
REM ProdSentinel Fake Services - Folder Structure Creator
REM =====================================================

REM Root project folder
set PROJECT_ROOT=prodsentinel-fake-services

echo Creating project root...
mkdir %PROJECT_ROOT%
cd %PROJECT_ROOT%

REM --------------------
REM Common utilities
REM --------------------
echo Creating common utilities...
mkdir common
type nul > common\logging.py
type nul > common\tracing.py
type nul > common\middleware.py

REM --------------------
REM API Gateway Service
REM --------------------
echo Creating api-gateway service...
mkdir api-gateway
type nul > api-gateway\main.py
type nul > api-gateway\service.py
type nul > api-gateway\requirements.txt

REM --------------------
REM Payment Service
REM --------------------
echo Creating payment-service...
mkdir payment-service
type nul > payment-service\main.py
type nul > payment-service\service.py
type nul > payment-service\requirements.txt

REM --------------------
REM Inventory Service
REM --------------------
echo Creating inventory-service...
mkdir inventory-service
type nul > inventory-service\main.py
type nul > inventory-service\service.py
type nul > inventory-service\requirements.txt

REM --------------------
REM Root README
REM --------------------
echo Creating README.md...
type nul > README.md

echo.
echo ==========================================
echo Project structure created successfully!
echo ==========================================
pause
