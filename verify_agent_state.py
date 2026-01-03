
import asyncio
import os
import sys

# Add path to sys
sys.path.append("/Users/bee/Sync/Antigravity/ai")

from agent_runner.state import AgentState
from agent_runner.config_manager import ConfigManager

async def main():
    print("--- DIAGNOSTIC DUMP ---")
    state = AgentState()
    
    # Check Env
    print(f"ENV[AGENT_MODEL]: {os.getenv('AGENT_MODEL')}")
    print(f"ENV[llm_roles.agent_model]: {os.getenv('llm_roles.agent_model')}")
    
    # Check Defaults (before DB)
    state._load_base_config()
    print(f"STATE.agent_model (Base Config): {state.agent_model}")
    
    # Check DB Load
    cm = ConfigManager(state)
    await state._load_runtime_config_from_db()
    print(f"STATE.agent_model (After DB): {state.agent_model}")
    
    print("--- ROLES ---")
    print(f"TASK_MODEL: {state.task_model}")
    print(f"ROUTER_MODEL: {state.router_model}")
    print(f"MCP_MODEL: {state.mcp_model}")

if __name__ == "__main__":
    asyncio.run(main())
