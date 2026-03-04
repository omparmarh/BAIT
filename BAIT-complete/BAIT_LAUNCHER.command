#!/bin/zsh

# BAIT PRO ULTIMATE - macOS One-Click Launcher
# This script starts the Backend, Frontend, and the Desktop App

echo "🚀 Starting BAIT PRO ULTIMATE..."

# Change to the project directory
cd "$(dirname "$0")"

# Add common paths for Node.js and Python
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:/opt/homebrew/sbin:$PATH"

# Kill anything currently running on port 8000 to avoid "address already in use"
echo "🕸️  Cleaning up port 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found! Please install it from nodejs.org or use brew install node."
    echo "If you have it installed, make sure it's in your PATH."
    exit 1
fi

# Check for virtual environment
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found! Attempting to create one..."
    if [ -f "install.sh" ]; then
        chmod +x install.sh
        ./install.sh
    else
        echo "❌ install.sh not found! Cannot automatically set up."
        exit 1
    fi
fi

# Run the unified start script from package.json
# This runs: vite + electron (backend is started by electron)
echo "📡 Initializing servers and launching App..."
npm start
