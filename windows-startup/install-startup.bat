@echo off
REM ============================================================
REM  Nahin AI - Install Auto Start
REM  Copies the launcher into the Windows Startup folder so that
REM  Nahin AI starts automatically after Windows login.
REM
REM  Run manually:
REM      windows-startup\install-startup.bat
REM ============================================================
title Nahin AI - Install Auto Start

set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "PROJECT_DIR=C:\xampp\htdocs\nahin-ai"
set "LAUNCHER=%STARTUP_FOLDER%\NahinAI-Startup.bat"

REM Check the source launcher exists.
if not exist "%PROJECT_DIR%\windows-startup\start-nahin-ai.bat" (
    echo [ERROR] start-nahin-ai.bat not found. Make sure the project path is correct.
    pause
    exit /b 1
)

REM Create the Startup folder if it does not exist yet.
if not exist "%STARTUP_FOLDER%" (
    mkdir "%STARTUP_FOLDER%"
)

REM Copy the launcher into the Startup folder.
copy /y "%PROJECT_DIR%\windows-startup\start-nahin-ai.bat" "%LAUNCHER%" >nul

if errorlevel 1 (
    echo [ERROR] Could not copy the launcher into the Startup folder.
    pause
    exit /b 1
)

echo.
echo ==============================================
echo  [SUCCESS] Nahin AI auto-start is installed.
echo ==============================================
echo.
echo  Nahin AI will start automatically after your
echo  next Windows login.
echo.
echo  Launcher installed at:
echo  %LAUNCHER%
echo.
echo  To undo, run:
echo  windows-startup\remove-startup.bat
echo.
pause
