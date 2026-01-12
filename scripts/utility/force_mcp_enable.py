import asyncio
import sys
import yaml
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from agent_runner.agent_runner import get_shared_state
from agent_runner.config_manager import ConfigManager

async def force_enable_mcp():
    print("🚀 Starting Force Enable of MCP Servers...")
    state = get_shared_state()
    # Initialize Memory Server (required for DB access)
    from agent_runner.memory_server import MemoryServer
    state.memory = MemoryServer(state)
    await state.memory.initialize()
    
    config_manager = ConfigManager(state)
    state.config_manager = config_manager
    
    mcp_path = project_root / "config" / "mcp.yaml"
    if not mcp_path.exists():
        print(f"❌ mcp.yaml not found at {mcp_path}")
        return

    with open(mcp_path, "r") as f:
        data = yaml.safe_load(f) or {}
        
    servers = data.get("mcp_servers", {})
    print(f"Found {len(servers)} servers in mcp.yaml")
    
    for name, config in servers.items():
        # Force enabled=True based on file (which we edited)
        config["enabled"] = True
        print(f"Enabling {name}...")
        await config_manager.update_mcp_server(name, config)
        
    print("✅ All servers updated in Sovereign Memory.")
    
    # Verify by reading back
    print("Verifying DB state...")
    results = await state.memory._execute_query("SELECT name, enabled FROM mcp_server")
    for r in results:
        print(f" - {r['name']}: {r.get('enabled')}")

if __name__ == "__main__":
    try:
        asyncio.run(force_enable_mcp())
    except Exception as e:
        print(f"❌ Error: {e}")
