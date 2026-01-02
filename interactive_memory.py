
import asyncio
import os
import sys
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from agent_runner.registry import ServiceRegistry
from agent_runner.state import AgentState
from agent_runner.memory_server import MemoryServer

# Standard logging setup (now that memory_server uses it)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("playground")

async def interactive_session():
    print("--- Initializing Memory System ---")
    state = AgentState()
    # Mock config for embedding model if needed, though defaults usually work
    state.config = {"ai": {"embedding_model": "mxbai-embed-large:latest"}}
    ServiceRegistry.register_state(state)
    
    memory = MemoryServer(state)
    await memory.initialize()
    ServiceRegistry.register_memory_server(memory)
    
    print("\n--- Memory Playground Ready ---")
    print("Type a query to search semantic memory.")
    print("Type 'exit' to quit.\n")

    while True:
        query = input("Query > ")
        if query.lower() in ["exit", "quit"]:
            break
        
        try:
            print(f"Searching for: '{query}'...")
            # Search
            results = await memory.semantic_search(query, limit=3)
            
            if not results or not results.get("ok"):
                print(f"Error: {results}")
                continue
                
            match_list = results.get("matches", [])
            print(f"\nFound {len(match_list)} matches:")
            for i, m in enumerate(match_list):
                # Calculate simple distance score representation
                dist = m.get('dist', 99)
                score = max(0, 1 - dist) # Approximate similarity
                
                print(f"[{i+1}] (Dist: {dist:.4f})")
                print(f"   Entity: {m.get('entity')}")
                print(f"   Fact:   {m.get('entity')} {m.get('relation')} {m.get('target')}")
                print(f"   Conf:   {m.get('confidence')}")
            print("-" * 40 + "\n")
            
        except Exception as e:
            logger.error(f"Search failed: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(interactive_session())
    except KeyboardInterrupt:
        print("\nGoodbye.")
