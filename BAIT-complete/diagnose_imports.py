
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(r"c:/Users/a2z/Downloads/BAIT-complete (1) - Copy/BAIT-complete/backend")
sys.path.insert(0, str(backend_path))

print(f"Checking imports from {backend_path}...")

modules = [
    "voice_engine",
    "vision_processor",
    "memory_system",
    "automation_engine",
    "browser_agent",
    "desktop_controller",
    "file_manager",
    "avatar_controller",
    "api_integrations"
]

for module in modules:
    try:
        __import__(module)
        print(f"✅ {module} imported successfully")
    except ImportError as e:
        print(f"❌ {module} failed to import: {e}")
    except Exception as e:
        print(f"❌ {module} failed with error: {e}")
