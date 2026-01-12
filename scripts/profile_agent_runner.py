#!/usr/bin/env python3
"""
Detailed profiling of agent runner components to identify bottlenecks.
"""

import asyncio
import time
import sys
import json
from datetime import datetime

sys.path.insert(0, '.')

async def profile_memory_retrieval():
    """Profile memory retrieval time."""
    try:
        from agent_runner.memory_server import MemoryServer
        from agent_runner.state import AgentState
        
        # Create minimal state
        class MockState:
            def __init__(self):
                self.memory = None
        
        state = MockState()
        memory = MemoryServer(state)
        
        start = time.time()
        # This would normally retrieve relevant memories
        result = await memory.semantic_search("test query", 5)
        elapsed = time.time() - start
        
        return {"component": "Memory Retrieval", "duration": elapsed, "success": True}
    except Exception as e:
        return {"component": "Memory Retrieval", "duration": 0, "success": False, "error": str(e)}

async def profile_prompt_generation():
    """Profile prompt generation time."""
    try:
        from agent_runner.engine import AgentEngine
        from agent_runner.state import AgentState
        
        # Create minimal state for testing
        class MockState:
            def __init__(self):
                self.gateway_base = "http://127.0.0.1:5455"
                self.agent_runner_url = "http://127.0.0.1:5460"
                self.system_event_queue = []
                self.memory = None
        
        state = MockState()
        engine = AgentEngine(state)
        
        start = time.time()
        prompt = await engine.get_system_prompt()
        elapsed = time.time() - start
        
        return {"component": "Prompt Generation", "duration": elapsed, "success": True, "prompt_length": len(prompt)}
    except Exception as e:
        return {"component": "Prompt Generation", "duration": 0, "success": False, "error": str(e)}

async def profile_tool_discovery():
    """Profile tool discovery time."""
    try:
        from agent_runner.executor import ToolExecutor
        from agent_runner.state import AgentState
        
        class MockState:
            def __init__(self):
                self.gateway_base = "http://127.0.0.1:5455"
                self.agent_runner_url = "http://127.0.0.1:5460"
                self.system_event_queue = []
                self.memory = None
        
        state = MockState()
        executor = ToolExecutor(state)
        
        start = time.time()
        tools = await executor.get_all_tools()
        elapsed = time.time() - start
        
        return {"component": "Tool Discovery", "duration": elapsed, "success": True, "tool_count": len(tools)}
    except Exception as e:
        return {"component": "Tool Discovery", "duration": 0, "success": False, "error": str(e)}

async def main():
    print("🔬 Agent Runner Component Profiling")
    print("=" * 40)
    
    results = []
    results.append(await profile_memory_retrieval())
    results.append(await profile_prompt_generation()) 
    results.append(await profile_tool_discovery())
    
    print("\n📊 COMPONENT PROFILING RESULTS")
    print("-" * 35)
    
    for result in results:
        status = "✅" if result['success'] else "❌"
        duration = ".2f"
        component = result['component'].ljust(20)
        extra = ""
        if 'tool_count' in result:
            extra = f" ({result['tool_count']} tools)"
        elif 'prompt_length' in result:
            extra = f" ({result['prompt_length']} chars)"
            
        print(f"{status} {component} {duration}{extra}")
        
        if not result['success']:
            print(f"    Error: {result.get('error', 'Unknown')}")
    
    # Identify bottlenecks
    slow_components = [r for r in results if r['success'] and r['duration'] > 1.0]
    if slow_components:
        print("\n🐌 Potentially slow components (>1s):")
        for comp in slow_components:
            print(f"  - {comp['component']}: {comp['duration']:.2f}s")
    
    # Save results
    output_file = f"agent_runner_profile_{int(time.time())}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")

if __name__ == "__main__":
    asyncio.run(main())
