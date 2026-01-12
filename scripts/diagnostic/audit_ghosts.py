
import asyncio
import os
from agent_runner.state import AgentState
from agent_runner.memory_server import MemoryServer

async def audit():
    state = AgentState()
    # Mock config for connection
    state.config = {
        "surreal": {
            "url": "http://127.0.0.1:8000",
            "ns": "orchestrator",
            "db": "memory",
            "user": "root",
            "pass": "root"
        }
    }
    mem = MemoryServer(state) # Minimal init
    
    print("--- MCP SERVERS IN DB ---")
    res = await mem._execute_query("SELECT * FROM mcp_server")
    for r in res:
        print(f"Name: {r['name']} | Enabled: {r.get('enabled')}")
        
        if r['name'] == 'xai:grok-3':
            print("!!! FOUND GHOST MODEL AS SERVER !!!")
            # Delete it
            await mem._execute_query("DELETE mcp_server WHERE name = 'xai:grok-3'")
            print(">>> DELETED GHOST SERVER <<<")

if __name__ == "__main__":
    asyncio.run(audit())
