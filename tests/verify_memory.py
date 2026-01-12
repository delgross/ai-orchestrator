
import asyncio
import os
from agent_runner.state import AgentState
from agent_runner.tools.mcp import tool_mcp_proxy

async def verify():
    print("⏳ Initializing AgentState...")
    state = AgentState()
    await state.initialize()
    
    server_name = "project-memory"
    print(f"⏳ Loading MCP Servers for {server_name}...")
    # Manual Load because AgentState.initialize() doesn't load MCP table automatically
    from agent_runner.db_utils import run_query
    res = await run_query(state, "SELECT * FROM mcp_server WHERE enabled = true")
    if res:
        for row in res:
             # Normalize: ConfigManager usually does this
             if "command" in row and "cmd" not in row:
                 c = [row["command"]]
                 if row.get("args"):
                     c.extend(row["args"])
                 row["cmd"] = c
             state.mcp_servers[row['name']] = row
             
    tool_name = "semantic_search"
    args = {"query": "latency optimization", "limit": 1}
    
    print(f"🔬 Testing '{server_name}'...")
    try:
        # Since we just added it, it might need 'warming up' (process launch)
        # tool_mcp_proxy handles this via ensuring stdio process exists
        result = await tool_mcp_proxy(state, server_name, tool_name, args, bypass_circuit_breaker=True)
        print("✅ SUCCESS! Memory Server Responded:")
        print(f"   Result: {str(result)[:200]}...")
    except Exception as e:
        print(f"❌ FAILURE: {e}")

if __name__ == "__main__":
    asyncio.run(verify())
