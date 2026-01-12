import asyncio
import os
import sys

# Add parent dir to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_runner.memory_server import MemoryServer
from agent_runner.state import AgentState

async def reset_mcp_db():
    print("Initializing State & Memory...")
    state = AgentState()
    # We need to init memory server manually
    server = MemoryServer(state)
    await server.initialize()
    
    print("Connected to SurrealDB.")
    
    # Check current count
    res = await server._execute_query("SELECT count() FROM mcp_server")
    print(f"Current MCP Server rows: {res}")
    
    # DELETE ALL
    print("Deleting all rows from 'mcp_server'...")
    await server._execute_query("DELETE FROM mcp_server")
    
    # Verify
    res = await server._execute_query("SELECT count() FROM mcp_server")
    print(f"Post-Delete count: {res}")
    
    print("MCP DB State Reset Complete. Restart Agent Runner to reload from mcp.yaml.")

if __name__ == "__main__":
    asyncio.run(reset_mcp_db())
