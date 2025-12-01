import librosa
import numpy as np
from scipy import signal
import json

class LipSyncAnalyzer:
    """Analyzes audio frequency to generate lip-sync data"""
    
    def __init__(self, sr=16000):
        self.sr = sr
        # Frequency ranges for different phonemes
        self.phoneme_ranges = {
            'A': (500, 1000),    # Open mouth
            'E': (1500, 2500),   # Mid-open
            'I': (2500, 4000),   # Tight
            'O': (800, 1200),    # Rounded
            'U': (600, 900),     # Very rounded
            'M': (200, 500),     # Closed
            'Rest': (0, 200),    # Silent
        }
    
    def analyze_audio(self, audio_path):
        """Extract lip-sync keyframes from audio"""
        try:
            y, sr = librosa.load(audio_path, sr=self.sr)
            
            # Compute MFCC (Mel-frequency cepstral coefficients)
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            
            # Compute energy in frequency bands
            D = librosa.stft(y)
            magnitude = np.abs(D)
            
            # Extract features every 10ms
            hop_length = 160  # ~10ms at 16kHz
            frames = []
            
            for i in range(0, len(y) - hop_length, hop_length):
                frame = y[i:i + hop_length]
                
                # Compute frequency content
                fft = np.fft.fft(frame)
                freqs = np.fft.fftfreq(len(frame), 1/sr)
                
                # Detect dominant phoneme
                phoneme = self._detect_phoneme(freqs, np.abs(fft))
                
                # Get mouth openness (0-1)
                energy = np.sqrt(np.mean(frame**2))
                mouth_open = min(1.0, energy / 0.1)
                
                frames.append({
                    'time': i / sr,
                    'phoneme': phoneme,
                    'mouth_open': mouth_open,
                    'energy': energy
                })
            
            return frames
        except Exception as e:
            print(f"Lip-sync error: {e}")
            return []
    
    def _detect_phoneme(self, freqs, magnitude):
        """Detect phoneme from frequency spectrum"""
        positive_freqs = freqs[:len(freqs)//2]
        positive_mag = magnitude[:len(magnitude)//2]
        
        scores = {}
        for phoneme, (freq_low, freq_high) in self.phoneme_ranges.items():
            mask = (positive_freqs >= freq_low) & (positive_freqs <= freq_high)
            scores[phoneme] = np.sum(positive_mag[mask])
        
        return max(scores, key=scores.get)

# Export for use
lip_sync = LipSyncAnalyzer()
