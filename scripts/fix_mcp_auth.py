import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from agent_runner.state import AgentState
from agent_runner.db_utils import run_query
from agent_runner.config_manager import ConfigManager

async def fix_mcp_auth():
    print("🔧 Starting MCP Auth Fix...")
    
    # Initialize State
    state = AgentState()
    await state.initialize()
    
    # 1. Fetch current config from DB
    print("   Querying 'project-memory' configuration from Sovereign Memory...")
    result = await run_query(state, "SELECT * FROM mcp_server WHERE name = 'project-memory'")
    
    if not result:
        print("❌ Error: 'project-memory' server not found in database!")
        return

    config = result[0]
    print(f"   Found config: {config.get('name')}")
    
    # 2. Patch Environment Variables
    env = config.get("env", {})
    if "ROUTER_AUTH_TOKEN" in env and env["ROUTER_AUTH_TOKEN"] == "${ROUTER_AUTH_TOKEN}":
        print("✅ Config already patched. No action needed.")
        return

    print("   Injecting ROUTER_AUTH_TOKEN into environment...")
    env["ROUTER_AUTH_TOKEN"] = "${ROUTER_AUTH_TOKEN}"
    config["env"] = env
    
    # 3. Update Database using ConfigManager (Handles history/validation)
    # We need to re-instantiate ConfigManager properly if state doesn't have it
    if not hasattr(state, 'config_manager'):
        state.config_manager = ConfigManager(state)
        
    await state.config_manager.update_mcp_server("project-memory", config)
    print("✅ Database updated successfully.")
    
    # 4. Verification
    verify = await run_query(state, "SELECT env FROM mcp_server WHERE name = 'project-memory'")
    print(f"   Verification: {verify[0]['env']}")
    
    print("\n🎉 Fix Complete. Please restart the agent: ./restart_services.sh")

if __name__ == "__main__":
    asyncio.run(fix_mcp_auth())
