#!/bin/bash

echo "🚀 Starting BAIT macOS Environment Setup..."

# Check for Homebrew
if ! command -v brew &> /dev/null; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add brew to path for current session
    if [[ $(uname -m) == "arm64" ]]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    else
        eval "$(/usr/local/bin/brew shellenv)"
    fi
else
    echo "✅ Homebrew is already installed."
fi

# Install system dependencies
echo "📦 Installing system dependencies via Homebrew..."
# portaudio is essential for pyaudio/STT
# ffmpeg is essential for audio processing
brew install portaudio ffmpeg python@3.11 node

# Create virtual environment
echo "🐍 Setting up Python virtual environment..."
# Clean up existing venv if it's broken
if [ -d "venv" ]; then
    echo "Cleaning up existing environment..."
    rm -rf venv
fi

python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies (this may take a few minutes)..."
pip install --upgrade pip
pip install -r requirements_mac.txt

# Install Node dependencies
echo "📦 Installing Node dependencies..."
npm install

echo "✅ Setup complete! You can now run the app using one-click: ./BAIT_LAUNCHER.command"
chmod +x start_bait.command
chmod +x BAIT_LAUNCHER.command
