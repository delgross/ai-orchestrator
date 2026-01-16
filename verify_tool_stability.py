
import asyncio
import json
import hashlib
from agent_runner.executor import ToolExecutor
from agent_runner.state import AgentState

async def verify_stability():
    state = AgentState()
    await state.initialize()
    executor = ToolExecutor(state)
    
    hashes = []
    
    print("🔄 Generating Tool Definitions 5 times...")
    for i in range(5):
        # Force re-discovery/deduplication if possible, or just re-sort
        # We can't easily force discovery without mocking, but we can check the sorting output
        tools = await executor.get_all_tools(messages=[])
        
        # Serialize with strict sorting to check if the OBJECT itself is stable
        # If the keys inside "properties" are random, this dump might vary if sort_keys=False
        # But we want to simulate what we send to Ollama.
        # Ollama receives the list of dicts.
        
        # We dump with sort_keys=True to normalize the JSON for comparison.
        # If the *content* varies (e.g. dynamic description), the hash will change.
        dump = json.dumps(tools, sort_keys=True)
        h = hashlib.md5(dump.encode()).hexdigest()
        hashes.append(h)
        print(f"Run {i+1}: Tool Count={len(tools)} Hash={h}")
        
    if len(set(hashes)) == 1:
        print("✅ STABLE: Tool definitions are deterministic.")
    else:
        print("❌ UNSTABLE: Tool definitions vary between runs!")
        
if __name__ == "__main__":
    asyncio.run(verify_stability())
