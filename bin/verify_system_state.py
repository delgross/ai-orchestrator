import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_runner.memory_server import MemoryServer
from agent_runner.state import AgentState

async def verify_system_state():
    print("--- Verifying System State Ingestion ---")
    state = AgentState()
    server = MemoryServer(state)
    await server.ensure_connected()
    
    # 1. Check Config
    print("\n--- CONFIG STATE ---")
    res = await server._execute_query("SELECT * FROM config_state LIMIT 5")
    for r in res:
        print(f"Key: {r.get('key')} | Source: {r.get('source')} | Val: {r.get('value')[:20]}...")
        
    # 2. Check System
    print("\n--- SYSTEM STATE ---")
    res = await server._execute_query("SELECT * FROM system_state")
    for r in res:
        print(f"Item: {r.get('item')} | Details: {str(r.get('details'))[:50]}...")

    if len(res) > 0:
        print("\n✅ System State Ingested Successfully!")
    else:
        print("\n❌ System State Empty.")

if __name__ == "__main__":
    asyncio.run(verify_system_state())
