#!/usr/bin/env python3
"""
Force reload MCP servers from database to fix runtime state.
This syncs the runtime state.mcp_servers with the database.
"""
import asyncio
import sys
import httpx
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def reload_mcp_servers():
    """Reload MCP servers via API endpoint."""
    base_url = "http://localhost:5460"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Try to reload via API if endpoint exists
        # Otherwise, we'll need to restart the service
        try:
            # Check if there's a reload endpoint
            resp = await client.post(f"{base_url}/api/admin/reload-mcp")
            if resp.status_code == 200:
                print("✅ MCP servers reloaded via API")
                return
        except Exception:
            pass
        
        # Fallback: Use the config reload endpoint if available
        try:
            from agent_runner.state import AgentState
            from agent_runner.config import load_mcp_servers
            
            state = AgentState()
            await state.initialize()
            
            print("Reloading MCP servers from database...")
            await load_mcp_servers(state)
            
            print(f"✅ Loaded {len(state.mcp_servers)} MCP servers")
            for name, cfg in state.mcp_servers.items():
                enabled = cfg.get("enabled", True)
                status = "✅" if enabled else "❌"
                print(f"  {status} {name}: enabled={enabled}")
        except Exception as e:
            print(f"❌ Error: {e}")
            print("\n⚠️  You may need to restart the agent runner for changes to take effect.")
            print("   Run: ./bin/run_agent_runner.sh restart")

if __name__ == "__main__":
    asyncio.run(reload_mcp_servers())


