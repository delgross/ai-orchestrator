
import asyncio
import logging
import yaml
import sys
import os
sys.path.append("/Users/bee/Sync/Antigravity/ai")

from agent_runner.state import AgentState
from agent_runner.db_utils import run_query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sync_prompts")

async def sync_prompts():
    print("🎭 Syncing Prompts to Sovereign Memory...")
    
    state = AgentState()
    await state.initialize()
    
    # Read YAML
    config_path = "/Users/bee/Sync/Antigravity/ai/config/sovereign.yaml"
    with open(config_path, "r") as f:
        data = yaml.safe_load(f)
        
    system_template = data.get("prompts", {}).get("system_template")
    chat_suffix = data.get("modes", {}).get("chat", {}).get("prompt_suffix")
    
    updates = {
        "system_template": system_template,
        "chat_prompt_suffix": chat_suffix
    }
    
    for key, value in updates.items():
        if not value:
            print(f"⚠️ Missing value for {key} in YAML")
            continue
            
        print(f"🔄 Updating {key}...")
        try:
            # Delete old
            await run_query(state, "DELETE FROM config_state WHERE key = $key", {"key": key})
            
            # Insert new using parameters (SurrealDB handles escaping)
            # Note: run_query wrapper might need dictionary for params
            await run_query(
                state, 
                "INSERT INTO config_state (key, value) VALUES ($key, $value)", 
                {"key": key, "value": value}
            )
            print(f"✅ Updated {key}")
        except Exception as e:
            print(f"❌ Error updating {key}: {e}")

    print("🎭 Sync Complete.")

if __name__ == "__main__":
    asyncio.run(sync_prompts())
