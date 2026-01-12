
import requests
import json
import time

URL = "http://127.0.0.1:5460/v1/chat/completions"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer antigravity_router_token_2025"
}

# Payload to trigger list_all_available_tools
PAYLOAD = {
    "messages": [
        {"role": "user", "content": "list all available tools"}
    ],
    "model": "agent:mcp",
    "stream": False
}

def check_tools():
    print(f"🚀 Sending request to {URL}...")
    try:
        resp = requests.post(URL, headers=HEADERS, json=PAYLOAD, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        
        content = data['choices'][0]['message']['content']
        print(f"Agent Response Truncated: {content[:500]}...")
        
        # We also want to see if we can get the raw tool list via the tool call if it makes one
        if "tool_calls" in data['choices'][0]['message']:
             print("Tool calls found:", data['choices'][0]['message']['tool_calls'])
        
        # Actually, let's just inspect the logs or use the 'list_all_available_tools' tool response if the agent calls it.
        # But if the agent calls it, we need to run the tool.
        # Simpler: just grep the logs for "Active Tools passed to Model" since I'm running manually.
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_tools()
