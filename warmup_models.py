
import asyncio
import time
import httpx
import json
import sys

# Define Models to Warmup
MODELS = [
    {
        "name": "ollama:llama3.3:70b",
        "role": "Agent (Slot 0)",
        "prompt": "Hello", 
        "config": {"num_ctx": 32768} 
    },
    {
        "name": "ollama:qwen2.5:7b-instruct",
        "role": "Maître d' (Slot 1)",
        "prompt": "Hello",
        "config": {"num_ctx": 32768}
    }
]

BASE_URL = "http://127.0.0.1:11434/v1/chat/completions"

async def warmup_single_model(model_def):
    name = model_def["name"]
    clean_name = name.replace("ollama:", "")
    role = model_def["role"]
    
    print(f"🔥 Warming up {role} [{clean_name}]...")
    
    payload = {
        "model": clean_name,
        "messages": [{"role": "user", "content": model_def["prompt"]}],
        "stream": False,
        "options": model_def["config"]
    }
    
    t0 = time.time()
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(BASE_URL, json=payload)
            dur = time.time() - t0
            
            if resp.status_code == 200:
                print(f"✅ {role} Ready in {dur:.2f}s")
            else:
                print(f"❌ {role} Failed: {resp.status_code} - {resp.text}")
                
    except Exception as e:
        print(f"❌ {role} Error: {e}")

async def main():
    print("🚀 Starting Parallel Model Warmup sequence...")
    print("Note: This ensures both 70B and 7B models are pinned to VRAM slots.")
    
    # Run sequentially to ensure deterministic slot filling order
    # (Though Ollama handles it, sequential is safer for predictable logs)
    for model in MODELS:
        await warmup_single_model(model)
        
    print("\n✨ All Models Warmed Up. System is Ready for Hybrid Execution.")

if __name__ == "__main__":
    asyncio.run(main())
