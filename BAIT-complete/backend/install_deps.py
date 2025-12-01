#!/usr/bin/env python3
"""
BAIT PRO ULTIMATE - Quick Dependency Installer & Fixer
Installs all required dependencies and tests backend modules
"""

import subprocess
import sys
import os

def run_command(cmd):
    """Run command and print output"""
    print(f"\n{'='*60}")
    print(f"Running: {cmd}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    return result.returncode == 0

def main():
    print("🚀 BAIT PRO ULTIMATE - Dependency Installer")
    print("="*60)
    
    # List of dependencies to install
    dependencies = [
        # Core
        "fastapi uvicorn python-dotenv pydantic",
        # Vision & Camera
        "opencv-python pillow pytesseract mediapipe",
        # Browser & Web
        "selenium beautifulsoup4 lxml requests",
        # Desktop Control
        "pyautogui pygetwindow",
        # Memory & Search
        "chromadb whoosh",
        # Automation
        "schedule",
        # Voice (optional, may fail)
        "SpeechRecognition pydub",
    ]
    
    print("\n📦 Installing dependencies...")
    
    for dep_group in dependencies:
        print(f"\n Installing: {dep_group}")
        success = run_command(f"pip install {dep_group}")
        if not success:
            print(f"⚠️ Warning: Failed to install {dep_group}")
            print("Continuing anyway...")
    
    print("\n✅ Dependency installation complete!")
    
    # Test imports
    print("\n🧪 Testing backend module imports...")
    test_modules = [
        "fastapi",
        "cv2",
        "selenium",
        "bs4",
        "whoosh",
        "chromadb",
        "schedule"
    ]
    
    for module in test_modules:
        try:
            __import__(module)
            print(f"✅ {module} - OK")
        except ImportError as e:
            print(f"❌ {module} - FAILED: {e}")
    
    print("\n" + "="*60)
    print("✅ Setup Complete!")
    print("="*60)
    print("\nTo start BAIT:")
    print("1. python api_server.py")
    print("2. npm run dev (in another terminal)")

if __name__ == "__main__":
    main()
