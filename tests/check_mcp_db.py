
import asyncio
import os
from agent_runner.state import AgentState
from agent_runner.db_utils import run_query

async def check():
    state = AgentState()
    print("⏳ Initializing State (Connecting to DB)...")
    await state.initialize()
    
    print("🔍 Checking MCP Servers in Database...")
    try:
        results = await run_query(state, "SELECT name, enabled, command, args, env FROM mcp_server")
        if not results:
            print("❌ No MCP servers found in DB!")
            return

        found = False
        for row in results:
            name = row.get("name")
            enabled = row.get("enabled")
            if name == "project-memory":
                found = True
                print(f"✅ Found 'project-memory': Enabled={enabled}")
                print(f"   Command: {row.get('command')}")
                print(f"   Args: {row.get('args')}")
            else:
                print(f"   Server: {name} (Enabled={enabled})")
        
        if not found:
            print("❌ 'project-memory' is MISSING from Database.")
            
    except Exception as e:
        print(f"❌ DB Query Failed: {e}")

if __name__ == "__main__":
    asyncio.run(check())
