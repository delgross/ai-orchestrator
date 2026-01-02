import asyncio
import os
import sys

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_runner.memory_server import MemoryServer
from agent_runner.tools import registry
from agent_runner.state import AgentState

async def test_sources():
    print("--- Testing Source Authority ---")
    # Mock State
    state = AgentState()
    # Explicitly set root just in case env is weird
    state.agent_fs_root = "/Users/bee/Sync/Antigravity/ai"
    
    server = MemoryServer(state)
    await server.ensure_connected()
    await server.ensure_schema() # Force schema application
    
    # Store
    print("Storing source...")
    res_store = await server.store_source(
        url="https://archive.org",
        title="The Internet Archive",
        author="Brewster Kahle",
        reliability=1.0,
        summary="Universal access to all knowledge."
    )
    print(f"Store Result: {res_store}")
    
    # Raw Debug
    print("Raw Dump of Source Table:")
    raw = await server._execute_query("SELECT * FROM source")
    print(f"Raw: {raw}")

    # List
    print("Listing sources via tool...")
    res = await server.list_sources(limit=5)
    print(f"Result: {res}")
    
    found = False
    if res.get("ok"):
        for s in res["sources"]:
            if s["url"] == "https://archive.org":
                print("✅ Source found!")
                found = True
                break
    
    if not found:
        print("❌ Source NOT found.")

async def test_registry():
    print("\n--- Testing Recursive Registry ---")
    state = AgentState()
    state.agent_fs_root = "/Users/bee/Sync/Antigravity/ai"
    
    res = await registry.tool_registry_list(state)
    print(f"Registry List: {res}")
    
    if "antigravity/inventory.md" in res.get("files", []):
         print("✅ Nested file 'antigravity/inventory.md' found!")
    else:
         print("❌ Nested file NOT found.")

async def main():
    await test_sources()
    await test_registry()

if __name__ == "__main__":
    asyncio.run(main())
