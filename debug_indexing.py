import asyncio
import os
import sys
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("debug_indexing")

# Add project root
sys.path.append(os.getcwd())

from agent_runner.state import AgentState
from agent_runner.memory_server import MemoryServer
from agent_runner.executor import ToolExecutor

async def main():
    print("Initializing State...")
    state = AgentState()
    # Mocking config load
    state.config = {"security": {}}
    
    print("Initializing Memory...")
    state.memory = MemoryServer(state)
    await state.memory.initialize()
    
    print("Initializing Executor...")
    executor = ToolExecutor(state)
    
    # Check Internal Tools
    internal_tools = executor.tool_definitions
    print(f"Internal Tools Count: {len(internal_tools)}")
    
    # Check if 'get_component_map' or 'get_llm_roles' is in there
    found = False
    for t in internal_tools:
        name = t.get("function", {}).get("name")
        if name in ["get_component_map", "get_llm_roles"]:
            print(f"FOUND Internal Tool: {name}")
            found = True
            
    if not found:
        print("CRITICAL: Introspection tools NOT found in executor.tool_definitions!")
    
    # Check DB Content
    print("Querying Vector Store (tool_definition)...")
    res = await state.memory._execute_query("SELECT name, description, requires_admin, vector::length(embedding) as dim FROM tool_definition")
    
    print(f"DB Row Count: {len(res) if res else 0}")
    if res:
        for row in res:
            if row['name'] in ["get_component_map", "get_llm_roles"]:
                print(f"DB Entry: {row['name']} | Dim: {row['dim']}")
                
    # Test Semantic Search
    print("\nTesting Search 'list internal llms'...")
    term = "list internal llms"
    emb = await state.memory.get_embedding(term)
    q = "SELECT name, vector::similarity::cosine(embedding, $emb) as score FROM tool_definition ORDER BY score DESC LIMIT 3"
    search_res = await state.memory._execute_query(q, {"emb": emb})
    print("Search Results:")
    for r in search_res:
        print(f"- {r['name']} (Score: {r['score']:.4f})")

if __name__ == "__main__":
    asyncio.run(main())
