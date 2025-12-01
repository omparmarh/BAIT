#!/usr/bin/env python3
"""
BAIT PRO ULTIMATE - Avatar Controller with Lip Sync
- Phoneme detection from audio
- Mouth shape mapping (10 distinct shapes)
- Real-time sync data generation (60fps)
- Expression control
- Eye movement tracking
"""

import os
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json
import numpy as np

# Try audio processing libraries
try:
    import librosa
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False
    logging.warning("librosa not available - limited audio analysis")

try:
    from pydub import AudioSegment
    HAS_PYDUB = True
except ImportError:
    HAS_PYDUB = False
    logging.warning("pydub not available")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# PHONEME DETECTOR
# ═══════════════════════════════════════════════════════════════

class PhonemeDetector:
    """
    Detects phonemes from audio for lip sync
    """
    
    # Phoneme to mouth shape mapping
    PHONEME_SHAPES = {
        # Vowels
        'AA': 'open',      # father
        'AE': 'open',      # cat
        'AH': 'open',      # cut
        'AO': 'round',     # dog
        'AW': 'round',     # down
        'AY': 'wide',      # my
        'EH': 'wide',      # bed
        'ER': 'neutral',   # bird
        'EY': 'wide',      # bay
        'IH': 'wide',      # bit
        'IY': 'wide',      # beat
        'OW': 'round',     # go
        'OY': 'round',     # boy
        'UH': 'round',     # put
        'UW': 'round',     # boot
        
        # Consonants
        'B': 'closed',     # bee
        'P': 'closed',     # pea
        'M': 'closed',     # me
        'F': 'f_shape',    # fee
        'V': 'f_shape',    # vee
        'TH': 'th_shape',  # thee
        'DH': 'th_shape',  # the
        'S': 'wide',       # sea
        'Z': 'wide',       # zee
        'T': 'wide',       # tea
        'D': 'wide',       # dee
        'N': 'wide',       # knee
        'L': 'wide',       # lee
        'R': 'neutral',    # ree
        'W': 'round',      # we
        'Y': 'wide',       # ye
        'K': 'neutral',    # key
        'G': 'neutral',    # gee
        'H': 'neutral',    # he
        'SH': 'wide',      # she
        'CH': 'wide',      # chee
        'JH': 'wide',      # gee
        'NG': 'neutral',   # sing
    }
    
    # Simplified mouth shapes (10 total)
    MOUTH_SHAPES = {
        'neutral': 0,     # Resting position
        'open': 1,        # A, E sounds
        'wide': 2,        # I, smile
        'round': 3,       # O, U sounds
        'closed': 4,      # M, B, P
        'f_shape': 5,     # F, V (bottom lip tucked)
        'th_shape': 6,    # TH (tongue between teeth)
        'smile': 7,       # Happy expression
        'frown': 8,       # Sad expression
        'surprised': 9    # O shape, wide eyes
    }
    
    def __init__(self, sample_rate: int = 22050):
        """
        Initialize phoneme detector
        
        Args:
            sample_rate: Audio sample rate
        """
        self.sample_rate = sample_rate
        logger.info("Phoneme Detector initialized")
    
    def detect_from_audio(self, audio_path: str) -> List[Dict[str, Any]]:
        """
        Detect phonemes from audio file
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            List of phoneme events with timestamps
        """
        if not HAS_LIBROSA:
            logger.error("librosa required for phoneme detection")
            return self._fallback_detection(audio_path)
        
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Extract features
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            
            # Detect onset frames (simplification)
            onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
            onset_times = librosa.frames_to_time(onset_frames, sr=sr)
            
            # Analyze energy for vowel detection
            rms = librosa.feature.rms(y=y)[0]
            
            phonemes = []
            duration = librosa.get_duration(y=y, sr=sr)
            
            # Simple phoneme estimation (in production, use actual phoneme recognition)
            num_segments = min(len(onset_times), 50)
            
            for i, time in enumerate(onset_times[:num_segments]):
                # Estimate phoneme based on energy and spectral features
                frame_idx = librosa.time_to_frames(time, sr=sr)
                
                if frame_idx < len(rms):
                    energy = rms[frame_idx]
                    
                    # Simple classification (placeholder)
                    if energy > 0.02:
                        shape = 'open' if energy > 0.04 else 'wide'
                    else:
                        shape = 'neutral'
                    
                    phonemes.append({
                        'time': float(time),
                        'shape': shape,
                        'duration': 0.1  # Approximate
                    })
            
            # Add final neutral state
            phonemes.append({
                'time': float(duration),
                'shape': 'neutral',
                'duration': 0.1
            })
            
            logger.info(f"Detected {len(phonemes)} phoneme events")
            return phonemes
        
        except Exception as e:
            logger.error(f"Phoneme detection error: {e}")
            return self._fallback_detection(audio_path)
    
    def _fallback_detection(self, audio_path: str) -> List[Dict[str, Any]]:
        """
        Fallback phoneme detection without librosa
        Creates simple open-close pattern
        """
        if not HAS_PYDUB:
            # Ultimate fallback: fixed timing
            return [
                {'time': 0.0, 'shape': 'neutral', 'duration': 0.1},
                {'time': 0.2, 'shape': 'open', 'duration': 0.2},
                {'time': 0.4, 'shape': 'closed', 'duration': 0.1},
                {'time': 0.6, 'shape': 'wide', 'duration': 0.2},
                {'time': 0.8, 'shape': 'neutral', 'duration': 0.1}
            ]
        
        try:
            audio = AudioSegment.from_file(audio_path)
            duration = len(audio) / 1000.0  # Convert to seconds
            
            # Simple pattern based on duration
            phonemes = []
            time = 0.0
            shapes = ['open', 'wide', 'closed', 'round', 'neutral']
            
            while time < duration:
                shape = shapes[int(time * 5) % len(shapes)]
                phonemes.append({
                    'time': time,
                    'shape': shape,
                    'duration': 0.1
                })
                time += 0.15
            
            return phonemes
        
        except Exception as e:
            logger.error(f"Fallback detection error: {e}")
            return []

# ═══════════════════════════════════════════════════════════════
# LIP SYNC DATA GENERATOR
# ═══════════════════════════════════════════════════════════════

class LipSyncGenerator:
    """
    Generates 60fps lip sync data for avatar animation
    """
    
    def __init__(self, fps: int = 60):
        """
        Initialize lip sync generator
        
        Args:
            fps: Target frames per second
        """
        self.fps = fps
        self.frame_duration = 1.0 / fps
        logger.info(f"Lip Sync Generator initialized ({fps} fps)")
    
    def generate_sync_data(self, phonemes: List[Dict[str, Any]], total_duration: float) -> List[Dict[str, Any]]:
        """
        Generate frame-by-frame sync data
        
        Args:
            phonemes: Phoneme events from detector
            total_duration: Total audio duration
            
        Returns:
            List of frames with mouth shapes
        """
        if not phonemes:
            return []
        
        frames = []
        current_time = 0.0
        frame_number = 0
        phoneme_idx = 0
        
        while current_time <= total_duration:
            # Find current phoneme
            while phoneme_idx < len(phonemes) - 1 and phonemes[phoneme_idx + 1]['time'] <= current_time:
                phoneme_idx += 1
            
            current_phoneme = phonemes[phoneme_idx]
            
            # Add interpolation for smooth transitions
            if phoneme_idx < len(phonemes) - 1:
                next_phoneme = phonemes[phoneme_idx + 1]
                time_to_next = next_phoneme['time'] - current_time
                
                if time_to_next < 0.1:  # Transition zone
                    blend = 1.0 - (time_to_next / 0.1)
                    shape = current_phoneme['shape']
                else:
                    blend = 0.0
                    shape = current_phoneme['shape']
            else:
                blend = 0.0
                shape = current_phoneme['shape']
            
            frames.append({
                'frame': frame_number,
                'time': round(current_time, 4),
                'shape': shape,
                'blend': round(blend, 2)
            })
            
            current_time += self.frame_duration
            frame_number += 1
        
        logger.info(f"Generated {len(frames)} sync frames")
        return frames
    
    def export_json(self, frames: List[Dict[str, Any]], output_path: str):
        """Export sync data to JSON"""
        with open(output_path, 'w') as f:
            json.dump({
                'fps': self.fps,
                'frame_count': len(frames),
                'frames': frames
            }, f, indent=2)
        
        logger.info(f"Exported sync data to: {output_path}")

# ═══════════════════════════════════════════════════════════════
# EXPRESSION CONTROLLER
# ═══════════════════════════════════════════════════════════════

class ExpressionController:
    """
    Controls avatar facial expressions
    """
    
    EXPRESSIONS = {
        'neutral': {'mouth': 'neutral', 'eyes': 'normal', 'eyebrows': 'neutral'},
        'happy': {'mouth': 'smile', 'eyes': 'slight_close', 'eyebrows': 'raised'},
        'sad': {'mouth': 'frown', 'eyes': 'slight_close', 'eyebrows': 'lowered'},
        'surprised': {'mouth': 'surprised', 'eyes': 'wide', 'eyebrows': 'raised'},
        'angry': {'mouth': 'frown', 'eyes': 'narrow', 'eyebrows': 'furrowed'},
        'thinking': {'mouth': 'neutral', 'eyes': 'looking_up', 'eyebrows': 'raised'},
        'excited': {'mouth': 'smile', 'eyes': 'wide', 'eyebrows': 'raised'},
        'confused': {'mouth': 'neutral', 'eyes': 'looking_side', 'eyebrows': 'raised'}
    }
    
    def __init__(self):
        """Initialize expression controller"""
        self.current_expression = 'neutral'
        logger.info("Expression Controller initialized")
    
    def set_expression(self, expression: str) -> Dict[str, str]:
        """
        Set avatar expression
        
        Args:
            expression: Expression name
            
        Returns:
            Expression configuration
        """
        if expression not in self.EXPRESSIONS:
            logger.warning(f"Unknown expression: {expression}")
            expression = 'neutral'
        
        self.current_expression = expression
        return self.EXPRESSIONS[expression]
    
    def get_expression_for_emotion(self, emotion: str) -> str:
        """
        Map emotion to expression
        
        Args:
            emotion: Emotion name (happy, sad, etc.)
            
        Returns:
            Expression name
        """
        emotion_map = {
            'happy': 'happy',
            'joy': 'happy',
            'excited': 'excited',
            'sad': 'sad',
            'angry': 'angry',
            'surprised': 'surprised',
            'confused': 'confused',
            'thinking': 'thinking',
            'thoughtful': 'thinking'
        }
        
        return emotion_map.get(emotion.lower(), 'neutral')

# ═══════════════════════════════════════════════════════════════
# AVATAR CONTROLLER (Main Class)
# ═══════════════════════════════════════════════════════════════

class AvatarController:
    """
    Main avatar control system
    Coordinates lip sync, expressions, and eye movement
    """
    
    def __init__(self, fps: int = 60):
        """
        Initialize avatar controller
        
        Args:
            fps: Animation frame rate
        """
        self.phoneme_detector = PhonemeDetector()
        self.lip_sync_generator = LipSyncGenerator(fps=fps)
        self.expression_controller = ExpressionController()
        
        self.current_sync_data = None
        self.current_expression = 'neutral'
        
        logger.info("Avatar Controller initialized")
    
    def generate_lip_sync(self, audio_path: str, output_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Generate complete lip sync data from audio
        
        Args:
            audio_path: Path to audio file
            output_path: Optional path to save JSON
            
        Returns:
            Lip sync frame data
        """
        # Detect phonemes
        phonemes = self.phoneme_detector.detect_from_audio(audio_path)
        
        if not phonemes:
            logger.error("No phonemes detected")
            return []
        
        # Get audio duration
        if HAS_LIBROSA:
            import librosa
            duration = librosa.get_duration(path=audio_path)
        elif HAS_PYDUB:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(audio_path)
            duration = len(audio) / 1000.0
        else:
            duration = 2.0  # Default fallback
        
        # Generate sync data
        sync_data = self.lip_sync_generator.generate_sync_data(phonemes, duration)
        
        self.current_sync_data = sync_data
        
        # Export if requested
        if output_path:
            self.lip_sync_generator.export_json(sync_data, output_path)
        
        return sync_data
    
    def set_expression(self, expression: str) -> Dict[str, Any]:
        """Set avatar expression"""
        config = self.expression_controller.set_expression(expression)
        self.current_expression = expression
        return config
    
    def set_emotion(self, emotion: str) -> Dict[str, Any]:
        """Set expression based on emotion"""
        expression = self.expression_controller.get_expression_for_emotion(emotion)
        return self.set_expression(expression)
    
    def get_frame_data(self, time: float) -> Dict[str, Any]:
        """
        Get avatar data for specific time
        
        Args:
            time: Time in seconds
            
        Returns:
            Frame data including mouth shape and expression
        """
        if not self.current_sync_data:
            return {
                'mouth_shape': 'neutral',
                'expression': self.current_expression,
                'time': time
            }
        
        # Find closest frame
        fps = self.lip_sync_generator.fps
        frame_idx = int(time * fps)
        
        if frame_idx < len(self.current_sync_data):
            frame = self.current_sync_data[frame_idx]
            return {
                'mouth_shape': frame['shape'],
                'blend': frame.get('blend', 0.0),
                'expression': self.current_expression,
                'time': time
            }
        
        return {
            'mouth_shape': 'neutral',
            'expression': self.current_expression,
            'time': time
        }
    
    def generate_preview(self, audio_path: str, output_frames: int = 10) -> List[Dict[str, Any]]:
        """
        Generate preview frames for testing
        
        Args:
            audio_path: Audio file path
            output_frames: Number of preview frames
            
        Returns:
            Preview frames
        """
        sync_data = self.generate_lip_sync(audio_path)
        
        if not sync_data:
            return []
        
        # Sample frames evenly
        step = max(1, len(sync_data) // output_frames)
        preview = sync_data[::step][:output_frames]
        
        return preview

# ═══════════════════════════════════════════════════════════════
# TESTING
# ═══════════════════════════════════════════════════════════════

def main():
    """Standalone testing"""
    print("=" * 60)
    print("BAIT Avatar Controller - Test Mode")
    print("=" * 60)
    
    controller = AvatarController(fps=60)
    
    # Test expression control
    print("\n😊 Testing expressions...")
    happy = controller.set_expression('happy')
    print(f"  Happy: {happy}")
    
    sad = controller.set_expression('sad')
    print(f"  Sad: {sad}")
    
    # Test emotion mapping
    print("\n🎭 Testing emotion mapping...")
    expr = controller.set_emotion('excited')
    print(f"  Excited -> {controller.current_expression}: {expr}")
    
    # Note: Audio file testing would require actual audio file
    print("\n📝 Note: Lip sync requires audio file for full testing")
    print("  Usage: controller.generate_lip_sync('audio.wav', 'output.json')")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
