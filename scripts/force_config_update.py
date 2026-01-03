
import asyncio
import os
from agent_runner.state import AgentState

async def update_config():
    print("Initializing State...")
    state = AgentState()
    await state.initialize()
    
    # Define Target Config
    updates = {
        "AGENT_MODEL": "openai:gpt-5.1", 
        "TASK_MODEL": "openai:gpt-5.1", 
        "MCP_MODEL": "ollama:qwq:latest", # Balanced Local
        
        # Local Plumbing
        "ROUTER_MODEL": "ollama:mistral:latest",
        "INTENT_MODEL": "ollama:llama3.1:latest",
        "SUMMARIZATION_MODEL": "ollama:mistral:latest", # Downgrade from 70B
        "FINALIZER_MODEL": "ollama:mistral:latest",     # Downgrade from 70B
        "HEALER_MODEL": "ollama:llama3.3:70b-instruct-q8_0", # Keep Smart
        "CRITIC_MODEL": "ollama:llama3.3:70b-instruct-q8_0", # Keep Smart
    }
    print("Updating Sovereign Memory...")
    for key, val in updates.items():
        print(f"  Setting {key} -> {val}")
        # Direct DB Update
        await state.config_manager.set_config_value(key, val)
        
    print("Done. Please restart Agent Runner.")

if __name__ == "__main__":
    asyncio.run(update_config())
