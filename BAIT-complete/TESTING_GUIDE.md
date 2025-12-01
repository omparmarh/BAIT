# BAIT PRO ULTIMATE - Complete Testing & Launch Guide

## 🧪 STEP 1: Verify Installation Requirements

### Required Software
- ✅ **Python 3.8+** (check: `python --version`)
- ✅ **Node.js 16+** (check: `node --version`)
- ✅ **npm** (check: `npm --version`)

---

## 🔧 STEP 2: Install Dependencies

### Backend Dependencies
```bash
cd "BAIT-complete (1) - Copy\BAIT-complete\backend"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Dependencies
```bash
cd "BAIT-complete (1) - Copy\BAIT-complete"
npm install
```

**Note**: This will install:
- React Three Fiber (for 3D avatar)
- Framer Motion (animations)
- React Webcam (camera support)
- Wavesurfer.js (audio visualization)
- All other frontend dependencies

---

## ⚙️ STEP 3: Configure Environment

1. **Copy `.env.example` to `.env`**:
```bash
copy .env.example .env
```

2. **Edit `.env` file** (optional for advanced features):
```env
# LLM Configuration
LLM_API_BASE=http://localhost:1234/v1
LLM_API_KEY=lm-studio

# Optional API Keys (add if you want these features)
OPENAI_API_KEY=your-key-here
SPOTIFY_CLIENT_ID=your-id-here
OPENWEATHER_API_KEY=your-key-here
```

---

## 🚀 STEP 4: Launch BAIT PRO ULTIMATE

### Option A: One-Click Launch (Recommended)
```bash
START_BAIT_ULTIMATE.bat
```

This will:
- ✅ Check all dependencies
- ✅ Start Python backend (port 8000)
- ✅ Start React frontend (port 5173)
- ✅ Open browser automatically

### Option B: Manual Launch

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate
python ../api_server.py
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

**Terminal 3 - Electron (Optional):**
```bash
npm run electron
```

---

## 🧪 STEP 5: Run Integration Tests

```bash
# Activate backend virtualenv first
cd backend
venv\Scripts\activate

# Run tests
cd ..
python tests\integration_tests.py
```

**Expected Output:**
```
Testing Voice Control...
Testing Memory System...
Testing Workflow Automation...
Testing Vision System...
Testing Browser Agent...
Testing Desktop Control...
Testing File Manager...
Testing Avatar Controller...
Testing API Integrations...

----------------------------------------------------------------------
Ran 9 tests in X.XXXs

OK
```

---

## 🎯 STEP 6: Verify Each Module

### 1. Voice Control
- Click "🎤 Voice" tab
- Click "Start Voice Control"
- ✅ Should see waveform animation

### 2. Memory System
- Click "🧠 Memory" tab
- Add a test memory
- Search for it
- ✅ Should find the memory

### 3. Workflows
- Click "⚡ Workflows" tab
- Type: "Every day at 10am, log test"
- Click "Create Workflow"
- ✅ Should appear in workflow list

### 4. Screen Preview
- Click "📸 Screen" tab
- Click "Capture"
- ✅ Should show OCR analysis

### 5. Camera & Gestures
- Click "📷 Camera" tab
- Click "Start Camera"
- ✅ Should show webcam feed

### 6. Browser Agent
- Click "🌐 Browser" tab
- Search for "test query"
- ✅ Should show Google results

### 7. Desktop Control
- Click "🖥️ Desktop" tab
- Click "Refresh"
- ✅ Should list active windows

### 8. File Manager
- Click "📁 Files" tab
- Search for a file
- ✅ Should show results

### 9. API Integrations
- Click "🔌 APIs" tab
- ✅ Should show integration cards

### 10. 3D Avatar (in Chat)
- Click "💬 Chat" tab
- ✅ Should see animated 3D sphere

---

## 🐛 TROUBLESHOOTING

### Backend Won't Start
```bash
# Check Python version
python --version  # Must be 3.8+

# Reinstall dependencies
cd backend
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Frontend Won't Start
```bash
# Clear cache
rmdir /s /q node_modules
del package-lock.json
npm install

# Or
npm cache clean --force
npm install
```

### "Module Not Found" Errors
```bash
# Backend
pip install [missing-module]

# Frontend
npm install [missing-module]
```

### Port Already in Use
```bash
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID [PID_NUMBER] /F

# Kill process on port 5173
netstat -ano | findstr :5173
taskkill /PID [PID_NUMBER] /F
```

### Camera Not Working
- Check browser permissions
- Allow camera access when prompted
- Try a different browser

### Voice Control Issues
- Check microphone permissions
- Ensure microphone is not in use by another app
- Install PyAudio: `pip install pyaudio`

---

## 📊 Known Limitations

1. **Heavy Dependencies**: Some modules (dlib, mediapipe) may need C++ build tools
2. **API Keys Required**: Full functionality needs external API keys
3. **Windows Only**: Tested on Windows (Mac/Linux may need adjustments)
4. **Resource Intensive**: 3D avatar and camera use GPU

---

##  SUCCESS CHECKLIST

- [ ] Backend starts without errors (http://localhost:8000)
- [ ] Frontend loads (http://localhost:5173)
- [ ] All 10 tabs are visible in navigation
- [ ] Can click between tabs
- [ ] Memory panel can store/recall data
- [ ] Workflow panel can create workflows
- [ ] Integration tests pass

---

## 🎉 You're Ready!

The system is fully operational. Access at: **http://localhost:5173**

For API documentation, see: `API_DOCS.md`
