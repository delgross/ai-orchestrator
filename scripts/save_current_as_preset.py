import asyncio
import os
import yaml
import json
import httpx

async def save_preset():
    # 1. Read Config
    with open("config/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # Extract model config
    system_config = config.get("system", {})
    models = {k: v for k, v in system_config.items() if k.endswith("_model")}
    
    preset_name = "The Best"
    description = "Formula 1 Configuration: 70B Agent, 32B Intent, QwQ Critic."
    
    print(f"Saving Preset [{preset_name}]...")
    print(json.dumps(models, indent=2))
    
    # 3. Construct SQL (Explicit Namespace)
    models_json = json.dumps(models)
    q = "USE NS orchestrator; USE DB memory; "
    q += f"DELETE FROM model_presets WHERE name = '{preset_name}'; "
    q += f"CREATE model_presets SET name = '{preset_name}', config = {models_json}, description = '{description}', created_at = time::now();"
    
    # 3. Send to SurrealDB
    url = "http://127.0.0.1:8000/sql"
    headers = {"ns": "orchestrator", "db": "memory", "Accept": "application/json"}
    auth = ("root", "root")
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, content=q, headers=headers, auth=auth)
            print(f"DB Response: {resp.status_code} {resp.text}")
            if resp.status_code == 200:
                print("✅ Preset saved successfully.")
            else:
                print("❌ Failed to save preset.")
        except Exception as e:
            print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(save_preset())
