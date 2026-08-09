@echo off
REM ============================================================
REM  Nahin AI - Remove Auto Start
REM  Removes NahinAI-Startup.bat from the Windows Startup folder.
REM  The project itself is NOT touched or deleted.
REM
REM  Run manually:
REM      windows-startup\remove-startup.bat
REM ============================================================
title Nahin AI - Remove Auto Start

set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "LAUNCHER=%STARTUP_FOLDER%\NahinAI-Startup.bat"

if exist "%LAUNCHER%" (
    del /f "%LAUNCHER%" >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Could not remove the launcher. Try running as the same user you logged in as.
        pause
        exit /b 1
    )
    echo.
    echo ==============================================
    echo  [SUCCESS] Nahin AI auto-start was removed.
    echo ==============================================
    echo.
    echo  Nahin AI will no longer start automatically.
    echo  The project files were not touched.
) else (
    echo.
    echo  Nahin AI auto-start was not installed.
    echo  Nothing to remove.
)

echo.
pause
