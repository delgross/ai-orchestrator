import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_runner.memory_server import MemoryServer
from agent_runner.state import AgentState

async def verify_storage():
    print("--- Verifying Episode Storage ---")
    state = AgentState()
    state.agent_fs_root = "/Users/bee/Sync/Antigravity/ai"
    
    server = MemoryServer(state)
    await server.ensure_connected()
    
    # Fake Episode
    req_id = "test-probe-delta"
    msgs = [
        {"role": "user", "content": "This is a direct persistence test."},
        {"role": "assistant", "content": "Acknowledged."}
    ]
    
    print(f"Storing episode {req_id}...")
    res = await server.store_episode(req_id, msgs)
    print(f"Store Result: {res}")
    
    # Query back
    print("Querying verification...")
    q = "SELECT * FROM episode WHERE request_id = $rid"
    verify = await server._execute_query(q, {"rid": req_id})
    print(f"Verification: {verify}")
    
    if verify and len(verify) > 0:
        print("✅ Episode successfully persisted!")
    else:
        print("❌ Episode NOT found.")

if __name__ == "__main__":
    asyncio.run(verify_storage())
