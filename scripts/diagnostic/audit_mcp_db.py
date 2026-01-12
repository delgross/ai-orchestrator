import asyncio
import logging
from agent_runner.state import AgentState

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("audit_db")

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
    target_found = False
    for s in servers:
        name = s['name']
        print(f" - '{name}' (enabled={s.get('enabled')})")
        
        # Check for the ghost or partial matches
        if "grok-2" in name:
            target_found = True
            print(f"   -> FOUND GHOST: {name}")

    if target_found:
        print("\nDeleting Ghost Entries...")
        # Delete anything matching the pattern
        await state.memory._execute_query("DELETE FROM mcp_server WHERE name CONTAINS 'grok-2'")
        print("DELETE executed.")
        
        # Verify
        servers_after = await state.memory._execute_query("SELECT * FROM mcp_server WHERE name CONTAINS 'grok-2'")
        if not servers_after:
            print("SUCCESS: Ghosts removed from DB.")
        else:
            print("WARNING: Ghosts still exist!")
    else:
        print("\nNo 'grok-2' ghosts found in DB.")

if __name__ == "__main__":
    asyncio.run(main())
