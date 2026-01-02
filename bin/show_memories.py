import asyncio
import os
import sys

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_runner.memory_server import MemoryServer
from agent_runner.state import AgentState

async def show_memories():
    print("--- Reading Short-Term Memory ---")
    state = AgentState()
    state.agent_fs_root = "/Users/bee/Sync/Antigravity/ai" # Env var usually handles this
    
    server = MemoryServer(state)
    await server.ensure_connected()
    
    # Query Episodes
    # Flatten structure for readability
    q = "SELECT messages, timestamp FROM episode ORDER BY timestamp DESC LIMIT 3"
    res = await server._execute_query(q)
    
    if res is None:
        print("Failed to query.")
        return

    episodes = res # Already unwrapped by fix
    print(f"Found {len(episodes)} recent episodes:\n")
    
    for ep in episodes:
        ts = ep.get("timestamp", "unknown")
        msgs = ep.get("messages", [])
        print(f"[TIMESTAMP: {ts}]")
        for m in msgs:
            role = m.get("role", "?")
            content = m.get("content", "")[:100] + "..." # Truncate
            print(f"  {role.upper()}: {content}")
        print("-" * 40)

if __name__ == "__main__":
    asyncio.run(show_memories())
