# BAIT — AI Assistant

**BAIT** (Browser AI Integration Tool) is a locally-hosted AI assistant with a React frontend and a Python FastAPI backend. It supports voice input, chat, web research, notes, file management, and more.

---

## ✨ Features

| Feature | Description |
|---|---|
| 💬 Chat | Conversational AI powered by a local LLM (LM Studio) |
| 🎤 Voice Input | Microphone-based speech-to-text |
| 🔊 TTS | Hyper-human text-to-speech via `edge-tts` |
| 🌐 Web Research | Auto-search DuckDuckGo / Wikipedia for real-time info |
| 📝 Live Notes | Create and manage notes from the UI |
| 🗂 File Manager | Search, organize, and deduplicate files |
| 🧠 Memory | Persistent memory system using SQLite |
| 🤖 Automation | Natural-language workflow builder |
| 📷 Vision | Screen analysis and camera presence detection |
| 🖥 Desktop Control | Window management and macro recording |
| 🎭 Avatar | Lip-sync and expression controller |

---

## 🛠 Tech Stack

- **Frontend:** React 18 + Vite + CSS
- **Backend:** Python 3.9+ · FastAPI · Uvicorn
- **LLM:** OpenAI-compatible API (defaults to [LM Studio](https://lmstudio.ai) on `localhost:1234`)
- **Database:** SQLite (chat history + memory)
- **Desktop App:** Electron (optional)

---

## 🚀 Quick Start (macOS)

### 1. Install dependencies

```bash
chmod +x install.sh
./install.sh
```

This installs Homebrew, PortAudio, ffmpeg, Python 3.11, Node.js, and all project dependencies.

### 2. Configure your LLM

Copy the example environment file and edit it:

```bash
cp BAIT-complete/.env.example BAIT-complete/.env
```

Edit `.env`:
```env
LLM_API_BASE=http://127.0.0.1:1234/v1   # Your LM Studio URL
LLM_API_KEY=lm-studio
```

> You can also use any OpenAI-compatible API by changing `LLM_API_BASE`.

### 3. Run the app

```bash
./BAIT-complete/start_bait.command
```

Or manually:

```bash
# Terminal 1 — Backend
cd BAIT-complete
source venv/bin/activate
python3 api_server.py

# Terminal 2 — Frontend
cd BAIT-complete
npm run dev
```

Open **http://localhost:5173** in your browser.

---

## 📁 Project Structure

```
BAIT-complete/
├── api_server.py          # Main FastAPI backend
├── backend/
│   ├── api_routes.py      # Extended API endpoints
│   ├── voice_engine.py    # STT / voice control
│   ├── vision_processor.py# Screen & camera analysis
│   ├── memory_system.py   # Persistent memory (SQLite)
│   ├── automation_engine.py# Workflow automation
│   ├── browser_agent.py   # Web scraping & search
│   ├── desktop_controller.py# Window & input control
│   ├── file_manager.py    # File indexing & organizer
│   ├── avatar_controller.py# Lip-sync & expressions
│   ├── api_integrations.py# Spotify, Google, etc.
│   └── history_manager.py # Chat history persistence
├── src/                   # React frontend source
├── public/                # Electron main process
├── requirements_mac.txt   # Python dependencies (macOS)
├── package.json           # Node dependencies
└── vite.config.js         # Frontend build config
```

---

## 🔧 macOS Permissions

Grant these permissions when prompted (System Settings → Privacy & Security):

- **Microphone** — for voice input
- **Screen Recording** — for screen analysis
- **Accessibility** — for desktop control

---

## 💻 Electron Desktop App (Optional)

```bash
cd BAIT-complete
npm run electron      # Run as desktop window
npm run dist          # Build .dmg / .app bundle
```

---

## 📦 Installing Python Dependencies Manually

```bash
cd BAIT-complete
python3 -m venv venv
source venv/bin/activate
pip install -r requirements_mac.txt
```

---

## 🐛 Troubleshooting

| Problem | Fix |
|---|---|
| Port 8000 in use | `lsof -ti:8000 \| xargs kill -9` |
| `pyaudio` install fails | Run `brew install portaudio` first |
| LLM not responding | Make sure LM Studio is running with a model loaded |
| Voice not working | Check Microphone permission in System Settings |

---

## 📄 License

MIT — feel free to fork and build on it.
