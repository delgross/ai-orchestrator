#!/usr/bin/env python3
"""
Comprehensive latency profiling for AI system components.
Identifies bottlenecks in the request processing pipeline.
"""

import asyncio
import time
import sys
import json
from typing import Dict, Any, List
from datetime import datetime

# Add project root to path
sys.path.insert(0, '.')

async def time_function(func, *args, **kwargs):
    """Time an async function call."""
    start = time.time()
    result = await func(*args, **kwargs)
    elapsed = time.time() - start
    return result, elapsed

async def profile_component(name: str, func, *args, **kwargs) -> Dict[str, Any]:
    """Profile a single component."""
    print(f"🔍 Profiling {name}...", end="", flush=True)
    try:
        result, elapsed = await time_function(func, *args, **kwargs)
        print(f" ({elapsed:.2f}s)")
        return {
            "component": name,
            "duration": elapsed,
            "success": True,
            "result": result if len(str(result)) < 100 else f"{str(result)[:100]}..."
        }
    except Exception as e:
        print(" ❌")
        return {
            "component": name,
            "duration": 0,
            "success": False,
            "error": str(e)
        }

async def profile_router_analyzer():
    """Profile router analyzer performance."""
    from agent_runner.router_analyzer import analyze_query
    import httpx
    
    messages = [{'role': 'user', 'content': 'List all files in the current directory and analyze their contents'}]
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as http_client:
        return await profile_component(
            "Router Analyzer",
            analyze_query,
            query='List all files in the current directory and analyze their contents',
            messages=messages,
            gateway_base='http://127.0.0.1:5455',
            http_client=http_client,
            available_tools=[
                {'function': {'name': 'list_dir', 'description': 'List files in a directory'}},
                {'function': {'name': 'read_file', 'description': 'Read file contents'}},
                {'function': {'name': 'run_command', 'description': 'Execute shell commands'}}
            ],
            available_models=['ollama:qwen2.5:7b-instruct']
        )

async def profile_agent_runner_simple():
    """Profile simple agent runner query."""
    import httpx
    
    payload = {
        "model": "agent_runner",
        "messages": [{"role": "user", "content": "Hello"}],
        "stream": False,
        "max_tokens": 50
    }
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
        async def make_request():
            resp = await client.post(
                "http://127.0.0.1:5460/v1/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            resp.raise_for_status()
            return resp.json()
        
        return await profile_component("Agent Runner (Simple)", make_request)

async def profile_agent_runner_complex():
    """Profile complex agent runner query."""
    import httpx
    
    payload = {
        "model": "agent_runner", 
        "messages": [{"role": "user", "content": "List all files in the current directory and tell me what each one contains"}],
        "stream": False,
        "max_tokens": 200
    }
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
        async def make_request():
            resp = await client.post(
                "http://127.0.0.1:5460/v1/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            resp.raise_for_status()
            return resp.json()
        
        return await profile_component("Agent Runner (Complex)", make_request)

async def profile_ollama_direct():
    """Profile direct Ollama call."""
    import httpx
    
    payload = {
        "model": "qwen2.5:7b-instruct",
        "messages": [{"role": "user", "content": "Hello, respond with exactly: DIRECT"}],
        "stream": False,
        "max_tokens": 10
    }
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
        async def make_request():
            resp = await client.post(
                "http://127.0.0.1:5455/v1/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            resp.raise_for_status()
            return resp.json()
        
        return await profile_component("Direct Ollama Call", make_request)

async def main():
    print("🚀 AI System Latency Profiling")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    results = []
    
    # Profile individual components
    results.append(await profile_ollama_direct())
    results.append(await profile_router_analyzer())
    results.append(await profile_agent_runner_simple())
    results.append(await profile_agent_runner_complex())
    
    print("\n📊 PROFILING RESULTS")
    print("=" * 50)
    
    # Sort by duration
    results.sort(key=lambda x: x['duration'], reverse=True)
    
    total_time = sum(r['duration'] for r in results if r['success'])
    
    for result in results:
        status = "✅" if result['success'] else "❌"
        duration = ".2f"
        component = result['component'].ljust(25)
        print(f"{status} {component} {duration}")
        
        if not result['success']:
            print(f"    Error: {result.get('error', 'Unknown')}")
    
    print(f"\n⏱️  Total profiled time: {total_time:.2f}s")
    
    # Identify bottlenecks
    print("\n🔍 BOTTLENECK ANALYSIS")
    print("-" * 30)
    
    slow_components = [r for r in results if r['success'] and r['duration'] > 10.0]
    if slow_components:
        print("🐌 Slow components (>10s):")
        for comp in slow_components:
            pct = (comp['duration'] / total_time) * 100
            print(f"  - {comp['component']}: {comp['duration']:.2f}s ({pct:.1f}% of total)")
    else:
        print("✅ No major bottlenecks identified (>10s)")
    
    # Save results
    output_file = f"latency_profile_{int(time.time())}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: {output_file}")

if __name__ == "__main__":
    asyncio.run(main())
