
import time
import requests
import json

ROUTER_URL = "http://127.0.0.1:5455/v1/chat/completions"

def benchmark_chat():
    print(f"\n--- Benchmarking Chat Router (UI Sim) ---")
    
    data = {
        "messages": [
            {"role": "user", "content": "What time is it?"}
        ],
        "model": "agent",
        "stream": False # Measure full roundtrip first
    }
    
    headers = {
        "Authorization": "Bearer antigravity_router_token_2025"
    }
    
    start_time = time.time()
    try:
        response = requests.post(ROUTER_URL, json=data, headers=headers, timeout=30)
        end_time = time.time()
        
        duration = end_time - start_time
        
        if response.status_code == 200:
            print(f"✅ Success. Duration: {duration:.4f}s")
            res_json = response.json()
            # Try to extract content
            content = ""
            if "choices" in res_json:
                 content = res_json["choices"][0]["message"]["content"]
            print(f"   Output: {content.strip()}")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    benchmark_chat()
