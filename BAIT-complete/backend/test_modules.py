#!/usr/bin/env python3
"""
BAIT-complete - Test Backend Modules
Quick test to see which modules load successfully
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

print("="*60)
print("🧪 TESTING BACKEND MODULES")
print("="*60)

modules_to_test = [
    ('voice_engine', 'VoiceControlEngine'),
    ('vision_processor', 'VisionProcessor'),
    ('memory_system', 'MemorySystem'),
    ('automation_engine', 'AutomationEngine'),
    ('browser_agent', 'BrowserAgent'),
    ('desktop_controller', 'DesktopController'),
    ('file_manager', 'FileManager'),
    ('avatar_controller', 'AvatarController'),
    ('api_integrations', 'APIIntegrationManager'),
]

results = {}

for module_name, class_name in modules_to_test:
    try:
        module = __import__(module_name)
        cls = getattr(module, class_name)
        results[module_name] = "✅ OK"
        print(f"✅ {module_name}.{class_name} - LOADED")
    except Exception as e:
        results[module_name] = f"❌ {str(e)[:50]}"
        print(f"❌ {module_name}.{class_name} - FAILED: {e}")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)

working = sum(1 for v in results.values() if v.startswith("✅"))
total = len(results)

print(f"\nWorking: {working}/{total}")

for name, status in results.items():
    print(f"{name:20} {status}")

print("\n" + "="*60)

if working == total:
    print("✅ ALL MODULES WORKING!")
else:
    print(f"⚠️ {total - working} modules need attention")
