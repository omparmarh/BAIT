#!/usr/bin/env python3
"""
BAIT PRO ULTIMATE - Desktop Controller
- Window management
- Mouse and keyboard control  
- Macro recording and playback
- UI automation
"""

import os
import logging
from typing import Dict, Any, List, Optional, Tuple
import time
import json

# Try desktop control libraries
try:
    import pyautogui
    pyautogui.FAILSAFE = True  # Move mouse to corner to abort
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False
    logging.warning("pyautogui not available")

try:
    import pygetwindow as gw
    HAS_PYGETWINDOW = True
except ImportError:
    HAS_PYGETWINDOW = False
    logging.warning("pygetwindow not available")

try:
    from pynput import keyboard, mouse
    from pynput.keyboard import Controller as KeyboardController
    from pynput.mouse import Controller as MouseController
    HAS_PYNPUT = True
except ImportError:
    HAS_PYNPUT = False
    logging.warning("pynput not available")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# WINDOW MANAGER
# ═══════════════════════════════════════════════════════════════

class WindowManager:
    """
    Manage application windows
    """
    
    def __init__(self):
        """Initialize window manager"""
        if not HAS_PYGETWINDOW:
            logger.warning("Window management limited without pygetwindow")
        
        logger.info("Window Manager initialized")
    
    def list_windows(self) -> List[str]:
        """List all window titles"""
        if not HAS_PYGETWINDOW:
            return []
        
        windows = gw.getAllTitles()
        return [w for w in windows if w.strip()]
    
    def get_active_window(self) -> Optional[str]:
        """Get active window title"""
        if not HAS_PYGETWINDOW:
            return None
        
        try:
            active = gw.getActiveWindow()
            return active.title if active else None
        except:
            return None
    
    def find_window(self, title: str) -> Optional[Any]:
        """Find window by title"""
        if not HAS_PYGETWINDOW:
            return None
        
        windows = gw.getWindowsWithTitle(title)
        return windows[0] if windows else None
    
    def activate_window(self, title: str) -> bool:
        """Activate window by title"""
        window = self.find_window(title)
        if window:
            try:
                window.activate()
                logger.info(f"Activated window: {title}")
                return True
            except Exception as e:
                logger.error(f"Window activation error: {e}")
                return False
        return False
    
    def resize_window(self, title: str, width: int, height: int) -> bool:
        """Resize window"""
        window = self.find_window(title)
        if window:
            try:
                window.resizeTo(width, height)
                logger.info(f"Resized window: {title} to {width}x{height}")
                return True
            except Exception as e:
                logger.error(f"Window resize error: {e}")
                return False
        return False
    
    def move_window(self, title: str, x: int, y: int) -> bool:
        """Move window to position"""
        window = self.find_window(title)
        if window:
            try:
                window.moveTo(x, y)
                logger.info(f"Moved window: {title} to ({x}, {y})")
                return True
            except Exception as e:
                logger.error(f"Window move error: {e}")
                return False
        return False
    
    def maximize_window(self, title: str) -> bool:
        """Maximize window"""
        window = self.find_window(title)
        if window:
            try:
                window.maximize()
                logger.info(f"Maximized window: {title}")
                return True
            except Exception as e:
                logger.error(f"Window maximize error: {e}")
                return False
        return False
    
    def minimize_window(self, title: str) -> bool:
        """Minimize window"""
        window = self.find_window(title)
        if window:
            try:
                window.minimize()
                logger.info(f"Minimized window: {title}")
                return True
            except Exception as e:
                logger.error(f"Window minimize error: {e}")
                return False
        return False
    
    def close_window(self, title: str) -> bool:
        """Close window"""
        window = self.find_window(title)
        if window:
            try:
                window.close()
                logger.info(f"Closed window: {title}")
                return True
            except Exception as e:
                logger.error(f"Window close error: {e}")
                return False
        return False
    
    def split_screen(self, title1: str, title2: str, orientation: str = "horizontal"):
        """
        Split screen between two windows
        
        Args:
            title1: First window title
            title2: Second window title
            orientation: 'horizontal' or 'vertical'
        """
        if not HAS_PYGETWINDOW or not HAS_PYAUTOGUI:
            return False
        
        screen_width, screen_height = pyautogui.size()
        
        if orientation == "horizontal":
            # Side by side
            self.move_window(title1, 0, 0)
            self.resize_window(title1, screen_width // 2, screen_height)
            
            self.move_window(title2, screen_width // 2, 0)
            self.resize_window(title2, screen_width // 2, screen_height)
        else:
            # Top and bottom
            self.move_window(title1, 0, 0)
            self.resize_window(title1, screen_width, screen_height // 2)
            
            self.move_window(title2, 0, screen_height // 2)
            self.resize_window(title2, screen_width, screen_height // 2)
        
        logger.info(f"Split screen: {title1} & {title2} ({orientation})")

# ═══════════════════════════════════════════════════════════════
# MOUSE & KEYBOARD CONTROLLER
# ═══════════════════════════════════════════════════════════════

class InputController:
    """
    Control mouse and keyboard
    """
    
    def __init__(self):
        """Initialize input controller"""
        if HAS_PYNPUT:
            self.keyboard = KeyboardController()
            self.mouse = MouseController()
        
        logger.info("Input Controller initialized")
    
    def move_mouse(self, x: int, y: int, duration: float = 0.5):
        """Move mouse to position"""
        if HAS_PYAUTOGUI:
            pyautogui.moveTo(x, y, duration=duration)
            logger.info(f"Moved mouse to ({x}, {y})")
    
    def click(self, x: Optional[int] = None, y: Optional[int] = None, button: str = 'left'):
        """Click mouse"""
        if HAS_PYAUTOGUI:
            if x is not None and y is not None:
                pyautogui.click(x, y, button=button)
            else:
                pyautogui.click(button=button)
            logger.info(f"Clicked {button} button")
    
    def double_click(self, x: Optional[int] = None, y: Optional[int] = None):
        """Double click"""
        if HAS_PYAUTOGUI:
            if x is not None and y is not None:
                pyautogui.doubleClick(x, y)
            else:
                pyautogui.doubleClick()
            logger.info("Double clicked")
    
    def scroll(self, amount: int):
        """Scroll mouse wheel"""
        if HAS_PYAUTOGUI:
            pyautogui.scroll(amount)
            logger.info(f"Scrolled {amount}")
    
    def type_text(self, text: str, interval: float = 0.05):
        """Type text"""
        if HAS_PYAUTOGUI:
            pyautogui.write(text, interval=interval)
            logger.info(f"Typed: {text[:20]}...")
    
    def press_key(self, key: str):
        """Press single key"""
        if HAS_PYAUTOGUI:
            pyautogui.press(key)
            logger.info(f"Pressed key: {key}")
    
    def hotkey(self, *keys):
        """Press hotkey combination"""
        if HAS_PYAUTOGUI:
            pyautogui.hotkey(*keys)
            logger.info(f"Pressed hotkey: {'+'.join(keys)}")
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse position"""
        if HAS_PYAUTOGUI:
            return pyautogui.position()
        return (0, 0)
    
    def screenshot(self, region: Optional[Tuple[int, int, int, int]] = None) -> Any:
        """Take screenshot"""
        if HAS_PYAUTOGUI:
            return pyautogui.screenshot(region=region)
        return None

# ═══════════════════════════════════════════════════════════════
# MACRO RECORDER
# ═══════════════════════════════════════════════════════════════

class MacroRecorder:
    """
    Record and playback mouse/keyboard macros
    """
    
    def __init__(self):
        """Initialize macro recorder"""
        self.is_recording = False
        self.recorded_events = []
        self.start_time = None
        
        logger.info("Macro Recorder initialized")
    
    def start_recording(self):
        """Start recording macro"""
        self.is_recording = True
        self.recorded_events = []
        self.start_time = time.time()
        logger.info("Macro recording started")
    
    def stop_recording(self):
        """Stop recording macro"""
        self.is_recording = False
        logger.info(f"Macro recording stopped ({len(self.recorded_events)} events)")
    
    def record_event(self, event_type: str, data: Dict[str, Any]):
        """Record single event"""
        if self.is_recording:
            timestamp = time.time() - self.start_time
            self.recorded_events.append({
                'type': event_type,
                'timestamp': timestamp,
                'data': data
            })
    
    def record_click(self, x: int, y: int, button: str = 'left'):
        """Record mouse click"""
        self.record_event('click', {'x': x, 'y': y, 'button': button})
    
    def record_keypress(self, key: str):
        """Record key press"""
        self.record_event('keypress', {'key': key})
    
    def record_type(self, text: str):
        """Record text typing"""
        self.record_event('type', {'text': text})
    
    def save_macro(self, filepath: str):
        """Save macro to file"""
        with open(filepath, 'w') as f:
            json.dump(self.recorded_events, f, indent=2)
        logger.info(f"Macro saved to: {filepath}")
    
    def load_macro(self, filepath: str):
        """Load macro from file"""
        with open(filepath, 'r') as f:
            self.recorded_events = json.load(f)
        logger.info(f"Macro loaded from: {filepath}")
    
    def playback(self, controller: InputController, speed: float = 1.0):
        """
        Playback recorded macro
        
        Args:
            controller: InputController instance
            speed: Playback speed multiplier
        """
        if not self.recorded_events:
            logger.warning("No macro to playback")
            return
        
        logger.info(f"Playing back macro ({len(self.recorded_events)} events)")
        
        last_timestamp = 0
        for event in self.recorded_events:
            # Wait for appropriate time
            wait_time = (event['timestamp'] - last_timestamp) /speed
            if wait_time > 0:
                time.sleep(wait_time)
            
            # Execute event
            event_type = event['type']
            data = event['data']
            
            if event_type == 'click':
                controller.click(data['x'], data['y'], data['button'])
            elif event_type == 'keypress':
                controller.press_key(data['key'])
            elif event_type == 'type':
                controller.type_text(data['text'])
            
            last_timestamp = event['timestamp']
        
        logger.info("Macro playback complete")

# ═══════════════════════════════════════════════════════════════
# DESKTOP CONTROLLER (Main Class)
# ═══════════════════════════════════════════════════════════════

class DesktopController:
    """
    Main desktop control system
    """
    
    def __init__(self):
        """Initialize desktop controller"""
        self.window_manager = WindowManager()
        self.input_controller = InputController()
        self.macro_recorder = MacroRecorder()
        
        logger.info("Desktop Controller initialized")
    
    def execute_command(self, command: Dict[str, Any]) -> bool:
        """
        Execute desktop control command
        
        Args:
            command: Command definition
            
        Returns:
            True if successful
        """
        cmd_type = command.get('type')
        
        try:
            if cmd_type == 'window_activate':
                return self.window_manager.activate_window(command['title'])
            elif cmd_type == 'window_resize':
                return self.window_manager.resize_window(
                    command['title'], command['width'], command['height']
                )
            elif cmd_type == 'window_move':
                return self.window_manager.move_window(
                    command['title'], command['x'], command['y']
                )
            elif cmd_type == 'window_maximize':
                return self.window_manager.maximize_window(command['title'])
            elif cmd_type == 'window_minimize':
                return self.window_manager.minimize_window(command['title'])
            elif cmd_type == 'window_close':
                return self.window_manager.close_window(command['title'])
            elif cmd_type == 'split_screen':
                self.window_manager.split_screen(
                    command['title1'], command['title2'], command.get('orientation', 'horizontal')
                )
                return True
            elif cmd_type == 'click':
                self.input_controller.click(command.get('x'), command.get('y'), command.get('button', 'left'))
                return True
            elif cmd_type == 'type':
                self.input_controller.type_text(command['text'])
                return True
            elif cmd_type == 'hotkey':
                self.input_controller.hotkey(*command['keys'])
                return True
            elif cmd_type == 'macro_record_start':
                self.macro_recorder.start_recording()
                return True
            elif cmd_type == 'macro_record_stop':
                self.macro_recorder.stop_recording()
                return True
            elif cmd_type == 'macro_playback':
                self.macro_recorder.playback(self.input_controller, command.get('speed', 1.0))
                return True
            else:
                logger.error(f"Unknown command type: {cmd_type}")
                return False
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return False

# ═══════════════════════════════════════════════════════════════
# TESTING
# ═══════════════════════════════════════════════════════════════

def main():
    """Standalone testing"""
    print("=" * 60)
    print("BAIT Desktop Controller - Test Mode")
    print("=" * 60)
    
    controller = DesktopController()
    
    # List windows
    print("\n🪟 Active windows:")
    windows = controller.window_manager.list_windows()
    for i, win in enumerate(windows[:10], 1):
        print(f"  {i}. {win}")
    
    # Get mouse position
    if HAS_PYAUTOGUI:
        print(f"\n🖱️  Mouse position: {controller.input_controller.get_mouse_position()}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
