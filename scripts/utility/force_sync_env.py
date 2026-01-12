import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from agent_runner.state import AgentState
from agent_runner.config_manager import ConfigManager
from agent_runner.db_utils import run_query

async def main():
    print("Initializing State...")
    state = AgentState()
    await state.initialize()
    
    config_manager = ConfigManager(state)
    env_path = state.agent_fs_root.parent / ".env"
    
    print(f"Syncing .env from {env_path} to Sovereign Memory...")
    if not env_path.exists():
        print("Error: .env not found")
        return
        
    await config_manager.sync_env_from_disk()
    print("Sync Complete.")
    
    # Verify
    res = await run_query(state, "SELECT value FROM config_state WHERE key = 'AGENT_MODEL'")
    if res:
        print(f"DB AGENT_MODEL: {res[0]['value']}")
    else:
        print("DB AGENT_MODEL not found!")

if __name__ == "__main__":
    asyncio.run(main())
