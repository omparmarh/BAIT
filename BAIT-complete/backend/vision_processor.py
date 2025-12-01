#!/usr/bin/env python3
"""
BAIT PRO ULTIMATE - Vision Processor
- Screenshot capture and analysis
- OCR text extraction
- GPT-4 Vision integration
- Camera face/gesture recognition
- Emotion detection
- Screen context awareness
"""

import os
import sys
import base64
import logging
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from io import BytesIO

# Image processing
import cv2
import numpy as np
from PIL import Image, ImageGrab
import pytesseract

# Try to import optional dependencies
try:
    import face_recognition
    HAS_FACE_RECOGNITION = True
except ImportError:
    HAS_FACE_RECOGNITION = False
    logging.warning("face_recognition not available")

try:
    import mediapipe as mp
    HAS_MEDIAPIPE = True
except ImportError:
    HAS_MEDIAPIPE = False
    logging.warning("mediapipe not available")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# SCREEN CAPTURE & ANALYSIS
# ═══════════════════════════════════════════════════════════════

class ScreenAnalyzer:
    """
    Captures and analyzes screen content
    - Screenshots
    - OCR text extraction
    - Error detection
    - Code analysis
    - UI element detection
    """
    
    def __init__(self, tesseract_cmd: Optional[str] = None):
        """
        Initialize screen analyzer
        
        Args:
            tesseract_cmd: Path to tesseract executable (if not in PATH)
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        
        logger.info("Screen Analyzer initialized")
    
    def capture_screenshot(self, save_path: Optional[str] = None) -> Image.Image:
        """
        Capture screenshot of entire screen
        
        Args:
            save_path: Optional path to save screenshot
            
        Returns:
            PIL Image object
        """
        try:
            screenshot = ImageGrab.grab()
            
            if save_path:
                screenshot.save(save_path)
                logger.info(f"Screenshot saved to: {save_path}")
            
            return screenshot
        except Exception as e:
            logger.error(f"Screenshot capture error: {e}")
            return None
    
    def capture_window(self, window_title: str) -> Optional[Image.Image]:
        """
        Capture screenshot of specific window
        
        Args:
            window_title: Title of window to capture
            
        Returns:
            PIL Image or None
        """
        try:
            # This requires platform-specific implementation
            # For now, capture full screen
            return self.capture_screenshot()
        except Exception as e:
            logger.error(f"Window capture error: {e}")
            return None
    
    def extract_text(self, image: Image.Image, lang: str = 'eng') -> str:
        """
        Extract text from image using OCR
        
        Args:
            image: PIL Image object
            lang: Language code (default: eng)
            
        Returns:
            Extracted text
        """
        try:
            text = pytesseract.image_to_string(image, lang=lang)
            logger.info(f"Extracted {len(text)} characters from image")
            return text.strip()
        except Exception as e:
            logger.error(f"OCR error: {e}")
            return ""
    
    def detect_errors(self, image: Image.Image) -> List[Dict[str, Any]]:
        """
        Detect error messages in screenshot
        
        Args:
            image: PIL Image object
            
        Returns:
            List of detected errors with locations
        """
        try:
            # Extract text with bounding boxes
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            errors = []
            error_keywords = [
                'error', 'exception', 'failed', 'fatal', 'warning',
                'traceback', 'errno', 'crash', 'bug', 'invalid'
            ]
            
            for i, text in enumerate(data['text']):
                text_lower = text.lower()
                if any(keyword in text_lower for keyword in error_keywords):
                    errors.append({
                        'text': text,
                        'confidence': data['conf'][i],
                        'left': data['left'][i],
                        'top': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i]
                    })
            
            logger.info(f"Detected {len(errors)} potential errors")
            return errors
        except Exception as e:
            logger.error(f"Error detection failed: {e}")
            return []
    
    def analyze_code(self, image: Image.Image) -> Dict[str, Any]:
        """
        Analyze code in screenshot
        
        Args:
            image: PIL Image object
            
        Returns:
            Code analysis results
        """
        try:
            text = self.extract_text(image)
            
            # Detect programming language
            language_indicators = {
                'python': ['def ', 'import ', 'class ', 'if __name__'],  
                'javascript': ['function ', 'const ', 'let ', 'var '],
                'java': ['public class', 'private ', 'void '],
                'c++': ['#include', 'using namespace', 'int main'],
                'html': ['<html>', '<div>', '<body>'],
                'css': ['{', '}', ':', ';']
            }
            
            detected_language = 'unknown'
            for lang, indicators in language_indicators.items():
                if any(ind in text for ind in indicators):
                    detected_language = lang
                    break
            
            # Count lines
            lines = [l for l in text.split('\n') if l.strip()]
            
            return {
                'language': detected_language,
                'line_count': len(lines),
                'has_errors': 'error' in text.lower() or 'exception' in text.lower(),
                'text': text
            }
        except Exception as e:
            logger.error(f"Code analysis error: {e}")
            return {'language': 'unknown', 'error': str(e)}
    
    def image_to_base64(self, image: Image.Image) -> str:
        """
        Convert PIL Image to base64 string for API transmission
        
        Args:
            image: PIL Image object
            
        Returns:
            Base64 encoded string
        """
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str

# ═══════════════════════════════════════════════════════════════
# CAMERA & FACE RECOGNITION
# ═══════════════════════════════════════════════════════════════

class CameraProcessor:
    """
    Processes camera input
    - Face detection and recognition
    - Gesture recognition
    - Emotion detection
    - Presence detection
    """
    
    def __init__(self, camera_index: int = 0):
        """
        Initialize camera processor
        
        Args:
            camera_index: Camera device index (default: 0)
        """
        self.camera_index = camera_index
        self.camera = None
        self.known_faces = {}  # name -> face_encoding
        
        # Initialize MediaPipe if available
        if HAS_MEDIAPIPE:
            self.mp_hands = mp.solutions.hands
            self.mp_face_mesh = mp.solutions.face_mesh
            self.hands_detector = self.mp_hands.Hands(
                min_detection_confidence=0.7,
                min_tracking_confidence=0.5
            )
        
        logger.info(f"Camera Processor initialized (index: {camera_index})")
    
    def start_camera(self) -> bool:
        """
        Start camera capture
        
        Returns:
            True if successful
        """
        try:
            self.camera = cv2.VideoCapture(self.camera_index)
            if not self.camera.isOpened():
                logger.error("Failed to open camera")
                return False
            logger.info("Camera started")
            return True
        except Exception as e:
            logger.error(f"Camera start error: {e}")
            return False
    
    def stop_camera(self):
        """Stop camera capture"""
        if self.camera:
            self.camera.release()
            self.camera = None
            logger.info("Camera stopped")
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture single frame from camera
        
        Returns:
            numpy array (BGR image) or None
        """
        if not self.camera:
            logger.warning("Camera not started")
            return None
        
        ret, frame = self.camera.read()
        if not ret:
            logger.error("Failed to capture frame")
            return None
        
        return frame
    
    def detect_faces(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect faces in frame
        
        Args:
            frame: numpy array (BGR image)
            
        Returns:
            List of face locations and encodings
        """
        if not HAS_FACE_RECOGNITION:
            logger.warning("face_recognition library not available")
            return []
        
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            
            faces = []
            for location, encoding in zip(face_locations, face_encodings):
                top, right, bottom, left = location
                faces.append({
                    'location': {'top': top, 'right': right, 'bottom': bottom, 'left': left},
                    'encoding': encoding,
                    'recognized': self._recognize_face(encoding)
                })
            
            return faces
        except Exception as e:
            logger.error(f"Face detection error: {e}")
            return []
    
    def _recognize_face(self, face_encoding: np.ndarray) -> Optional[str]:
        """
        Recognize face from known faces
        
        Args:
            face_encoding: Face encoding to match
            
        Returns:
            Name of recognized person or None
        """
        if not self.known_faces:
            return None
        
        for name, known_encoding in self.known_faces.items():
            matches = face_recognition.compare_faces([known_encoding], face_encoding)
            if matches[0]:
                return name
        
        return None
    
    def register_face(self, name: str, frame: np.ndarray) -> bool:
        """
        Register a new face
        
        Args:
            name: Name of person
            frame: Image frame containing face
            
        Returns:
            True if successful
        """
        if not HAS_FACE_RECOGNITION:
            return False
        
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_encodings = face_recognition.face_encodings(rgb_frame)
            
            if not face_encodings:
                logger.error("No face found in frame")
                return False
            
            self.known_faces[name] = face_encodings[0]
            logger.info(f"Registered face for: {name}")
            return True
        except Exception as e:
            logger.error(f"Face registration error: {e}")
            return False
    
    def detect_gestures(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect hand gestures
        
        Args:
            frame: numpy array (BGR image)
            
        Returns:
            List of detected gestures
        """
        if not HAS_MEDIAPIPE:
            logger.warning("MediaPipe not available")
            return []
        
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect hands
            results = self.hands_detector.process(rgb_frame)
            
            gestures = []
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    gesture = self._classify_gesture(hand_landmarks)
                    gestures.append(gesture)
            
            return gestures
        except Exception as e:
            logger.error(f"Gesture detection error: {e}")
            return []
    
    def _classify_gesture(self, hand_landmarks) -> Dict[str, Any]:
        """
        Classify hand gesture from landmarks
        
        Args:
            hand_landmarks: MediaPipe hand landmarks
            
        Returns:
            Gesture classification
        """
        # Simple gesture classification based on finger positions
        # This is a simplified version - full implementation would be more complex
        
        landmarks = hand_landmarks.landmark
        
        # Get finger tip and base positions
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]
        
        # Simple gesture detection
        fingers_up = []
        
        # Thumb (different logic)
        if thumb_tip.x < landmarks[3].x:
            fingers_up.append(True)
        else:
            fingers_up.append(False)
        
        # Other fingers
        finger_tips = [index_tip, middle_tip, ring_tip, pinky_tip]
        finger_bases = [landmarks[6], landmarks[10], landmarks[14], landmarks[18]]
        
        for tip, base in zip(finger_tips, finger_bases):
            if tip.y < base.y:
                fingers_up.append(True)
            else:
                fingers_up.append(False)
        
        # Classify gesture
        fingers_count = sum(fingers_up)
        
        if fingers_count == 0:
            gesture_name = "fist"
        elif fingers_count == 1 and fingers_up[1]:  # Index finger
            gesture_name = "point"
        elif fingers_count == 2 and fingers_up[1] and fingers_up[2]:  # Peace sign
            gesture_name = "peace"
        elif fingers_count == 5:
            gesture_name = "open_hand"
        elif fingers_count == 1 and fingers_up[0]:  # Thumb
            gesture_name = "thumbs_up"
        else:
            gesture_name = "unknown"
        
        return {
            'gesture': gesture_name,
            'fingers_up': fingers_count,
            'confidence': 0.8  # Simplified
        }
    
    def detect_emotion(self, frame: np.ndarray) -> Optional[str]:
        """
        Detect emotion from facial expression
        
        Args:
            frame: numpy array (BGR image)
            
        Returns:
            Detected emotion or None
        """
        # This would require DeepFace or similar library
        # Placeholder implementation
        logger.info("Emotion detection not fully implemented")
        return None

# ═══════════════════════════════════════════════════════════════
# VISION PROCESSOR (Main Class)
# ═══════════════════════════════════════════════════════════════

class VisionProcessor:
    """
    Main vision processing system
    Combines screen and camera analysis
    """
    
    def __init__(self, tesseract_cmd: Optional[str] = None, camera_index: int = 0):
        """
        Initialize vision processor
        
        Args:
            tesseract_cmd: Path to tesseract executable
            camera_index: Camera device index
        """
        self.screen_analyzer = ScreenAnalyzer(tesseract_cmd)
        self.camera_processor = CameraProcessor(camera_index)
        
        logger.info("Vision Processor initialized")
    
    def analyze_screen_context(self) -> Dict[str, Any]:
        """
        Analyze current screen context
        
        Returns:
            Comprehensive screen analysis
        """
        screenshot = self.screen_analyzer.capture_screenshot()
        
        if not screenshot:
            return {'error': 'Failed to capture screenshot'}
        
        # Extract text
        text = self.screen_analyzer.extract_text(screenshot)
        
        # Detect errors
        errors = self.screen_analyzer.detect_errors(screenshot)
        
        # Analyze if code is visible
        code_analysis = self.screen_analyzer.analyze_code(screenshot)
        
        return {
            'text': text[:500] + '...' if len(text) > 500 else text,  # Truncate
            'text_length': len(text),
            'errors_detected': len(errors),
            'errors': errors[:5],  # First 5 errors
            'code_detected': code_analysis['language'] != 'unknown',
            'code_language': code_analysis.get('language'),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_screen_summary(self) -> str:
        """
        Get human-readable screen summary
        
        Returns:
            Text summary of screen content
        """
        analysis = self.analyze_screen_context()
        
        summary_parts = []
        
        if analysis.get('code_detected'):
            summary_parts.append(f"You have {analysis['code_language']} code visible on screen")
        
        if analysis.get('errors_detected', 0) > 0:
            summary_parts.append(f"I detected {analysis['errors_detected']} error(s)")
        
        if analysis.get('text_length', 0) > 100:
            summary_parts.append(f"Screen contains approximately {analysis['text_length']} characters of text")
        
        if not summary_parts:
            summary_parts.append("Screen analysis completed")
        
        return ". ".join(summary_parts)
    
    def check_presence(self) -> bool:
        """
        Check if user is present via camera
        
        Returns:
            True if user detected
        """
        if not self.camera_processor.start_camera():
            return False
        
        frame = self.camera_processor.capture_frame()
        if frame is None:
            return False
        
        faces = self.camera_processor.detect_faces(frame)
        self.camera_processor.stop_camera()
        
        return len(faces) > 0

# ═══════════════════════════════════════════════════════════════
# TESTING
# ═══════════════════════════════════════════════════════════════

def main():
    """Standalone testing"""
    print("=" * 60)
    print("BAIT Vision Processor - Test Mode")
    print("=" * 60)
    
    processor = VisionProcessor()
    
    # Test screen analysis
    print("\n📸 Capturing and analyzing screen...")
    context = processor.analyze_screen_context()
    print(f"  Text length: {context['text_length']}")
    print(f"  Errors detected: {context['errors_detected']}")
    print(f"  Code detected: {context['code_detected']}")
    
    if context['code_detected']:
        print(f"  Language: {context['code_language']}")
    
    print(f"\n📝 Summary: {processor.get_screen_summary()}")
    
    # Test camera (if available)
    print("\n📷 Testing camera...")
    if processor.camera_processor.start_camera():
        frame = processor.camera_processor.capture_frame()
        if frame is not None:
            faces = processor.camera_processor.detect_faces(frame)
            print(f"  Faces detected: {len(faces)}")
            
            gestures = processor.camera_processor.detect_gestures(frame)
            print(f"  Gestures detected: {len(gestures)}")
            for gesture in gestures:
                print(f"    - {gesture['gesture']}")
        
        processor.camera_processor.stop_camera()
    else:
        print("  Camera not available")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
