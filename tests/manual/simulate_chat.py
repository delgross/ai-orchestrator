#!/usr/bin/env python3
import asyncio
import aiohttp
import json
import argparse
import sys

# Default Config
ROUTER_URL = "http://localhost:5455/v1/chat/completions"
DEFAULT_MODEL = "ollama:llama3.1:latest"

async def chat_stream(prompt, model=DEFAULT_MODEL, url=ROUTER_URL, token=None, raw=False):
    """
    Simulates a chat request to the router with streaming.
    """
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": True
    }
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    print(f"Connecting to {url}...")
    print(f"Model: {model}")
    print(f"Prompt: {prompt}\n")
    print("-" * 40)

    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    print(f"Error: HTTP {response.status}")
                    text = await response.text()
                    print(f"Response: {text}")
                    return

                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if not line:
                        continue

                    if line.startswith("data: "):
                        data_str = line[6:]  # Strip "data: "
                        
                        if data_str == "[DONE]":
                            print("\n" + "-" * 40)
                            print("[DONE] Signal received.")
                            break
                        
                        try:
                            data = json.loads(data_str)
                            if raw:
                                print(f"RAW: {data}")
                            
                            delta = data.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            
                            if content:
                                sys.stdout.write(content)
                                sys.stdout.flush()
                        except json.JSONDecodeError:
                            print(f"\n[Error] Failed to parse JSON: {data_str}")
                    else:
                        if raw:
                            print(f"UNKNOWN LINE: {line}")
                            
    except Exception as e:
        print(f"\n[Exception] {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate a chat request to the AI Router.")
    parser.add_argument("--prompt", type=str, default="Hello, who are you?", help="User prompt to send.")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help="Model ID to use.")
    parser.add_argument("--url", type=str, default=ROUTER_URL, help="Router endpoint URL.")
    parser.add_argument("--token", type=str, default=None, help="Bearer token for authentication.")
    parser.add_argument("--raw", action="store_true", help="Print raw JSON chunks.")
    
    args = parser.parse_args()
    
    asyncio.run(chat_stream(args.prompt, args.model, args.url, args.token, args.raw))
