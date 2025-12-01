import asyncio
import edge_tts
import os
from pathlib import Path
import tempfile
import threading

class HyperHumanTTS:
    """
    HYPER-HUMAN TTS using Microsoft Edge voices
    Supports multiple voices and emotions
    """
    
    # Best natural voices (female has more warmth)
    VOICES = {
        "female_natural": "en-US-AriaNeural",      # Warm, friendly
        "female_energetic": "en-US-AvaNeural",     # Energetic, engaging
        "male_natural": "en-US-GuyNeural",         # Professional yet warm
        "male_friendly": "en-US-EricNeural",       # Friendly, casual
    }
    
    # Rate settings (-50 to 50) - negative = slower (more natural)
    SPEAKING_RATES = {
        "slow": "-30%",      # Very natural, conversational
        "normal": "-10%",    # Natural pace
        "fast": "10%",       # Energetic
    }
    
    def __init__(self):
        self.current_task = None
        self.should_stop = False
        self.voice = self.VOICES["female_natural"]
        self.rate = self.SPEAKING_RATES["normal"]
        
    async def speak(self, text, voice="female_natural", rate="normal", emotion=None):
        """
        Speak with hyper-human naturalness
        
        Args:
            text: What to say
            voice: Which voice to use
            rate: Speaking speed
            emotion: "happy", "sad", "excited", "calm" (affects pitch/rate)
        """
        # Stop previous speech
        self.should_stop = True
        if self.current_task:
            self.current_task.cancel()
        
        self.should_stop = False
        
        # Select voice
        selected_voice = self.VOICES.get(voice, self.VOICES["female_natural"])
        selected_rate = self.SPEAKING_RATES.get(rate, self.SPEAKING_RATES["normal"])
        
        # Apply emotion modifiers
        if emotion == "excited":
            selected_rate = self.SPEAKING_RATES["normal"]
        elif emotion == "calm":
            selected_rate = self.SPEAKING_RATES["slow"]
        elif emotion == "sad":
            selected_rate = "-40%"
        
        try:
            # Create SSML for more natural prosody
            ssml = self._create_ssml(text, selected_voice, selected_rate, emotion)
            
            # Stream audio directly (no file saving)
            communicate = edge_tts.Communicate(text, selected_voice, rate=selected_rate)
            
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                async for chunk in communicate.stream():
                    if self.should_stop:
                        break
                    if chunk["type"] == "audio":
                        f.write(chunk["data"])
                
                if not self.should_stop:
                    temp_file = f.name
                    # Play the audio
                    self._play_audio(temp_file)
                    # Clean up
                    try:
                        os.unlink(temp_file)
                    except:
                        pass
                        
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"TTS Error: {e}")
    
    def _create_ssml(self, text, voice, rate, emotion):
        """Create SSML for advanced prosody"""
        pitch = "+10%"
        if emotion == "calm":
            pitch = "-5%"
        elif emotion == "sad":
            pitch = "-15%"
        elif emotion == "excited":
            pitch = "+20%"
        
        ssml = f"""
        <speak>
            <voice name="{voice}">
                <prosody pitch="{pitch}" rate="{rate}">
                    {text}
                </prosody>
            </voice>
        </speak>
        """
        return ssml
    
    def _play_audio(self, filepath):
        """Play audio file"""
        try:
            import subprocess
            import sys
            if sys.platform == 'win32':
                os.startfile(filepath)
            else:
                subprocess.Popen(['afplay', filepath])
        except:
            pass
    
    def stop(self):
        """Stop current speech"""
        self.should_stop = True

# Global TTS instance
tts_manager = HyperHumanTTS()
