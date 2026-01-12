
import requests
import json
import time

URL = "http://127.0.0.1:5460/v1/chat/completions"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer antigravity_router_token_2025"
}

# Payload to trigger add_mcp_server tool call
PAYLOAD = {
    "messages": [
        {"role": "user", "content": "add mcp server named test-server with command 'echo hello'"}
    ],
    "model": "agent:mcp",
    "stream": False # Use non-stream for easier parsing
}

def verify():
    print(f"🚀 Sending request to {URL}...")
    try:
        resp = requests.post(URL, headers=HEADERS, json=PAYLOAD, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        
        # Check if the response contains a tool call to add_mcp_server
        content = data['choices'][0]['message']['content']
        print(f"Agent Response: {content}")
        
        if '"name": "add_mcp_server"' in content or "'name': 'add_mcp_server'" in content:
            print("✅ SUCCESS: Agent selected 'add_mcp_server' tool.")
        elif '"name": "install_mcp_package"' in content:
            print("⚠️ PARTIAL SUCCESS: Agent selected 'install_mcp_package' (acceptable if interpreted as package).")
        else:
            print("❌ FAILED: Agent did NOT select 'add_mcp_server'. Listing tools in response...")
            # Ideally we'd inspect the actual tool definitions available to the model, but we can infer from failure.

    except Exception as e:
        print(f"❌ Error: {e}")
        if hasattr(e, 'response'):
             print(f"Response text: {e.response.text}")

if __name__ == "__main__":
    # Give a moment for restart
    time.sleep(2)
    verify()
