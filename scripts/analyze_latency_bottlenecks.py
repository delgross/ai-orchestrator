#!/usr/bin/env python3
"""
Analyze the top 5 latency bottlenecks in the AI system.
"""

import asyncio
import time
import sys
import json
from typing import Dict, Any, List
import httpx

sys.path.insert(0, '.')

async def measure_component_latency(name: str, operation) -> Dict[str, Any]:
    """Measure latency of a specific operation."""
    start_time = time.time()
    success = False
    error = None
    
    try:
        result = await operation()
        success = True
    except Exception as e:
        error = str(e)
        result = None
    
    elapsed = time.time() - start_time
    
    return {
        "component": name,
        "latency": elapsed,
        "success": success,
        "error": error,
        "result": result
    }

async def test_direct_ollama():
    """Test direct Ollama call."""
    async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
        response = await client.post(
            "http://127.0.0.1:5455/v1/chat/completions",
            json={
                "model": "ollama:qwen2.5:7b-instruct",
                "messages": [{"role": "user", "content": "Hello"}],
                "stream": False,
                "max_tokens": 10
            },
            headers={"Authorization": "Bearer 9sYBjBLjAHKG8g8ZzzsUeBOvtzgQFHmX7oIeygdpzic"}
        )
        response.raise_for_status()
        return response.json()

async def test_router_analyzer():
    """Test router analyzer component."""
    from agent_runner.router_analyzer import analyze_query
    import httpx
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as http_client:
        return await analyze_query(
            query="List files in directory",
            messages=[{"role": "user", "content": "List files in directory"}],
            gateway_base="http://127.0.0.1:5455",
            http_client=http_client,
            available_tools=[{"function": {"name": "list_dir"}}],
            available_models=["ollama:qwen2.5:7b-instruct"]
        )

async def test_tool_discovery():
    """Test tool discovery component."""
    from agent_runner.executor import ToolExecutor
    from agent_runner.state import AgentState
    
    class MockState:
        def __init__(self):
            self.gateway_base = "http://127.0.0.1:5455"
            self.agent_runner_url = "http://127.0.0.1:5460"
    
    state = MockState()
    executor = ToolExecutor(state)
    return await executor.get_all_tools()

async def test_memory_retrieval():
    """Test memory retrieval component."""
    from agent_runner.memory_server import MemoryServer
    from agent_runner.state import AgentState
    
    class MockState:
        def __init__(self):
            self.memory = None
    
    state = MockState()
    memory = MemoryServer(state)
    return await memory.semantic_search("test query", 5)

async def test_agent_full_pipeline():
    """Test full agent pipeline."""
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
        response = await client.post(
            "http://127.0.0.1:5460/v1/chat/completions",
            json={
                "model": "agent_runner",
                "messages": [{"role": "user", "content": "Hello"}],
                "stream": False,
                "max_tokens": 50
            }
        )
        response.raise_for_status()
        return response.json()

async def main():
    print("🔬 AI System Latency Bottleneck Analysis")
    print("=" * 50)
    
    # Test each component
    tests = [
        ("Direct Ollama Call", test_direct_ollama),
        ("Router Analyzer", test_router_analyzer),
        ("Tool Discovery", test_tool_discovery),
        ("Memory Retrieval", test_memory_retrieval),
        ("Full Agent Pipeline", test_agent_full_pipeline)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"Testing {name}...", end="", flush=True)
        result = await measure_component_latency(name, test_func)
        status = "✅" if result["success"] else "❌"
        latency = ".2f" if result["success"] else ".2f"
        print(f" {status} ({latency})")
        results.append(result)
    
    print("\n📊 LATENCY BREAKDOWN")
    print("-" * 40)
    
    # Sort by latency
    successful_results = [r for r in results if r["success"]]
    failed_results = [r for r in results if not r["success"]]
    
    successful_results.sort(key=lambda x: x["latency"], reverse=True)
    
    total_latency = sum(r["latency"] for r in successful_results)
    
    for result in successful_results:
        latency = result["latency"]
        percentage = (latency / total_latency) * 100 if total_latency > 0 else 0
        print(".2f")
    
    print("\n❌ FAILED COMPONENTS")
    print("-" * 20)
    for result in failed_results:
        print(f"• {result['component']}: {result['error']}")
    
    print("\n🎯 TOP 5 LATENCY BOTTLENECKS")
    print("-" * 30)
    
    # Analyze bottlenecks
    bottlenecks = []
    
    # 1. Full Agent Pipeline bottleneck
    agent_result = next((r for r in results if r["component"] == "Full Agent Pipeline"), None)
    if agent_result and agent_result["success"]:
        ollama_result = next((r for r in results if r["component"] == "Direct Ollama Call"), None)
        if ollama_result and ollama_result["success"]:
            agent_overhead = agent_result["latency"] - ollama_result["latency"]
            bottlenecks.append({
                "rank": 1,
                "bottleneck": "Agent Processing Overhead",
                "latency": agent_overhead,
                "percentage": (agent_overhead / agent_result["latency"]) * 100,
                "description": "Non-LLM processing time in agent pipeline"
            })
    
    # 2. Router Analyzer bottleneck
    router_result = next((r for r in results if r["component"] == "Router Analyzer"), None)
    if router_result and router_result["success"]:
        bottlenecks.append({
            "rank": 2,
            "bottleneck": "Router Analyzer LLM Call",
            "latency": router_result["latency"],
            "percentage": (router_result["latency"] / total_latency) * 100,
            "description": "Semantic tool filtering analysis"
        })
    
    # 3. Tool Discovery bottleneck
    tool_result = next((r for r in results if r["component"] == "Tool Discovery"), None)
    if tool_result and tool_result["success"]:
        bottlenecks.append({
            "rank": 3,
            "bottleneck": "Tool Discovery & Loading",
            "latency": tool_result["latency"],
            "percentage": (tool_result["latency"] / total_latency) * 100,
            "description": "Loading and caching MCP tools"
        })
    
    # 4. Memory Retrieval bottleneck
    memory_result = next((r for r in results if r["component"] == "Memory Retrieval"), None)
    if memory_result and memory_result["success"]:
        bottlenecks.append({
            "rank": 4,
            "bottleneck": "Memory Retrieval",
            "latency": memory_result["latency"],
            "percentage": (memory_result["latency"] / total_latency) * 100,
            "description": "Querying relevant conversation history"
        })
    
    # 5. LLM Inference bottleneck
    ollama_result = next((r for r in results if r["component"] == "Direct Ollama Call"), None)
    if ollama_result and ollama_result["success"]:
        bottlenecks.append({
            "rank": 5,
            "bottleneck": "LLM Inference Time",
            "latency": ollama_result["latency"],
            "percentage": (ollama_result["latency"] / total_latency) * 100,
            "description": "Raw model generation time"
        })
    
    # Sort bottlenecks by latency impact
    bottlenecks.sort(key=lambda x: x["latency"], reverse=True)
    
    for bottleneck in bottlenecks:
        print(f"{bottleneck['rank']}. {bottleneck['bottleneck']}")
        print(".2f")
        print(f"   {bottleneck['description']}")
        print()
    
    # Save detailed results
    output_file = f"latency_bottlenecks_{int(time.time())}.json"
    with open(output_file, 'w') as f:
        json.dump({
            "component_breakdown": results,
            "bottlenecks": bottlenecks,
            "total_latency": total_latency
        }, f, indent=2, default=str)
    
    print(f"💾 Detailed results saved to: {output_file}")

if __name__ == "__main__":
    asyncio.run(main())
