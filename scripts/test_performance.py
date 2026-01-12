#!/usr/bin/env python3
"""
Performance Test for AI Orchestrator

Tests the latency improvements after optimizations.
"""

import asyncio
import time
import sys
import os
import requests

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_latency(endpoint: str, payload: dict, description: str) -> float:
    """Test latency of a single request."""
    start_time = time.time()

    try:
        response = requests.post(
            endpoint,
            json=payload,
            headers={"Authorization": "Bearer 9sYBjBLjAHKG8g8ZzzsUeBOvtzgQFHmX7oIeygdpzic"},
            timeout=30
        )
        response.raise_for_status()

        elapsed = time.time() - start_time
        print(f"  ✅ {description}: {elapsed:.2f}s")
        return elapsed

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"  ❌ {description}: {elapsed:.2f}s (error: {e})")
        return elapsed

async def main():
    """Run performance tests."""
    print("🚀 AI Orchestrator Performance Test")
    print("=" * 50)

    router_url = "http://127.0.0.1:5455"

    # Test 1: Simple Ollama model (fastest path)
    print("\n📊 Test 1: Simple Ollama Model")
    latencies = []
    for i in range(3):
        latency = test_latency(
            f"{router_url}/v1/chat/completions",
            {
                "model": "ollama:mistral:latest",
                "messages": [{"role": "user", "content": "Say hello"}],
                "stream": False
            },
            f"Ollama Request {i+1}"
        )
        latencies.append(latency)
        time.sleep(0.5)  # Brief pause between requests

    avg_latency = sum(latencies) / len(latencies)
    print(f"  📈 Average latency: {avg_latency:.2f}s")

    # Test 2: Agent model (simple query fast path)
    print("\n📊 Test 2: Agent Model (simple query fast path)")
    latencies = []
    for i in range(3):
        latency = test_latency(
            f"{router_url}/v1/chat/completions",
            {
                "model": "agent:mcp",
                "messages": [{"role": "user", "content": "What is 2+2?"}],
                "stream": False
            },
            f"Agent Simple Request {i+1}"
        )
        latencies.append(latency)
        time.sleep(0.5)  # Brief pause between requests

    avg_latency = sum(latencies) / len(latencies)
    print(f"  📈 Average latency: {avg_latency:.2f}s")

    # Test 3: Agent model (generic query - slower path)
    print("\n📊 Test 3: Agent Model (generic query)")
    latencies = []
    for i in range(2):  # Only 2 tests for slower path
        latency = test_latency(
            f"{router_url}/v1/chat/completions",
            {
                "model": "agent:mcp",
                "messages": [{"role": "user", "content": "Tell me about machine learning"}],
                "stream": False
            },
            f"Agent Generic Request {i+1}"
        )
        latencies.append(latency)
        time.sleep(1.0)  # Longer pause for slower requests

    avg_latency = sum(latencies) / len(latencies)
    print(f"  📈 Average latency: {avg_latency:.2f}s")

    # Performance targets
    print("\n🎯 Performance Targets:")
    print("  Ollama model: < 1.0 seconds")
    print("  Agent model:  < 3.0 seconds")
    print("  Cache clearing: Disabled by default")

    print("\n✅ Performance test completed!")

if __name__ == "__main__":
    asyncio.run(main())