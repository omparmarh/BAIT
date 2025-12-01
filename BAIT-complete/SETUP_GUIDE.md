# BAIT PRO ULTIMATE - Quick Setup Guide

## 🚀 Quick Start (5 Minutes)

### 1. Prerequisites
- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **Node.js 16+** - [Download](https://nodejs.org/)
- **Git** - [Download](https://git-scm.com/)

### 2. One-Click Launch
```bash
# Navigate to project
cd "BAIT-complete (1) - Copy/BAIT-complete"

# Double-click to start
START_BAIT_ULTIMATE.bat
```

That's it! The launcher will:
- ✅ Check dependencies
- ✅ Install packages
- ✅ Start backend server
- ✅ Start frontend app
- ✅ Open browser automatically

---

## 📝 Manual Setup (Optional)

### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Frontend Setup
```bash
# Install Node packages
npm install
```

### Configuration
1. Copy `.env.example` to `.env`
2. Add your API keys:
   - `OPENAI_API_KEY` - For Whisper STT, GPT-4 Vision
   - `SPOTIFY_CLIENT_ID` & `SPOTIFY_CLIENT_SECRET` - For music control
   - `OPENWEATHER_API_KEY` - For weather
   - etc.

### Manual Start
```bash
# Terminal 1: Backend
cd backend
venv\Scripts\activate
python ../api_server.py

# Terminal 2: Frontend
npm run dev
```

---

## 🔧 Optional Dependencies

### For Full Features
```bash
# Tesseract OCR (for screen text extraction)
# Download: https://github.com/UB-Mannheim/tesseract/wiki

# dlib (for face recognition) - May require Visual C++ Build Tools
pip install dlib

# MediaPipe (for gesture recognition)
pip install mediapipe
```

---

## 🎯 Features Overview

| Module | Functionality | Status |
|--------|--------------|--------|
| 🎤 **Voice Control** | "Hey BAIT" wake word, STT | ✅ Ready |
| 🧠 **Memory System** | Semantic search, learning | ✅ Ready |
| ⚡ **Automation** | Natural language workflows | ✅ Ready |
| 👁️ **Vision** | Screen OCR, face/gesture recognition | ✅ Ready |
| 🌐 **Browser Agent** | Web scraping, automation | ✅ Ready |
| 🖥️ **Desktop Control** | Window management, macros | ✅ Ready |
| 📁 **File Manager** | Smart search, organization | ✅ Ready |
| 🎭 **Avatar** | Lip sync, expressions | ✅ Ready |
| 🔌 **API Hub** | Spotify, Gmail, Weather | ✅ Ready |

---

## 🌐 Endpoints

After starting, access:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs *(if enabled)*

### Key API Endpoints
```
POST /api/ultimate/voice/start
POST /api/ultimate/memory/store
POST /api/ultimate/workflow/create
GET  /api/ultimate/vision/analyze-screen
POST /api/ultimate/browser/search
GET  /api/ultimate/desktop/windows
POST /api/ultimate/files/organize
POST /api/ultimate/avatar/lip-sync
```

---

## ⚙️ Configuration Files

- `.env` - API keys and settings
- `workflows.json` - Saved automation workflows
- `memory.db` - SQLite memory database
- `bait.db` - Main conversation database

---

## 🐛 Troubleshooting

### Backend won't start
- Check Python version: `python --version`
- Ensure venv activated: `venv\Scripts\activate`
- Install deps: `pip install -r backend/requirements.txt`

### Frontend won't start
- Check Node version: `node --version`
- Clear cache: `rm -rf node_modules package-lock.json`
- Reinstall: `npm install`

### API key errors
- Verify `.env` file exists
- Check API keys are valid
- Some features work without keys (local models)

---

## 📚 Usage Examples

### Voice Control
1. Click "Start Voice Control" in UI
2. Say "Hey BAIT"
3. Speak your command
4. AI responds with TTS

### Create Workflow
```
Type: "Every day at 9am, open Chrome and go to Gmail.com"
Click: Create Workflow
Result: Automation runs daily
```

### Memory System
```
Add memory: "User prefers Python for backend"
Search: "programming language"
Result: Finds relevant memories
```

---

**Status**: Production Ready
**Version**: 1.0.0 (PRO ULTIMATE)
**Support**: See documentation in walkthrough.md
