import asyncio
import logging
from agent_runner.state import AgentState

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fix_db")

async def main():
    print("Initializing AgentState...")
    state = AgentState()
    await state.initialize()
    
    if not hasattr(state, "memory") or not state.memory:
        print("ERROR: Memory not initialized in State.")
        return

    print("Querying mcp_server table...")
    try:
        servers = await state.memory._execute_query("SELECT * FROM mcp_server")
    except Exception as e:
        print(f"Query failed: {e}")
        return

    if not servers:
        print("No servers found in DB.")
        return

    print(f"Found {len(servers)} servers in DB:")
    found_openai = False
    for s in servers:
        print(f" - {s['name']} (enabled={s.get('enabled')})")
        if s['name'] == 'openai':
            found_openai = True

    if found_openai:
        print("\nDeleting 'openai' from DB...")
        await state.memory._execute_query("DELETE FROM mcp_server WHERE name = 'openai'")
        print("DELETE executed.")
        
        # Verify
        servers_after = await state.memory._execute_query("SELECT * FROM mcp_server WHERE name = 'openai'")
        if not servers_after:
            print("SUCCESS: 'openai' removed from DB.")
        else:
            print("WARNING: 'openai' still exists!")
    else:
        print("\n'openai' not found in DB. Nothing to do.")

if __name__ == "__main__":
    asyncio.run(main())
