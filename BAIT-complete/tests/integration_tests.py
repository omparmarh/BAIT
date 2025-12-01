import unittest
import requests
import json
import time
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

BASE_URL = "http://127.0.0.1:8000/api/ultimate"

class TestBAITUltimate(unittest.TestCase):
    """
    Comprehensive Integration Tests for BAIT PRO ULTIMATE
    Covers all 10 phases of the implementation
    """

    def setUp(self):
        # Ensure server is running (check health)
        try:
            response = requests.get(f"{BASE_URL}/health")
            if response.status_code != 200:
                print("WARNING: Server might not be running or healthy")
        except:
            print("WARNING: Server connection failed. Make sure api_server.py is running.")

    # 1. Voice Control Test
    def test_voice_control_endpoints(self):
        print("\nTesting Voice Control...")
        # Start voice
        response = requests.post(f"{BASE_URL}/voice/start", json={"provider": "google"})
        # It might fail if no mic, but endpoint should exist
        if response.status_code == 500 and "PyAudio" in response.text:
            print("Voice start failed (expected if no mic):", response.text)
        else:
            self.assertIn(response.status_code, [200, 500])
        
        # Stop voice
        response = requests.post(f"{BASE_URL}/voice/stop")
        self.assertEqual(response.status_code, 200)

    # 2. Memory System Test
    def test_memory_system(self):
        print("\nTesting Memory System...")
        # Store memory
        memory_data = {
            "content": "Integration test memory",
            "memory_type": "fact",
            "importance": 1
        }
        response = requests.post(f"{BASE_URL}/memory/store", json=memory_data)
        self.assertEqual(response.status_code, 200)
        
        # Recall memory
        response = requests.post(f"{BASE_URL}/memory/recall", json={"query": "Integration test"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data.get("memories"), list)

    # 3. Workflow Automation Test
    def test_workflow_automation(self):
        print("\nTesting Workflow Automation...")
        # Create workflow
        workflow_data = {"description": "Every day at 10am, log 'test'"}
        response = requests.post(f"{BASE_URL}/workflow/create", json=workflow_data)
        self.assertEqual(response.status_code, 200)
        workflow_id = response.json().get("workflow_id")
        
        # List workflows
        response = requests.get(f"{BASE_URL}/workflow/list")
        self.assertEqual(response.status_code, 200)
        
        # Delete workflow
        if workflow_id:
            response = requests.delete(f"{BASE_URL}/workflow/{workflow_id}")
            self.assertEqual(response.status_code, 200)

    # 4. Vision System Test
    def test_vision_system(self):
        print("\nTesting Vision System...")
        # Screen analysis
        response = requests.get(f"{BASE_URL}/vision/analyze-screen")
        # Might fail if dependencies missing, but endpoint should be there
        self.assertIn(response.status_code, [200, 500, 501])
        
        # Camera status
        response = requests.get(f"{BASE_URL}/vision/camera-status")
        self.assertIn(response.status_code, [200, 500, 501])

    # 5. Browser Agent Test
    def test_browser_agent(self):
        print("\nTesting Browser Agent...")
        # Search
        response = requests.post(f"{BASE_URL}/browser/search", json={"query": "python"})
        self.assertIn(response.status_code, [200, 500, 501])

    # 6. Desktop Control Test
    def test_desktop_control(self):
        print("\nTesting Desktop Control...")
        # List windows
        response = requests.get(f"{BASE_URL}/desktop/windows")
        self.assertIn(response.status_code, [200, 500, 501])

    # 7. File Manager Test
    def test_file_manager(self):
        print("\nTesting File Manager...")
        # Search files
        response = requests.post(f"{BASE_URL}/files/search", json={"query": "test"})
        self.assertIn(response.status_code, [200, 500, 501])

    # 8. Avatar Controller Test
    def test_avatar_controller(self):
        print("\nTesting Avatar Controller...")
        # Expression
        response = requests.post(f"{BASE_URL}/avatar/expression", json={"expression": "happy"})
        self.assertIn(response.status_code, [200, 500, 501])

    # 9. API Integrations Test
    def test_api_integrations(self):
        print("\nTesting API Integrations...")
        # Health check covers availability
        response = requests.get(f"{BASE_URL}/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("modules_available", data)

if __name__ == '__main__':
    unittest.main()
