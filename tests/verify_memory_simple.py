
import requests
import json

URL = "http://127.0.0.1:5460/v1/chat/completions"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer antigravity_router_token_2025"
}

PAYLOAD = {
    "messages": [
        {"role": "user", "content": "remember that the sky is purple"}
    ],
    "model": "agent:mcp",
    "stream": False
}

def verify_memory():
    print(f"🚀 Sending request to {URL}...")
    try:
        resp = requests.post(URL, headers=HEADERS, json=PAYLOAD, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        
        content = data['choices'][0]['message']['content']
        print(f"Agent Response: {content}")
        
        # Check tool calls
        if "tool_calls" in data['choices'][0]['message']:
            print("Tool Calls:", data['choices'][0]['message']['tool_calls'])
        
        # We look for confirmation or tool usage
        if "stored" in content.lower() or "remembered" in content.lower() or "memory_store_fact" in str(data):
             print("✅ Success: Memory tool used.")
        else:
             print("⚠️ Warning: Memory tool might not have been used.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verify_memory()
