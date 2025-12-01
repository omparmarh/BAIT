#!/usr/bin/env python3
"""
BAIT PRO ULTIMATE - Voice Control Engine
- Wake word detection ("Hey BAIT")
- Continuous listening mode
- Speech-to-text with multiple providers
- Voice activity detection
- Noise suppression
"""

import os
import sys
import time
import threading
import queue
import wave
import json
from typing import Optional, Callable, Dict, Any
from datetime import datetime
import logging

# Core libraries
import speech_recognition as sr
import pyaudio
import numpy as np
from collections import deque

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# WAKE WORD DETECTOR
# ═══════════════════════════════════════════════════════════════

class WakeWordDetector:
    """
    Detects wake word "Hey BAIT" using keyword spotting
    Falls back to simple pattern matching if porcupine not available
    """
    
    def __init__(self, wake_word: str = "hey bait", sensitivity: float = 0.5):
        self.wake_word = wake_word.lower()
        self.sensitivity = sensitivity
        self.is_listening = False
        self.porcupine = None
        self.use_porcupine = False
        
        # Try to initialize Porcupine (professional wake word detection)
        try:
            import pvporcupine
            # Note: Requires API key from Picovoice
            # For now, we'll use fallback method
            logger.info("Porcupine library found but using fallback detection")
        except ImportError:
            logger.info("Using fallback wake word detection")
    
    def detect_in_text(self, text: str) -> bool:
        """Simple text-based wake word detection"""
        text_lower = text.lower()
        # Check for variations
        wake_words = [
            "hey bait",
            "hey bayt", 
            "hey wait",
            "hey bate",
            "ok bait",
            "okay bait"
        ]
        return any(ww in text_lower for ww in wake_words)
    
    def start_listening(self):
        """Start continuous wake word detection"""
        self.is_listening = True
    
    def stop_listening(self):
        """Stop wake word detection"""
        self.is_listening = False

# ═══════════════════════════════════════════════════════════════
# VOICE ACTIVITY DETECTOR
# ═══════════════════════════════════════════════════════════════

class VoiceActivityDetector:
    """
    Detects when user is speaking vs silence
    Uses energy-based detection
    """
    
    def __init__(self, energy_threshold: int = 300, dynamic_threshold: bool = True):
        self.energy_threshold = energy_threshold
        self.dynamic_threshold = dynamic_threshold
        self.ambient_samples = deque(maxlen=50)
    
    def calculate_energy(self, audio_data: bytes) -> float:
        """Calculate audio energy level"""
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        energy = np.abs(audio_array).mean()
        return energy
    
    def is_speech(self, audio_data: bytes) -> bool:
        """Determine if audio contains speech"""
        energy = self.calculate_energy(audio_data)
        
        # Update ambient noise level
        if self.dynamic_threshold and len(self.ambient_samples) > 0:
            avg_ambient = np.mean(self.ambient_samples)
            threshold = avg_ambient * 1.5
        else:
            threshold = self.energy_threshold
        
        # Add to ambient samples if below threshold
        if energy < threshold * 0.8:
            self.ambient_samples.append(energy)
        
        return energy > threshold

# ═══════════════════════════════════════════════════════════════
# SPEECH TO TEXT ENGINE
# ═══════════════════════════════════════════════════════════════

class SpeechToTextEngine:
    """
    Converts speech to text using multiple providers
    - Google Speech Recognition (free, online)
    - Whisper API (OpenAI, requires API key)
    - Sphinx (offline, lower quality)
    """
    
    def __init__(self, provider: str = "google", api_key: Optional[str] = None):
        self.provider = provider
        self.api_key = api_key
        self.recognizer = sr.Recognizer()
        
        # Configure recognizer
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.phrase_threshold = 0.3
        
        logger.info(f"Speech-to-text initialized with provider: {provider}")
    
    def transcribe(self, audio_data: sr.AudioData, language: str = "en-US") -> Optional[str]:
        """
        Transcribe audio to text
        
        Args:
            audio_data: Audio data from microphone
            language: Language code (default: en-US)
            
        Returns:
            Transcribed text or None if failed
        """
        try:
            if self.provider == "google":
                return self._transcribe_google(audio_data, language)
            elif self.provider == "whisper":
                return self._transcribe_whisper(audio_data)
            elif self.provider == "sphinx":
                return self._transcribe_sphinx(audio_data)
            else:
                logger.error(f"Unknown provider: {self.provider}")
                return None
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None
    
    def _transcribe_google(self, audio_data: sr.AudioData, language: str) -> Optional[str]:
        """Google Speech Recognition (free, requires internet)"""
        try:
            text = self.recognizer.recognize_google(audio_data, language=language)
            logger.info(f"Google transcription: {text}")
            return text
        except sr.UnknownValueError:
            logger.warning("Google could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Google API error: {e}")
            return None
    
    def _transcribe_whisper(self, audio_data: sr.AudioData) -> Optional[str]:
        """OpenAI Whisper API (requires API key)"""
        try:
            if not self.api_key:
                logger.error("Whisper requires OpenAI API key")
                return None
            
            text = self.recognizer.recognize_whisper_api(
                audio_data, 
                api_key=self.api_key
            )
            logger.info(f"Whisper transcription: {text}")
            return text
        except Exception as e:
            logger.error(f"Whisper error: {e}")
            return None
    
    def _transcribe_sphinx(self, audio_data: sr.AudioData) -> Optional[str]:
        """CMU Sphinx (offline, lower quality)"""
        try:
            text = self.recognizer.recognize_sphinx(audio_data)
            logger.info(f"Sphinx transcription: {text}")
            return text
        except Exception as e:
            logger.error(f"Sphinx error: {e}")
            return None

# ═══════════════════════════════════════════════════════════════
# VOICE CONTROL ENGINE (Main Class)
# ═══════════════════════════════════════════════════════════════

class VoiceControlEngine:
    """
    Main voice control system
    - Manages wake word detection
    - Handles continuous listening
    - Processes voice commands
    - Manages audio input/output
    """
    
    def __init__(
        self, 
        wake_word: str = "hey bait",
        stt_provider: str = "google",
        api_key: Optional[str] = None,
        on_command: Optional[Callable[[str], None]] = None
    ):
        """
        Initialize voice control engine
        
        Args:
            wake_word: Wake word to activate (default: "hey bait")
            stt_provider: Speech-to-text provider (google, whisper, sphinx)
            api_key: API key for Whisper if used
            on_command: Callback function when command is detected
        """
        self.wake_word_detector = WakeWordDetector(wake_word)
        self.vad = VoiceActivityDetector()
        self.stt = SpeechToTextEngine(provider=stt_provider, api_key=api_key)
        self.on_command = on_command
        
        # State
        self.is_active = False
        self.is_listening_for_wake_word = False
        self.is_listening_for_command = False
        
        # Audio
        self.microphone = sr.Microphone()
        
        # Threading
        self.wake_word_thread = None
        self.command_queue = queue.Queue()
        
        logger.info("Voice Control Engine initialized")
    
    def start(self):
        """Start the voice control engine"""
        self.is_active = True
        self.start_wake_word_detection()
        logger.info("Voice Control Engine started")
    
    def stop(self):
        """Stop the voice control engine"""
        self.is_active = False
        self.is_listening_for_wake_word = False
        self.is_listening_for_command = False
        logger.info("Voice Control Engine stopped")
    
    def start_wake_word_detection(self):
        """Start continuous wake word detection in background thread"""
        if self.wake_word_thread and self.wake_word_thread.is_alive():
            logger.warning("Wake word detection already running")
            return
        
        self.is_listening_for_wake_word = True
        self.wake_word_thread = threading.Thread(
            target=self._wake_word_loop,
            daemon=True
        )
        self.wake_word_thread.start()
        logger.info("Wake word detection started")
    
    def _wake_word_loop(self):
        """Background loop for wake word detection"""
        with self.microphone as source:
            # Adjust for ambient noise once
            logger.info("Adjusting for ambient noise...")
            self.stt.recognizer.adjust_for_ambient_noise(source, duration=1)
            logger.info("Ready for wake word...")
            
            while self.is_listening_for_wake_word and self.is_active:
                try:
                    # Listen for audio
                    audio = self.stt.recognizer.listen(
                        source, 
                        timeout=1, 
                        phrase_time_limit=3
                    )
                    
                    # Quick transcription to check for wake word
                    text = self.stt.transcribe(audio)
                    
                    if text and self.wake_word_detector.detect_in_text(text):
                        logger.info(f"Wake word detected! Text: {text}")
                        self._on_wake_word_detected()
                    
                except sr.WaitTimeoutError:
                    # No audio detected, continue listening
                    continue
                except Exception as e:
                    logger.error(f"Wake word loop error: {e}")
                    time.sleep(0.1)
    
    def _on_wake_word_detected(self):
        """Called when wake word is detected"""
        logger.info("Listening for command...")
        self.is_listening_for_command = True
        
        # Capture command
        command = self.capture_command()
        
        if command:
            logger.info(f"Command received: {command}")
            # Add to queue
            self.command_queue.put(command)
            # Call callback if provided
            if self.on_command:
                threading.Thread(
                    target=self.on_command,
                    args=(command,),
                    daemon=True
                ).start()
        
        self.is_listening_for_command = False
    
    def capture_command(self, timeout: int = 5) -> Optional[str]:
        """
        Capture voice command after wake word
        
        Args:
            timeout: Maximum time to wait for command
            
        Returns:
            Transcribed command or None
        """
        try:
            with self.microphone as source:
                logger.info("Listening for command...")
                audio = self.stt.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=10
                )
                
                # Transcribe
                text = self.stt.transcribe(audio)
                return text
        
        except sr.WaitTimeoutError:
            logger.warning("Command timeout - no speech detected")
            return None
        except Exception as e:
            logger.error(f"Command capture error: {e}")
            return None
    
    def manual_command_capture(self) -> Optional[str]:
        """Manually trigger command capture (push-to-talk mode)"""
        logger.info("Manual command capture triggered")
        return self.capture_command()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current engine status"""
        return {
            "active": self.is_active,
            "listening_for_wake_word": self.is_listening_for_wake_word,
            "listening_for_command": self.is_listening_for_command,
            "provider": self.stt.provider,
            "wake_word": self.wake_word_detector.wake_word
        }

# ═══════════════════════════════════════════════════════════════
# TESTING & STANDALONE MODE
# ═══════════════════════════════════════════════════════════════

def test_callback(command: str):
    """Test callback for demonstration"""
    print(f"\n🎤 COMMAND RECEIVED: {command}\n")

def main():
    """Standalone testing mode"""
    print("=" * 60)
    print("BAIT Voice Control Engine - Test Mode")
    print("=" * 60)
    print("Say 'Hey BAIT' followed by your command")
    print("Press Ctrl+C to exit")
    print("=" * 60)
    
    # Initialize engine
    engine = VoiceControlEngine(
        wake_word="hey bait",
        stt_provider="google",
        on_command=test_callback
    )
    
    # Start
    engine.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping...")
        engine.stop()
        print("Goodbye!")

if __name__ == "__main__":
    main()
