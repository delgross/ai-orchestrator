import json
import requests
import sys

def test_ollama_stream():
    url = "http://127.0.0.1:5455/v1/chat/completions"
    payload = {
        "model": "ollama:mistral:latest",
        "messages": [{"role": "user", "content": "Tell me a very short joke."}],
        "stream": True
    }
    
    headers = {
        "Authorization": "Bearer 9sYBjBLjAHKG8g8ZzzsUeBOvtzgQFHmX7oIeygdpzic"
    }
    
    print(f"Testing Ollama Stream: {url}")
    try:
        response = requests.post(url, json=payload, headers=headers, stream=True, timeout=30)
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                print(f"RAW: {line_str}")
                if line_str.startswith("data: "):
                    data_str = line_str[6:]
                    if data_str == "[DONE]":
                        print("Stream Finished")
                        break
                    try:
                        data = json.loads(data_str)
                        content = data['choices'][0]['delta'].get('content', '')
                        if content:
                            sys.stdout.write(content)
                            sys.stdout.flush()
                    except Exception as e:
                        print(f"\nError parsing JSON: {e}")
        print("\n--- Test Complete ---")
    except Exception as e:
        print(f"\nRequest Failed: {e}")

if __name__ == "__main__":
    test_ollama_stream()
