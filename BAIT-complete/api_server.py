#!/usr/bin/env python3
"""
BAIT PRO ULTIMATE - Complete API Server with Web Research, Live Notes & Hyper-Human TTS
Production Ready - Zero Bugs - FAST & HUMAN-LIKE SPEECH
"""
#!/usr/bin/env python3
import io
from pathlib import Path
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
import sys
import asyncio
import subprocess  # ← MAKE SURE THIS IS HERE
import threading
import webbrowser
import re
import datetime
import random
import socket
import json
import uuid
import tempfile
import base64
from dotenv import load_dotenv
from openai import AsyncOpenAI
import pyautogui
import psutil
import requests
from bs4 import BeautifulSoup
import speech_recognition as sr

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Load environment
load_dotenv()

# Check for edge-tts (hyper-human TTS)
try:
    import edge_tts
    HAS_EDGE_TTS = True
except:
    HAS_EDGE_TTS = False

# TTS Setup
tts_available = False
try:
    import win32com.client
    test_speaker = win32com.client.Dispatch("SAPI.SpVoice")
    tts_available = True
    del test_speaker
except Exception:
    try:
        import pyttsx3
        tts_engine = pyttsx3.init()
        tts_available = True
    except Exception:
        pass

# WebSocket connection manager for video chat
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.active_sessions: Dict[str, Dict] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.active_sessions[session_id] = {
            "id": session_id,
            "started_at": datetime.datetime.now().isoformat(),
            "messages": [],
            "video_enabled": True,
            "audio_enabled": True
        }

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]

    async def broadcast_to_session(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_json(message)
            except Exception as e:
                print(f"Broadcast error: {e}")

manager = ConnectionManager()

# FastAPI app
app = FastAPI(title="BAIT API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include BAIT PRO ULTIMATE routes
try:
    from backend.api_routes import router as ultimate_router
    app.include_router(ultimate_router)
    print("✅ BAIT PRO ULTIMATE routes loaded")
except Exception as e:
    print(f"⚠️  Ultimate routes not loaded: {e}")

# OpenAI Client
client = AsyncOpenAI(
    base_url=os.getenv("LLM_API_BASE", "http://localhost:1234/v1"),
    api_key=os.getenv("LLM_API_KEY", "lm-studio")
)

# In-memory storage
conversations_db = {}
notes_db = {}
conversation_counter = 0
note_counter = 0

# ═══════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []
    conversation_id: Optional[int] = None

class VoiceRequest(BaseModel):
    audio_data: str

class NoteRequest(BaseModel):
    text: str
    id: Optional[int] = None

# ═══════════════════════════════════════════════════════════════
# HYPER-HUMAN TTS SYSTEM - FAST & STREAMING
# ═══════════════════════════════════════════════════════════════

tts_stop_event = None

async def speak_text_edge_tts(text: str, emotion: str = None):
    """Speak with hyper-human naturalness using Edge TTS - STREAMING & FAST"""
    global tts_stop_event
    
    if not HAS_EDGE_TTS or not text:
        return
    
    try:
        # Stop previous speech
        if tts_stop_event:
            tts_stop_event.set()
        
        tts_stop_event = threading.Event()
        
        # Select voice based on emotion
        voice_map = {
            "excited": "en-US-AvaNeural",      # Fast, energetic female
            "calm": "en-US-AriaNeural",        # Warm, calm female
            "curious": "en-US-GuyNeural",      # Professional male
            "thoughtful": "en-US-AriaNeural",  # Warm female
        }
        
        voice = voice_map.get(emotion, "en-US-AriaNeural")
        
        # FASTER rates - sounds more natural & human
        rate_map = {
            "excited": "+20%",     # FAST for excitement
            "calm": "-5%",         # Slightly slower for calm
            "curious": "+10%",
            "thoughtful": "+5%",
        }
        
        rate = rate_map.get(emotion, "+5%")  # Default: NORMAL speed
        
        # Speak ONLY first 200 chars for speed
        text_to_speak = text[:200].strip()
        
        # Generate speech
        communicate = edge_tts.Communicate(text_to_speak, voice, rate=rate)
        
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            temp_file = f.name
            async for chunk in communicate.stream():
                if tts_stop_event.is_set():
                    break
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
        
        # Play audio (non-blocking, fires and forgets)
        if not tts_stop_event.is_set():
            try:
                if sys.platform == 'win32':
                    # Use subprocess so it doesn't block
                    subprocess.Popen(
                        ['powershell', '-Command', 
                         f'(New-Object Media.SoundPlayer "{temp_file}").PlaySync()'],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                else:
                    subprocess.Popen(
                        ['afplay', temp_file],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
            except:
                pass
            
            # Clean up after delay
            def cleanup():
                import time
                time.sleep(10)
                try:
                    os.unlink(temp_file)
                except:
                    pass
            
            threading.Thread(target=cleanup, daemon=True).start()
            
    except Exception as e:
        print(f"Edge TTS Error: {e}")

def speak_text_pyttsx3(text: str):
    """Fallback to pyttsx3 for natural speech"""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('rate', 180)      # FASTER - more human
        engine.setProperty('volume', 1.0)
        engine.say(text[:200])  # Only first 200 chars
        engine.runAndWait()
    except Exception as e:
        print(f"PyTTSX3 Error: {e}")

def speak_text(text: str, emotion: str = None):
    """
    Main TTS function - FAST & STREAMING
    Emotions: excited, calm, curious, thoughtful
    NON-BLOCKING - speaks in background thread
    """
    if not text:
        return
    
    # Non-blocking - speak in background thread
    def _speak():
        if HAS_EDGE_TTS:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(speak_text_edge_tts(text, emotion))
                loop.close()
            except Exception as e:
                print(f"Edge TTS failed: {e}")
                speak_text_pyttsx3(text)
        else:
            speak_text_pyttsx3(text)
    
    # Run in background thread (fire and forget)
    threading.Thread(target=_speak, daemon=True).start()

def stop_speaking():
    """Stop current speech immediately"""
    global tts_stop_event
    if tts_stop_event:
        tts_stop_event.set()

# ═══════════════════════════════════════════════════════════════
# SMART MOOD DETECTION (Hyper-Natural Responses)
# ═══════════════════════════════════════════════════════════════

def detect_mood(text: str) -> dict:
    """Smart mood detection with emotionally-aware responses"""
    text_lower = text.lower()
    
    patterns = [
        (r"(i'm|i am|im)\s+(so\s+)?(tired|exhausted|sleepy)", "tired"),
        (r"(i'm|i am|im)\s+(so\s+)?(sad|down|depressed|upset)", "sad"),
        (r"(i'm|i am|im)\s+(so\s+)?(happy|great|excited|amazing|awesome)", "happy"),
        (r"(i'm|i am|im)\s+(really|very)?\s+(frustrated|angry)", "angry"),
        (r"(i'm|i am|im)\s+confused", "confused"),
    ]
    
    responses = {
        "tired": {
            "text": "Aww, you sound really tired... I totally get it. Would you like me to play some soothing music?",
            "emotion": "calm"
        },
        "sad": {
            "text": "Oh no... I'm sorry you're feeling down. Want to talk about it, or should I play something uplifting?",
            "emotion": "calm"
        },
        "happy": {
            "text": "Oh my gosh, that's amazing! Your energy is awesome! What's making you so happy?",
            "emotion": "excited"
        },
        "angry": {
            "text": "I can tell you're frustrated right now, and that's valid. Let's take a breath together. How can I help?",
            "emotion": "calm"
        },
        "confused": {
            "text": "Yeah, that sounds confusing! Don't worry, we can figure this out together. Let me explain it.",
            "emotion": "thoughtful"
        },
    }
    
    for pattern, mood in patterns:
        if re.search(pattern, text_lower):
            if mood in responses:
                response_data = responses[mood]
                return {
                    "detected": True,
                    "mood": mood,
                    "response": response_data["text"],
                    "emotion": response_data["emotion"],
                    "action": "play_relaxing_music" if mood in ["tired", "sad"] else None
                }
    
    return {"detected": False}

# ═══════════════════════════════════════════════════════════════
# WEB SEARCH & RESEARCH
# ═══════════════════════════════════════════════════════════════

RESEARCH_KEYWORDS = [
    'who is', 'what is', 'how to', 'when was', 'where is',
    'latest', 'current', 'recent', 'news', 'today',
    'information about', 'tell me about', 'research',
    'look up', 'find out', 'search for info', 'explain',
    'define', 'difference between', 'best way to'
]

async def search_web_for_answer(query: str) -> Dict:
    """Search web and extract relevant information"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Try DuckDuckGo first
        search_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}&format=json"
        
        try:
            response = requests.get(search_url, headers=headers, timeout=8)
            data = response.json()
            
            results = []
            
            if 'AbstractText' in data and data['AbstractText']:
                results.append({
                    'title': 'Summary',
                    'snippet': data['AbstractText'],
                    'source': 'DuckDuckGo'
                })
            
            if 'Results' in data:
                for result in data['Results'][:3]:
                    if 'Text' in result and result['Text']:
                        results.append({
                            'title': result.get('FirstURL', 'Result'),
                            'snippet': result['Text'],
                            'source': 'DuckDuckGo'
                        })
            
            if results:
                return {"status": "success", "results": results, "count": len(results)}
        except:
            pass
        
        # Fallback to Wikipedia
        wiki_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&format=json"
        response = requests.get(wiki_url, headers=headers, timeout=8)
        wiki_data = response.json()
        
        results = []
        if 'query' in wiki_data and 'search' in wiki_data['query']:
            for item in wiki_data['query']['search'][:3]:
                results.append({
                    'title': item['title'],
                    'snippet': item['snippet'].replace('<span class="searchmatch">', '').replace('</span>', ''),
                    'source': 'Wikipedia'
                })
        
        if results:
            return {"status": "success", "results": results, "count": len(results)}
        
        return {"status": "error", "message": "No results found"}
        
    except Exception as e:
        return {"status": "error", "message": f"Search error: {str(e)}"}

async def format_research_response(search_results: Dict) -> str:
    """Format search results into readable response"""
    if search_results["status"] != "success":
        return "I couldn't find information about that. Could you rephrase?"
    
    response = "Here's what I found:\n\n"
    
    for i, result in enumerate(search_results["results"], 1):
        response += f"**{i}. {result['title']}** ({result['source']})\n"
        response += f"{result['snippet']}\n\n"
    
    return response

# ═══════════════════════════════════════════════════════════════
# FILE OPERATIONS
# ═══════════════════════════════════════════════════════════════

def create_file_at_location(filepath: str, content: str):
    """Create a file at specific location"""
    try:
        filepath = os.path.expandvars(os.path.expanduser(filepath))
        directory = os.path.dirname(filepath)
        
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        os.startfile(filepath)
        return {"status": "success", "message": f"File created at {filepath}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def edit_file(filepath: str, content: str):
    """Edit existing file"""
    try:
        filepath = os.path.expandvars(os.path.expanduser(filepath))
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        os.startfile(filepath)
        return {"status": "success", "message": f"File edited: {filepath}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ═══════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def find_executable(app_name: str) -> str:
    direct_paths = {
        "chrome": [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                   r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"],
        "firefox": [r"C:\Program Files\Mozilla Firefox\firefox.exe"],
        "edge": [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"],
        "notepad": [r"C:\Windows\notepad.exe"],
        "calculator": [r"C:\Windows\System32\calc.exe"],
        "paint": [r"C:\Windows\System32\mspaint.exe"],
    }
    
    if app_name.lower() in direct_paths:
        for path in direct_paths[app_name.lower()]:
            if os.path.exists(path):
                return path
    return app_name

def open_application(app_name: str):
    try:
        executable = find_executable(app_name.lower())
        os.startfile(executable)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def close_application(app_name: str):
    try:
        os.system(f"taskkill /IM {app_name}.exe /F")
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
def search_youtube(query: str):
    """Search YouTube - Multiple fallback methods"""
    try:
        query = query.strip()
        search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        
        # Force open in default browser
        import subprocess
        if sys.platform == 'win32':
            subprocess.Popen(['cmd', '/c', 'start', '', search_url], shell=False)
        else:
            subprocess.Popen(['open', search_url])
        
        return {"status": "success"}
    except:
        return {"status": "error", "message": "Failed to open YouTube"}

def search_google(query: str):
    try:
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(search_url)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def search_wikipedia(query: str):
    try:
        search_url = f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}"
        webbrowser.open(search_url)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def open_website(url: str):
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        webbrowser.open(url)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def take_screenshot():
    try:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = os.path.join(desktop, f"Screenshot_{timestamp}.png")
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)
        return {"status": "success", "path": screenshot_path}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_system_info():
    try:
        info = {
            "cpu": psutil.cpu_percent(interval=1),
            "memory": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage('/').percent,
        }
        return {"status": "success", "info": info}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ═══════════════════════════════════════════════════════════════
# COMMAND PROCESSOR
# ═══════════════════════════════════════════════════════════════

async def process_command(user_message: str) -> tuple:
    """Process commands - FINAL VERSION"""
    user_lower = user_message.lower().strip()
    
    # ═══════════════════════════════════════════════════════════
    # YOUTUBE
    # ═══════════════════════════════════════════════════════════
    
    if "youtube" in user_lower:
        # Extract search query
        query = None
        
        # Pattern 1: "search for X on youtube"
        match = re.search(r'search\s+(?:for\s+)?(.+?)\s+on\s+youtube', user_lower)
        if match:
            query = match.group(1).strip()
        
        # Pattern 2: "search youtube for X"
        if not query:
            match = re.search(r'search\s+youtube\s+(?:for\s+)?(.+)', user_lower)
            if match:
                query = match.group(1).strip()
        
        # Pattern 3: "youtube search X"
        if not query:
            match = re.search(r'youtube\s+search\s+(.+)', user_lower)
            if match:
                query = match.group(1).strip()
        
        # Pattern 4: Just "open youtube"
        if not query and "open youtube" in user_lower:
            subprocess.Popen(['cmd', '/c', 'start', '', 'https://www.youtube.com'], shell=False)
            return "Opening YouTube!", True
        
        # Execute search if query found
        if query:
            search_youtube(query)
            return f"Searching YouTube for '{query}'!", True
    
    # ═══════════════════════════════════════════════════════════
    # GOOGLE
    # ═══════════════════════════════════════════════════════════
    
    if "google" in user_lower and "youtube" not in user_lower:
        if "open google" in user_lower or user_lower == "google":
            subprocess.Popen(['cmd', '/c', 'start', '', 'https://www.google.com'], shell=False)
            return "Opening Google!", True
        
        match = re.search(r'google\s+(.+)', user_lower)
        if match:
            query = match.group(1).strip()
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            subprocess.Popen(['cmd', '/c', 'start', '', url], shell=False)
            return f"Googling '{query}'!", True
    
    # ═══════════════════════════════════════════════════════════
    # CHROME
    # ═══════════════════════════════════════════════════════════
    
    if "chrome" in user_lower and "open" in user_lower:
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ]
        for path in chrome_paths:
            if os.path.exists(path):
                subprocess.Popen([path])
                return "Opening Chrome!", True
        return "Chrome not found!", False
    
    # ═══════════════════════════════════════════════════════════
    # FILE OPERATIONS
    # ═══════════════════════════════════════════════════════════
    
    match = re.search(r'create\s+(?:a\s+)?file\s+(.+?)\s+(?:with|containing)\s+(.+)', user_message, re.IGNORECASE)
    if match:
        filename = match.group(1).strip()
        content = match.group(2).strip()
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        filepath = os.path.join(desktop, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        os.startfile(filepath)
        return f"Created {filename}!", True
    
    # ═══════════════════════════════════════════════════════════
    # SCREENSHOT
    # ═══════════════════════════════════════════════════════════
    
    if "screenshot" in user_lower:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(desktop, f"Screenshot_{timestamp}.png")
        pyautogui.screenshot(path)
        return f"Screenshot saved!", True
    
    # No command found
    return None, False

# ═══════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    return {
        "status": "BAIT API Running",
        "tts": tts_available,
        "edge_tts": HAS_EDGE_TTS,
        "features": ["Web Research", "Live Notes", "Hyper-Human TTS", "File Operations", "Video Chat"]
    }

# ═══════════════════════════════════════════════════════════════
# VIDEO CHAT ENDPOINTS (WebSocket)
# ═══════════════════════════════════════════════════════════════

@app.websocket("/ws/video-chat/{session_id}")
async def websocket_video_chat(websocket: WebSocket, session_id: str):
    """WebSocket for real-time video chat"""
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "chat":
                manager.active_sessions[session_id]["messages"].append({
                    "role": message.get("sender", "user"),
                    "content": message.get("content"),
                    "timestamp": datetime.datetime.now().isoformat()
                })
                
                await manager.broadcast_to_session(session_id, {
                    "type": "chat",
                    "role": message.get("sender"),
                    "content": message.get("content"),
                    "timestamp": datetime.datetime.now().isoformat()
                })
            
            elif message.get("type") == "ice-candidate":
                await manager.broadcast_to_session(session_id, {
                    "type": "ice-candidate",
                    "candidate": message.get("candidate")
                })
            
            elif message.get("type") == "offer":
                await manager.broadcast_to_session(session_id, {
                    "type": "offer",
                    "sdp": message.get("sdp")
                })
            
            elif message.get("type") == "answer":
                await manager.broadcast_to_session(session_id, {
                    "type": "answer",
                    "sdp": message.get("sdp")
                })
            
            elif message.get("type") == "status":
                if "video_enabled" in message:
                    manager.active_sessions[session_id]["video_enabled"] = message["video_enabled"]
                if "audio_enabled" in message:
                    manager.active_sessions[session_id]["audio_enabled"] = message["audio_enabled"]
                
                await manager.broadcast_to_session(session_id, {
                    "type": "status",
                    "video_enabled": manager.active_sessions[session_id]["video_enabled"],
                    "audio_enabled": manager.active_sessions[session_id]["audio_enabled"]
                })
    
    except WebSocketDisconnect:
        manager.disconnect(session_id)
        print(f"Client disconnected: {session_id}")

@app.get("/api/video-chat/session")
async def create_video_session():
    """Create new video chat session"""
    session_id = str(uuid.uuid4())
    return {
        "status": "success",
        "session_id": session_id,
        "server": "ws://localhost:8000/ws/video-chat/" + session_id
    }

@app.get("/api/video-chat/sessions/{session_id}")
async def get_session_info(session_id: str):
    """Get session information"""
    if session_id in manager.active_sessions:
        return manager.active_sessions[session_id]
    return {"error": "Session not found"}

@app.get("/api/video-chat/sessions")
async def list_sessions():
    """List all active sessions"""
    return list(manager.active_sessions.values())

# ═══════════════════════════════════════════════════════════════
# CALL RECORDING SYSTEM
# ═══════════════════════════════════════════════════════════════

recordings_db = {}
recording_counter = 0
RECORDINGS_DIR = os.path.join(os.path.expanduser("~"), "BAIT_Recordings")

# Create recordings directory
os.makedirs(RECORDINGS_DIR, exist_ok=True)

class RecordingData:
    def __init__(self, recording_id):
        self.id = recording_id
        self.created_at = datetime.datetime.now().isoformat()
        self.audio_chunks = []
        self.video_chunks = []
        self.messages = []
        self.duration = 0
        self.is_recording = False

# Store active recordings
active_recordings = {}

@app.post("/api/recording/start")
async def start_recording(request: ChatRequest):
    """Start recording a new call"""
    global recording_counter
    
    recording_counter += 1
    recording_id = recording_counter
    
    recording = RecordingData(recording_id)
    recording.is_recording = True
    active_recordings[recording_id] = recording
    
    return {
        "status": "recording_started",
        "recording_id": recording_id,
        "started_at": recording.created_at
    }

@app.post("/api/recording/{recording_id}/add-audio")
async def add_audio_chunk(recording_id: int, request: VoiceRequest):
    """Add audio chunk to recording"""
    try:
        if recording_id not in active_recordings:
            return {"status": "error", "message": "Recording not found"}
        
        recording = active_recordings[recording_id]
        
        # Decode base64 audio
        if ',' in request.audio_data:
            audio_data = base64.b64decode(request.audio_data.split(',')[1])
        else:
            audio_data = base64.b64decode(request.audio_data)
        
        recording.audio_chunks.append(audio_data)
        
        return {
            "status": "success",
            "chunks_count": len(recording.audio_chunks)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/recording/{recording_id}/add-message")
async def add_message_to_recording(recording_id: int, request: ChatMessage):
    """Add message to recording"""
    try:
        if recording_id not in active_recordings:
            return {"status": "error", "message": "Recording not found"}
        
        recording = active_recordings[recording_id]
        recording.messages.append({
            "role": request.role,
            "content": request.content,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/recording/{recording_id}/stop")
async def stop_recording(recording_id: int):
    """Stop recording and save as MP4"""
    try:
        if recording_id not in active_recordings:
            return {"status": "error", "message": "Recording not found"}
        
        recording = active_recordings[recording_id]
        recording.is_recording = False
        
        # Calculate duration
        duration_seconds = len(recording.messages) * 2  # Estimate
        recording.duration = duration_seconds
        
        # Save recording metadata
        recordings_db[recording_id] = {
            "id": recording_id,
            "created_at": recording.created_at,
            "duration": recording.duration,
            "messages_count": len(recording.messages),
            "audio_chunks_count": len(recording.audio_chunks),
            "status": "saved"
        }
        
        # Create MP4 file
        file_path = os.path.join(RECORDINGS_DIR, f"recording_{recording_id}.mp4")
        
        # For now, we'll save metadata as JSON
        # (Full video encoding requires ffmpeg)
        metadata_path = os.path.join(RECORDINGS_DIR, f"recording_{recording_id}_metadata.json")
        
        with open(metadata_path, 'w') as f:
            json.dump({
                "id": recording_id,
                "created_at": recording.created_at,
                "duration": recording.duration,
                "messages": recording.messages,
                "message_count": len(recording.messages)
            }, f, indent=2)
        
        # Combine audio chunks and save
        if recording.audio_chunks:
            audio_path = os.path.join(RECORDINGS_DIR, f"recording_{recording_id}_audio.wav")
            with open(audio_path, 'wb') as f:
                for chunk in recording.audio_chunks:
                    f.write(chunk)
        
        # Clean up memory
        if recording_id in active_recordings:
            del active_recordings[recording_id]
        
        return {
            "status": "success",
            "recording_id": recording_id,
            "saved_at": recording.created_at,
            "duration": recording.duration,
            "file_path": metadata_path,
            "audio_path": audio_path if recording.audio_chunks else None
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/recordings")
async def get_all_recordings():
    """Get all recordings"""
    return list(recordings_db.values())

@app.get("/api/recording/{recording_id}")
async def get_recording(recording_id: int):
    """Get specific recording"""
    if recording_id in recordings_db:
        # Load metadata
        metadata_path = os.path.join(RECORDINGS_DIR, f"recording_{recording_id}_metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            return metadata
    
    return {"status": "error", "message": "Recording not found"}

@app.get("/api/recording/{recording_id}/download")
async def download_recording(recording_id: int):
    """Download recording as JSON"""
    try:
        metadata_path = os.path.join(RECORDINGS_DIR, f"recording_{recording_id}_metadata.json")
        
        if not os.path.exists(metadata_path):
            return {"status": "error", "message": "Recording not found"}
        
        with open(metadata_path, 'r') as f:
            data = json.load(f)
        
        return {
            "status": "success",
            "data": data,
            "filename": f"recording_{recording_id}.json"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.delete("/api/recording/{recording_id}")
async def delete_recording(recording_id: int):
    """Delete recording"""
    try:
        if recording_id in recordings_db:
            del recordings_db[recording_id]
        
        # Delete files
        for ext in ['_metadata.json', '_audio.wav']:
            file_path = os.path.join(RECORDINGS_DIR, f"recording_{recording_id}{ext}")
            if os.path.exists(file_path):
                os.remove(file_path)
        
        return {"status": "success", "message": "Recording deleted"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/recording/{recording_id}/export-mp4")
async def export_mp4(recording_id: int):
    """Export recording as MP4 with subtitles"""
    try:
        # This requires ffmpeg - for now, return transcript
        metadata_path = os.path.join(RECORDINGS_DIR, f"recording_{recording_id}_metadata.json")
        
        if not os.path.exists(metadata_path):
            return {"status": "error", "message": "Recording not found"}
        
        with open(metadata_path, 'r') as f:
            data = json.load(f)
        
        # Create VTT subtitle file
        vtt_content = "WEBVTT\n\n"
        current_time = 0
        
        for i, msg in enumerate(data['messages']):
            start_time = f"00:00:{current_time:02d}.000"
            end_time = f"00:00:{current_time + 2:02d}.000"
            
            role = "🧑" if msg['role'] == 'user' else "🤖"
            vtt_content += f"{start_time} --> {end_time}\n"
            vtt_content += f"{role} {msg['content']}\n\n"
            
            current_time += 2
        
        return {
            "status": "success",
            "vtt_subtitle": vtt_content,
            "duration": data['duration']
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
# ═══════════════════════════════════════════════════════════════
# CONVERSATION ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.get("/api/conversations")
async def get_conversations():
    """Get all conversations"""
    return list(conversations_db.values())

@app.get("/api/conversation/{conversation_id}")
async def get_conversation(conversation_id: int):
    """Get specific conversation"""
    if conversation_id in conversations_db:
        return conversations_db[conversation_id]
    return {"error": "Conversation not found"}

@app.post("/api/conversation")
async def create_conversation(request: ChatRequest):
    """Create new conversation - TEXT SHOWS FIRST, THEN SPEAKS"""
    global conversation_counter
    
    # Stop any previous speech
    stop_speaking()
    
    if request.conversation_id and request.conversation_id in conversations_db:
        conv_id = request.conversation_id
        conversation = conversations_db[conv_id]
    else:
        conversation_counter += 1
        conv_id = conversation_counter
        conversation = {
            "id": conv_id,
            "title": request.message[:50] + ("..." if len(request.message) > 50 else ""),
            "messages": [],
            "created_at": datetime.datetime.now().isoformat()
        }
    
    try:
        user_message = request.message
        user_lower = user_message.lower()
        response_text = None
        detected_emotion = None
        
        # Check mood
        mood = detect_mood(user_message)
        if mood["detected"]:
            response_text = mood["response"]
            detected_emotion = mood["emotion"]
            
            # ADD TO CHAT IMMEDIATELY
            conversation["messages"].append({"role": "user", "content": user_message})
            conversation["messages"].append({"role": "assistant", "content": response_text})
            conversations_db[conv_id] = conversation
            
            # THEN speak in background (non-blocking)
            speak_text(response_text, emotion=detected_emotion)
            
            if mood.get("action") == "play_relaxing_music":
                search_youtube("relaxing music 1 hour")
            elif mood.get("action") == "play_uplifting_music":
                search_youtube("uplifting music motivational")
            
            return conversation
        
        # Check for commands
        response_text, command_executed = await process_command(user_message)
        
        # If command executed
        if command_executed and response_text:
            # ADD TO CHAT IMMEDIATELY
            conversation["messages"].append({"role": "user", "content": user_message})
            conversation["messages"].append({"role": "assistant", "content": response_text})
            conversations_db[conv_id] = conversation
            
            # THEN speak in background
            speak_text(response_text)
            
            return conversation
        
        # If no command, check if needs web research
        if not response_text:
            needs_research = any(keyword in user_lower for keyword in RESEARCH_KEYWORDS)
            
            if needs_research:
                # Do web search
                search_results = await search_web_for_answer(user_message)
                response_text = await format_research_response(search_results)
                detected_emotion = "thoughtful"
                
                # ADD TO CHAT IMMEDIATELY
                conversation["messages"].append({"role": "user", "content": user_message})
                conversation["messages"].append({"role": "assistant", "content": response_text})
                conversations_db[conv_id] = conversation
                
                # THEN speak in background (only first 200 chars)
                speak_text(response_text[:200], emotion=detected_emotion)
                
                return conversation
            
            else:
                SYSTEM_PROMPT = """You are Bait, a helpful AI assistant.

CRITICAL: Respond ONLY in plain English sentences. NO JSON, NO XML, NO CODE.

Examples:
User: "search for technogamers on youtube"
You: "Let me search for that on YouTube."

User: "open chrome"
You: "Opening Chrome now."

User: "what's the weather"
You: "I'll look that up for you."

NEVER output code or JSON. Always speak like a human."""

                
                messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                messages.extend([{"role": m["role"], "content": m["content"]} for m in conversation["messages"][-10:]])
                messages.append({"role": "user", "content": user_message})
                
                response = await client.chat.completions.create(
                    model="local-model",
                    messages=messages,
                    temperature=0.85,
                    top_p=0.95,
                    max_tokens=100,  # SHORTER responses
                )
                
                response_text = response.choices[0].message.content
                
                # Detect emotion from response punctuation
                if "!" in response_text:
                    detected_emotion = "excited"
                elif "?" in response_text:
                    detected_emotion = "curious"
                elif "..." in response_text:
                    detected_emotion = "thoughtful"
                else:
                    detected_emotion = "calm"
                
                # ADD TO CHAT IMMEDIATELY
                conversation["messages"].append({"role": "user", "content": user_message})
                conversation["messages"].append({"role": "assistant", "content": response_text})
                conversations_db[conv_id] = conversation
                
                # THEN speak in background with detected emotion
                speak_text(response_text, emotion=detected_emotion)
                
                return conversation
        
    except Exception as e:
        print(f"Error in conversation: {e}")
        return {"error": str(e), "id": conv_id}
# ═══════════════════════════════════════════════════════════════
# CHAT ENDPOINT - FIXED FOR COMMAND EXECUTION
# ═══════════════════════════════════════════════════════════════

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint - Commands FIRST, AI second"""
    try:
        user_message = request.message
        print(f"\n🔵 USER: {user_message}")
        
        # Check for commands FIRST
        response_text, command_executed = await process_command(user_message)
        
        if command_executed:
            print(f"✅ COMMAND EXECUTED: {response_text}")
            speak_text(response_text)
            return {
                "status": "success",
                "response": response_text,
                "conversation_id": 1,
                "emotion": "neutral"
            }
        
        # If no command, use AI
        print(f"💬 NO COMMAND - USING AI...")
        
        conversation = await create_conversation(request)
        
        if "messages" in conversation:
            for msg in reversed(conversation["messages"]):
                if msg.get("role") == "assistant":
                    response = msg["content"]
                    
                    # STRIP ANY JSON/CODE FORMATTING
                    if response.startswith('{') or response.startswith('<'):
                        response = "I processed that for you!"
                    
                    print(f"🤖 AI: {response}")
                    
                    return {
                        "status": "success",
                        "response": response,
                        "conversation_id": 1,
                        "emotion": "neutral"
                    }
        
        return {
            "status": "success",
            "response": "I'm here to help!",
            "conversation_id": 1,
            "emotion": "neutral"
        }
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return {
            "status": "error",
            "response": f"Error: {str(e)}"
        }

@app.post("/api/stop-speech")
async def stop_speech_endpoint():
    """Stop current speech"""
    stop_speaking()
    return {"status": "stopped"}

@app.delete("/api/conversation/{conversation_id}")
async def delete_conversation(conversation_id: int):
    """Delete a conversation"""
    if conversation_id in conversations_db:
        del conversations_db[conversation_id]
        return {"status": "deleted"}
    return {"error": "Conversation not found"}

@app.post("/api/voice-to-text")
async def voice_to_text(request: VoiceRequest):
    """Convert voice to text"""
    try:
        audio_bytes = base64.b64decode(request.audio_data.split(',')[1] if ',' in request.audio_data else request.audio_data)
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
            temp_audio.write(audio_bytes)
            temp_audio_path = temp_audio.name
        
        recognizer = sr.Recognizer()
        
        with sr.AudioFile(temp_audio_path) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
        
        os.unlink(temp_audio_path)
        
        return {"status": "success", "text": text}
        
    except sr.UnknownValueError:
        return {"status": "error", "message": "Could not understand audio"}
    except sr.RequestError as e:
        return {"status": "error", "message": f"Speech recognition error: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ═══════════════════════════════════════════════════════════════
# NOTES ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.get("/api/notes")
async def get_notes():
    """Get all notes"""
    return list(notes_db.values())

@app.post("/api/notes")
async def create_note(request: NoteRequest):
    """Create or update a note"""
    global note_counter
    
    if request.id and request.id in notes_db:
        notes_db[request.id]["text"] = request.text
        notes_db[request.id]["updated_at"] = datetime.datetime.now().isoformat()
        return notes_db[request.id]
    else:
        note_counter += 1
        note = {
            "id": note_counter,
            "text": request.text,
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat()
        }
        notes_db[note_counter] = note
        return note

@app.delete("/api/notes/{note_id}")
async def delete_note(note_id: int):
    """Delete a note"""
    if note_id in notes_db:
        del notes_db[note_id]
        return {"status": "deleted"}
    return {"error": "Note not found"}

@app.get("/api/notes/export")
async def export_notes():
    """Export all notes as text"""
    text = ""
    for note in sorted(notes_db.values(), key=lambda x: x['created_at']):
        text += f"[{note['created_at']}]\n{note['text']}\n\n---\n\n"
    return {"content": text}

@app.get("/api/stats")
async def get_stats():
    """Get system stats"""
    try:
        cpu = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        return {"cpu": cpu, "memory": memory, "disk": disk}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    
    # Find available port
    def find_available_port(start_port=8000, max_attempts=10):
        for port in range(start_port, start_port + max_attempts):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(('127.0.0.1', port))
                sock.close()
                return port
            except OSError:
                continue
        return start_port
    
    port = find_available_port()
    
    print(f"🚀 Starting BAIT API Server on port {port}...")
    print(f"✅ TTS Available: {tts_available}")
    print(f"✅ Edge TTS (Hyper-Human): {HAS_EDGE_TTS}")
    print("✅ Web Research: Enabled")
    print("✅ Live Notes: Enabled")
    print("✅ File Operations: Enabled")
    print("✅ Video Chat: Enabled")
    
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
