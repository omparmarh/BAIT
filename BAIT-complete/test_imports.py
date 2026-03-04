import sys
from pathlib import Path

backend = Path("backend")
sys.path.insert(0, str(backend))

modules = [
    "voice_engine", "vision_processor", "memory_system",
    "automation_engine", "browser_agent", "desktop_controller",
    "file_manager", "avatar_controller", "api_integrations"
]

for m in modules:
    try:
        __import__(m)
        print(f"OK: {m}")
    except Exception as e:
        print(f"FAILED: {m} - {type(e).__name__}: {str(e)}")
