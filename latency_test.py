#!/usr/bin/env python3
"""
LATENCY ANALYSIS - Focused testing of response times
"""

import time
import requests
import json

def test_query(query, description):
    """Test a single query and return timing"""
    payload = {
        "messages": [{"role": "user", "content": query}],
        "model": "ollama:llama3.3:70b",
        "stream": False
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer antigravity_router_token_2025"
    }

    start_time = time.time()
    try:
        response = requests.post("http://127.0.0.1:5455/v1/chat/completions",
                               json=payload, headers=headers, timeout=30)
        end_time = time.time()

        success = response.status_code == 200
        response_time = end_time - start_time

        if success:
            data = response.json()
            content = data["choices"][0]["message"]["content"][:50] + "..."
        else:
            content = f"ERROR: {response.status_code}"

        return {
            "query": query,
            "description": description,
            "time": response_time,
            "success": success,
            "response": content
        }

    except Exception as e:
        return {
            "query": query,
            "description": description,
            "time": 30.0,
            "success": False,
            "response": f"EXCEPTION: {str(e)[:30]}"
        }

def main():
    print("🔬 LATENCY ANALYSIS TEST")
    print("=" * 40)

    # Test queries categorized by expected behavior
    test_cases = [
        # Conversational (should be fast)
        ("hello", "Simple greeting"),
        ("hi there", "Greeting with more words"),
        ("thank you", "Gratitude"),
        ("how are you", "Personal question"),

        # Time/Info queries (might load tools)
        ("what time is it", "Time query"),
        ("what day is it", "Date query"),

        # Commands (should trigger tools)
        ("list files", "File listing"),
        ("show directory", "Directory listing"),
    ]

    results = []

    for query, description in test_cases:
        print(f"\n🧪 Testing: {description}")
        result = test_query(query, description)
        results.append(result)

        status = "✅" if result["success"] else "❌"
        print(f"{status} {result['time']:.2f}s | {result['response']}")

    print("\n📊 SUMMARY:")
    print("-" * 40)

    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    if successful:
        times = [r["time"] for r in successful]
        print(f"Successful queries: {len(successful)}")
        print(f"Average response time: {sum(times)/len(times):.2f}s")
        print(f"Min time: {min(times):.2f}s")
        print(f"Max time: {max(times):.2f}s")

        print("\nFast queries (<2s):")
        fast = [r for r in successful if r["time"] < 2]
        for r in fast:
            print(f"  {r['time']:.2f}s - {r['query']}")

        print("\nSlow queries (≥5s):")
        slow = [r for r in successful if r["time"] >= 5]
        for r in slow:
            print(f"  {r['time']:.2f}s - {r['query']}")

    if failed:
        print(f"\nFailed queries: {len(failed)}")
        for r in failed:
            print(f"  {r['time']:.2f}s - {r['query']} | {r['response']}")

    # Save results
    with open("latency_analysis.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n📄 Results saved to latency_analysis.json")

if __name__ == "__main__":
    main()