@echo off
REM PDF Toolkit - Production Server Startup with Multiple Workers
REM Use this script for production deployment

echo.
echo ========================================
echo   PDF TOOLKIT - Production Server
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed
    pause
    exit /b 1
)

REM Activate virtual environment
if exist "venv" (
    call venv\Scripts\activate.bat
)

REM Install/update dependencies
echo Checking dependencies...
pip install -r requirements.txt --quiet

REM Start server (Windows doesn't support Uvicorn workers, use single process)
echo.
echo Starting PDF Toolkit in PRODUCTION mode...
echo Host: 0.0.0.0
echo Port: 8000
echo.

python -m uvicorn main:app --host 0.0.0.0 --port 8000

pause
