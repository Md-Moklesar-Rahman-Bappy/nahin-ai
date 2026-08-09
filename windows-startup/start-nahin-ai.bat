@echo off
REM ============================================================
REM  Nahin AI - Startup Launcher (Python dashboard)
REM  Starts the local Nahin AI dashboard server and opens the
REM  /nahin page in the default browser.
REM
REM  Run manually:
REM      windows-startup\start-nahin-ai.bat
REM ============================================================
title Nahin AI Startup

REM Go to the project root. Adjust if the project moves.
cd /d C:\xampp\htdocs\nahin-ai

REM Make sure the dashboard module exists.
if not exist "dashboard\app.py" (
    echo [ERROR] dashboard\app.py not found in C:\xampp\htdocs\nahin-ai
    pause
    exit /b 1
)

REM Prefer a virtual environment if the user created one.
set "PYTHON=python"
if exist "venv\Scripts\python.exe" set "PYTHON=venv\Scripts\python.exe"

REM Start the Nahin AI dashboard server in its own window.
echo Starting Nahin AI Dashboard...
start "Nahin AI Dashboard" cmd /k "%PYTHON% dashboard\app.py"

REM Give the server a moment to boot, then open the dashboard.
timeout /t 4 >nul
start http://127.0.0.1:8000/nahin

exit
