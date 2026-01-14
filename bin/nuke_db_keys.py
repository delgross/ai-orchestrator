
import asyncio
import os
import sys
from pathlib import Path

# Setup path
sys.path.append(str(Path(__file__).parent.parent))

from agent_runner.state import AgentState
from agent_runner.db_utils import run_query

async def nuke_keys():
    print("☢️ Nuking Specific Config Keys...")
    state = AgentState()
    try:
        await state.initialize()
    except:
        pass
        
    keys_to_nuke = [
        "INTENT_MODEL", "AGENT_MODEL", "ROUTER_MODEL", "TASK_MODEL",
        "SUMMARIZATION_MODEL", "MCP_MODEL", "FINALIZER_MODEL", "CRITIC_MODEL",
        "HEALER_MODEL", "FALLBACK_MODEL", "PRUNER_MODEL", "QUERY_REFINEMENT_MODEL",
        "AGENT", "SYSTEM" # Nuke the dictionaries too
    ]
    
    for key in keys_to_nuke:
        q = f"DELETE FROM config_state WHERE key = '{key}';"
        await run_query(state, q)
        print(f"Executed: {q}")
        
    print("✅ Nuke sequence complete.")

if __name__ == "__main__":
    asyncio.run(nuke_keys())
