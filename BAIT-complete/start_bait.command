#!/bin/zsh

# BAIT macOS Launcher
# Double-click this file to start the application
echo "🚀 Starting BAIT PRO ULTIMATE..."

# Check for Terminal permissions (optional but helpful)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # Simple check for screen recording permission (via screencapture)
    # This won't prompt but helps logging
    logger "BAIT: Launcher started check for macOS"
fi

cd "$(dirname "$0")"

# Activate virtual environment
if [ -d "venv" ]; then
    echo "🐍 Activating virtual environment..."
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Please run ./install.sh first."
    exit 1
fi

# Start Backend
echo "📡 Starting Backend API (api_server.py)..."
python3 api_server.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start Frontend
echo "💻 Starting Frontend (Vite)..."
if command -v npm &> /dev/null; then
    npm run dev &
    FRONTEND_PID=$!
else
    echo "❌ npm not found! Please install Node.js."
fi

# Function to handle cleanup on exit
cleanup() {
    echo "👋 Shutting down BAIT..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

# Trap exit signals
trap cleanup SIGINT SIGTERM EXIT

# Open browser
echo "🌐 Opening BAIT Interface..."
sleep 5
open http://localhost:5173

echo "✅ BAIT is running! Use Ctrl+C to stop."
wait
