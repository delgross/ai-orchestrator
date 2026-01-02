import asyncio
import json
import os
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from agent_runner.state import AgentState
from common.constants import OBJ_MODEL

async def test_model(state, role, model_name):
    print(f"Testing {role}: {model_name}...", end=" ", flush=True)
    start = time.time()
    try:
        if "openai" in model_name:
            client = await state.get_http_client()
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"}
            payload = {
                "model": model_name.replace("openai:", ""),
                "messages": [{"role": "user", "content": "Hello, say 'ok'."}],
                "max_completion_tokens": 100
            }
            resp = await client.post(url, json=payload, headers=headers, timeout=10.0)
            if resp.status_code != 200:
                print(f"FAILED ({resp.status_code})")
                print(f"  Error: {resp.text}")
                return False
        else:
            # Local Ollama check via Gateway or Direct
            # We'll use the providers logic via state if possible, but simplest is direct request
            # For now, let's just assume the Agent Runner's http client is set up, 
            # but actually state.get_http_client returns a shared client.
            # Let's route through the Router's provider logic logic? No, too complex.
            # Detailed check:
            client = await state.get_http_client()
            # Assuming standard Ollama port
            url = "http://127.0.0.1:11434/api/chat"
            payload = {
                "model": model_name.replace("ollama:", ""),
                "messages": [{"role": "user", "content": "Hello, say 'ok'."}],
                "stream": False
            }
            resp = await client.post(url, json=payload, timeout=30.0)
            if resp.status_code != 200:
                print(f"FAILED ({resp.status_code})")
                return False
                
        duration = round(time.time() - start, 2)
        print(f"OK ({duration}s)")
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

async def main():
    print("--- Verifying Hybrid Model Architecture ---")
    
    # Load environment variables (Try both locations)
    from dotenv import load_dotenv
    root = Path(__file__).parent.parent
    env_path = root / ".env"
    
    print(f"DEBUG: Looking for .env at: {env_path}")
    if env_path.exists():
        print(f"DEBUG: File exists. Size: {env_path.stat().st_size} bytes")
        load_dotenv(env_path, override=True)
    else:
        print("DEBUG: .env FILE NOT FOUND at calculated path.")
        
    providers_env = root / "providers.env"
    if providers_env.exists():
        load_dotenv(providers_env, override=True)

    key = os.getenv("OPENAI_API_KEY")
    if not key:
        print("WARNING: OPENAI_API_KEY not found in env.", flush=True)
    else:
        print(f"DEBUG: API Key found (Length: {len(key)})", flush=True)
    
    state = AgentState()
    
    # Load Config (Simulated, since AgentState loads it async usually or in init)
    # Actually AgentState init loads config.yaml. system_config.json is loaded on demand or by tasks.
    # Config is at ../system_config.json relative to ai/tests
    config_path = Path(__file__).parent.parent / "system_config.json"
    with open(config_path) as f:
        sys_cfg = json.load(f)
    
    agent_model = sys_cfg.get("agent_model")
    router_model = sys_cfg.get("router_model")
    worker_model = sys_cfg.get("task_model")
    
    results = []
    results.append(await test_model(state, "Brain (GPT-5.1)", agent_model))
    results.append(await test_model(state, "Router (8B)", router_model))
    results.append(await test_model(state, "Worker (70B)", worker_model))
    
    if all(results):
        print("\n✅ All Systems Operational")
        sys.exit(0)
    else:
        print("\n❌ Verification Failed")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
