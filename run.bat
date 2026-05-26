@echo off
title VCF ↔ Excel Contact Converter
echo ===================================================
echo   VCF ↔ Excel Contact Converter Startup Script
echo ===================================================
echo.

:: Check for Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python was not found on your system.
    echo Please install Python (version 3.8 or newer) and add it to your PATH.
    echo You can download it from: https://www.python.org/
    echo.
    pause
    exit /b 1
)

:: Create Virtual Environment if it doesn't exist
if not exist .venv (
    echo Creating Python virtual environment (.venv)...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: Activate Virtual Environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)

:: Install Dependencies
echo Installing dependencies from requirements.txt...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo ===================================================
echo   Starting local converter server...
echo   Opening browser at http://127.0.0.1:5000
echo ===================================================
echo.

:: Launch browser in 1 second, then run Flask
start "" "http://127.0.0.1:5000"
python app.py

pause
