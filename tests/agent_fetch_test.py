import requests
import json
import sys

def test_agent_fetch():
    url = "http://127.0.0.1:5460/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "agent:mcp",
        "messages": [
            {"role": "user", "content": "Fetch the content of https://example.com"}
        ],
        "stream": False
    }

    try:
        print(f"Sending request to {url}...")
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("Response Body:")
            print(json.dumps(response.json(), indent=2))
        else:
            print("Error Response:")
            print(response.text)
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_agent_fetch()
