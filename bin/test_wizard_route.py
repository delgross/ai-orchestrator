import requests
import json
import os

TOKEN = "9sYBjBLjAHKG8g8ZzzsUeBOvtzgQFHmX7oIeygdpzic"
URL = "http://127.0.0.1:5455/v1/chat/completions"

payload = {
    "model": "agent:mcp",
    "messages": [
        {"role": "system", "content": "You are a test."},
        {"role": "user", "content": "Ping."}
    ],
    "stream": False
}

print(f"Sending request to {URL}...")
try:
    resp = requests.post(URL, json=payload, headers={"Authorization": f"Bearer {TOKEN}"}, timeout=10)
    print(f"Status: {resp.status_code}")
    print(f"Content: {resp.text}")
except Exception as e:
    print(f"Failed: {e}")
