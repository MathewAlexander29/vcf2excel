@echo off
title VCF to Excel Contact Converter
echo ===================================================
echo   VCF to Excel Contact Converter - Startup Script
echo ===================================================
echo.

:: Change directory to the folder where this batch file is located
cd /d "%~dp0"

:: Check for Python
where python >nul 2>nul
if errorlevel 1 goto NoPython
goto PythonFound

:NoPython
echo [ERROR] Python was not found on your system.
echo Please install Python 3.8+ and add it to your PATH.
echo Download from: https://www.python.org/
echo.
pause
exit /b 1

:PythonFound
echo Python found. Checking virtual environment...

:: Create Virtual Environment if it doesn't exist
if exist .venv goto VenvExists
echo Creating Python virtual environment...
python -m venv .venv
if not exist .venv\Scripts\activate.bat goto VenvFail
goto VenvOk

:VenvExists
if not exist .venv\Scripts\activate.bat goto VenvFail
goto VenvOk

:VenvFail
echo [ERROR] Failed to create virtual environment.
echo Please ensure Python is installed correctly.
pause
exit /b 1

:VenvOk
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Installing dependencies...
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet
if errorlevel 1 goto InstallFail
goto StartServer

:InstallFail
echo [ERROR] Failed to install required packages.
echo Check your internet connection and try again.
pause
exit /b 1

:StartServer
echo.
echo ===================================================
echo   Starting server... browser will open shortly.
echo   Press Ctrl+C or close this window to stop.
echo ===================================================
echo.

python app.py
if errorlevel 1 goto ServerError
goto Done

:ServerError
echo.
echo [ERROR] The server stopped unexpectedly.
echo Check server.log for details.
echo.
pause

:Done
