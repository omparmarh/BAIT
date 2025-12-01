@echo off
REM ════════════════════════════════════════════════════════════════
REM  BAIT ONE-CLICK LAUNCHER
REM  Installs everything and starts the system
REM ════════════════════════════════════════════════════════════════

title BAIT - Starting...
color 0B
cls

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                   🤖 BAIT LAUNCHER 🤖                         ║
echo ║              Personal AI Assistant System                     ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python not found!
    echo Please install Python 3.8+ from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo ✅ Python found!

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Node.js not found!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Node.js found!
echo.

REM Install Python dependencies
echo ⏳ Installing Python dependencies...
if not exist "venv" (
    python -m venv venv
)
call venv\Scriptsctivate.bat
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install Python dependencies
    pause
    exit /b 1
)
echo ✅ Python dependencies installed!

REM Install NPM dependencies
echo ⏳ Installing NPM dependencies...
if not exist "node_modules" (
    call npm install -q
)
if errorlevel 1 (
    echo ❌ Failed to install NPM dependencies
    pause
    exit /b 1
)
echo ✅ NPM dependencies installed!
echo.

REM Create database directory
if not exist "data" mkdir data

REM Start backend
echo ⏳ Starting BAIT Backend (FastAPI)...
start "BAIT Backend" cmd /k "call venv\Scriptsctivate.bat && python api_server.py"
echo ✅ Backend started on http://127.0.0.1:8000

REM Wait for backend to start
timeout /t 3 /nobreak

REM Start frontend
echo ⏳ Starting BAIT Frontend (React + Vite)...
start "BAIT Frontend" cmd /k "npm run dev"
echo ✅ Frontend starting on http://127.0.0.1:5173

REM Wait for frontend to start
timeout /t 5 /nobreak

REM Open browser
echo ⏳ Opening browser...
start http://127.0.0.1:5173

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║           🎉 BAIT IS READY! Welcome to the future!           ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo 📍 Backend: http://127.0.0.1:8000
echo 📍 Frontend: http://127.0.0.1:5173
echo.
echo 💡 TIPS:
echo   • Loading screen should appear in your browser
echo   • Click START to begin
echo   • All conversations are saved automatically
echo   • View history in the left sidebar
echo.
echo Press any key to keep the window open...
pause >nul

:end
