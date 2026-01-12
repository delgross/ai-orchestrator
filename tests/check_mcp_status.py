
import requests
import json

URL = "http://127.0.0.1:5460/v1/chat/completions"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer antigravity_router_token_2025"
}

PAYLOAD = {
    "messages": [
        {"role": "user", "content": "check status of mcp server named system-control"}
    ],
    "model": "agent:mcp",
    "stream": False
}

def check_status():
    print(f"🚀 Sending request to {URL}...")
    try:
        resp = requests.post(URL, headers=HEADERS, json=PAYLOAD, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        print(f"Response: {data['choices'][0]['message']['content']}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_status()
