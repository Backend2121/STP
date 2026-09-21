@echo off
setlocal
cd /d "%~dp0"
title STP

if not exist "venv\Scripts\python.exe" (
    echo STP is not installed yet. Run install.bat first.
    pause
    exit /b 1
)

"venv\Scripts\python.exe" main.py
if errorlevel 1 (
    echo.
    echo STP exited with an error, see the messages above.
    pause
    exit /b 1
)
