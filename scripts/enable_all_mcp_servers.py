#!/usr/bin/env python3
"""
Enable all disabled MCP servers in the database.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from agent_runner.state import AgentState
from agent_runner.memory_server import MemoryServer

async def enable_all_mcp_servers():
    """Enable all disabled MCP servers."""
    print("🚀 Enabling all disabled MCP servers...")
    
    state = AgentState()
    state.memory = MemoryServer(state)
    await state.memory.initialize()
    
    # Query for disabled servers
    query = "SELECT * FROM mcp_server WHERE enabled = false"
    disabled_servers = await state.memory._execute_query(query)
    
    if not disabled_servers or len(disabled_servers) == 0:
        print("✅ No disabled MCP servers found.")
        return
    
    print(f"Found {len(disabled_servers)} disabled server(s):")
    for server in disabled_servers:
        name = server.get('name', 'unknown')
        print(f"  - {name}")
    
    # Enable all disabled servers
    print("\nEnabling servers...")
    for server in disabled_servers:
        name = server.get('name', 'unknown')
        try:
            # Update the server to enabled
            update_query = f"UPDATE mcp_server SET enabled = true WHERE name = '{name}'"
            await state.memory._execute_query(update_query)
            print(f"  ✅ Enabled: {name}")
        except Exception as e:
            print(f"  ❌ Failed to enable {name}: {e}")
    
    # Verify
    print("\nVerifying enabled servers...")
    enabled_query = "SELECT name, enabled FROM mcp_server WHERE enabled = true"
    enabled_servers = await state.memory._execute_query(enabled_query)
    print(f"✅ {len(enabled_servers)} server(s) now enabled")
    
    # Show any still disabled
    still_disabled = await state.memory._execute_query("SELECT name FROM mcp_server WHERE enabled = false")
    if still_disabled and len(still_disabled) > 0:
        print(f"\n⚠️  {len(still_disabled)} server(s) still disabled:")
        for server in still_disabled:
            print(f"  - {server.get('name')}")

if __name__ == "__main__":
    try:
        asyncio.run(enable_all_mcp_servers())
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


