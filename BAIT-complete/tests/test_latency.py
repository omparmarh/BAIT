import time
import requests
import json

def measure_latency():
    print("🚀 Measuring BAIT TTS Latency...")
    url = "http://localhost:8000/api/chat"
    payload = {"message": "Tell me a very long story about a robot and a space traveler."}
    
    start_time = time.time()
    try:
        # Use streaming to see how fast the first chunk arrives
        response = requests.post(url, json=payload, stream=True)
        first_chunk_time = None
        
        for chunk in response.iter_lines():
            if not first_chunk_time:
                first_chunk_time = time.time()
                print(f"✅ First chunk arrived in: {first_chunk_time - start_time:.2f}s")
                break
        
        total_time = time.time() - start_time
        print(f"📊 Total latency check complete.")
        
    except Exception as e:
        print(f"❌ Error during latency check: {e}")

if __name__ == "__main__":
    # Note: This script assumes the server is running
    # measure_latency()
    pass
