
import time
import requests
import json
import sys

URL = "http://127.0.0.1:5455/v1/chat/completions" # Router
DIRECT_URL = "http://127.0.0.1:5460/v1/chat/completions" # Agent Runner
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer antigravity_router_token_2025"
}
PAYLOAD = {
    "messages": [{"role": "user", "content": "What is the capital of France?"}],
    "model": "agent:mcp",
    "stream": True 
}

def measure_url(url, name):
    print(f"🚀 Sending request to {url} ({name})...")
    start_time = time.time()
    
    try:
        # Use stream=True to measure TTFT
        with requests.post(url, headers=HEADERS, json=PAYLOAD, stream=True, timeout=10) as r:
            r.raise_for_status()
            
            first_byte_time = None
            total_content = ""
            
            for line in r.iter_lines():
                if line:
                    if first_byte_time is None:
                        first_byte_time = time.time()
                        ttft = first_byte_time - start_time
                        print(f"⏱️ TTFT ({name}): {ttft:.4f}s")
                    
                    # Consume content
                    decoded = line.decode('utf-8')
                    print(decoded) # Debug enabled
                    total_content += decoded
            
            end_time = time.time()
            total_time = end_time - start_time
            print(f"🏁 Total Time ({name}): {total_time:.4f}s")
            
    except Exception as e:
        print(f"❌ Error ({name}): {e}")

def measure():
    measure_url(URL, "Router")
    measure_url(DIRECT_URL, "Agent Runner")

if __name__ == "__main__":
    measure()
