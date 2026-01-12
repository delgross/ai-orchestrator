
import asyncio
from agent_runner.state import AgentState
from agent_runner.db_utils import run_query

async def update_roles():
    state = AgentState()
    from agent_runner.memory_server import MemoryServer
    state.memory = MemoryServer(state)
    await state.memory.initialize()
    
    # Qwen 2.5 Coder Upgrade
    coder_model = "ollama:qwen2.5-coder:32b"
    
    updates = {
        "HEALER_MODEL": "ollama:qwq:latest", # Transient (High Intel)
        
        # Upgrade Resident Roles to Coder
        "CRITIC_MODEL": coder_model, 
        "TASK_MODEL": coder_model,
        "MCP_MODEL": coder_model,
        "INTENT_MODEL": coder_model # Maître d' Logic
    }
    
    for key, value in updates.items():
        print(f"Updating {key} to {value}...")
        await run_query(state, f"DELETE config_state WHERE key = '{key}'")
        query = f"""
        CREATE config_state:{key} SET 
            key = '{key}', 
            value = '{value}',
            updated_at = time::now();
        """
        await run_query(state, query)
        print(f"✅ Updated {key}.")

if __name__ == "__main__":
    asyncio.run(update_roles())
