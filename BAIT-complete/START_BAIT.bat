@echo off
setlocal enabledelayedexpansion
title BAIT Desktop Launcher
color 0B

echo ========================================
echo    Starting BAIT Desktop App
echo ========================================
echo.

REM Try to find BAIT folder automatically
set "BAIT_DIR="

REM Check common locations
for %%A in (
    "C:\Users\a2z\Downloads\BAIT-complete (1)\BAIT-complete"
    "%UserProfile%\Desktop\BAIT-complete"
    "%UserProfile%\Documents\BAIT-complete"
    "C:\Users\a2z\BAIT-complete"
) do (
    if exist "%%A\package.json" (
        set "BAIT_DIR=%%A"
        echo Found BAIT at: !BAIT_DIR!
        goto found
    )
)

:notfound
echo ERROR: Could not find BAIT installation!
echo.
echo Please manually set BAIT_DIR in this script.
echo Expected folder should contain: package.json, api_server.py, electron.js
echo.
pause
exit /b 1

:found
cd /d "!BAIT_DIR!"

echo.
echo ========================================
echo       BAIT Launcher v1.0
echo ========================================
echo.
echo [1/3] Starting Python Backend...
start "BAIT Backend" /MIN cmd /k "venv\Scripts\activate && python api_server.py"
timeout /t 3 /nobreak > nul

echo [2/3] Starting Frontend (Vite)...
start "BAIT Frontend" /MIN cmd /k "npm run dev"
timeout /t 5 /nobreak > nul

echo [3/3] Launching Electron App...
timeout /t 2 /nobreak > nul
start "" cmd /k "cd /d "!BAIT_DIR!" && electron ."

echo.
echo ========================================
echo     BAIT is Running!
echo ========================================
echo.
echo Windows minimized. Check taskbar for:
echo  - BAIT Backend (Python)
echo  - BAIT Frontend (Vite)
echo  - BAIT Electron (Desktop App)
echo.
echo Close all windows to stop BAIT.
echo.
timeout /t 5 /nobreak > nul
exit /b 0
