@echo off
REM ═══════════════════════════════════════════════════════════════
REM BAIT PRO ULTIMATE - Master Launcher
REM Starts all components of the BAIT system
REM ═══════════════════════════════════════════════════════════════

color 0A
title BAIT PRO ULTIMATE Launcher

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║          BAIT PRO ULTIMATE - Master Launcher                 ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Check Python
echo [1/4] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+
    pause
    exit /b 1
)
echo ✅ Python found

REM Check Node.js
echo [2/4] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found! Please install Node.js 16+
    pause
    exit /b 1
)
echo ✅ Node.js found

REM Install Python dependencies
echo [3/4] Installing Python dependencies...
cd backend
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate
pip install -r requirements.txt --quiet
cd ..
echo ✅ Python dependencies ready

REM Install Node dependencies
echo [4/4] Installing Node dependencies...
if not exist node_modules (
    echo Installing packages...
    call npm install --silent
)
echo ✅ Node dependencies ready

echo.
echo ══════════════════════════════════════════════════════════════
echo  Starting BAIT PRO ULTIMATE...
echo ══════════════════════════════════════════════════════════════
echo.

REM Start Python backend
echo 🚀 Starting Python backend server...
start "BAIT Backend" cmd /k "cd backend && venv\Scripts\activate && python ../api_server.py"

REM Wait for backend
echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak >nul

REM Start frontend
echo 🚀 Starting React frontend...
start "BAIT Frontend" cmd /k "npm run dev"

REM Wait for frontend
timeout /t 3 /nobreak >nul

REM Open browser
echo 🌐 Opening browser...
timeout /t 3 /nobreak >nul
start http://localhost:5173

echo.
echo ══════════════════════════════════════════════════════════════
echo  ✅ BAIT PRO ULTIMATE is running!
echo ══════════════════════════════════════════════════════════════
echo.
echo  Backend:  http://localhost:8000
echo  Frontend: http://localhost:5173
echo.
echo  Press any key to shutdown all components...
echo ══════════════════════════════════════════════════════════════
pause >nul

REM Cleanup - kill all related processes
echo.
echo Shutting down...
taskkill /FI "WINDOWTITLE eq BAIT Backend*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq BAIT Frontend*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq BAIT*" /T /F >nul 2>&1

echo ✅ Shutdown complete
timeout /t 2 /nobreak >nul
