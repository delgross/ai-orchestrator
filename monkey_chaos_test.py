#!/usr/bin/env python3
"""
MONKEY CHAOS LATENCY TEST SUITE
Comprehensive testing of chat interface latency with various query types
"""

import time
import json
import requests
import statistics
import sys
from typing import Dict, List, Tuple
from datetime import datetime

class MonkeyChaosTester:
    def __init__(self, base_url: str = "http://127.0.0.1:5455", auth_token: str = "antigravity_router_token_2025"):
        self.base_url = base_url
        self.auth_token = auth_token
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_token}"
        }
        self.results = []

    def send_query(self, query: str, model: str = "ollama:llama3.3:70b", description: str = "") -> Dict:
        """Send a single query and measure response time"""
        payload = {
            "messages": [{"role": "user", "content": query}],
            "model": model,
            "stream": False
        }

        start_time = time.time()
        try:
            response = requests.post(f"{self.base_url}/v1/chat/completions", json=payload, headers=self.headers, timeout=60)
            end_time = time.time()

            result = {
                "query": query[:50] + "..." if len(query) > 50 else query,
                "description": description,
                "response_time": end_time - start_time,
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "response_length": len(response.text) if response.status_code == 200 else 0,
                "timestamp": datetime.now().isoformat()
            }

            if response.status_code == 200:
                try:
                    data = response.json()
                    result["model"] = data.get("model", "")
                    result["usage"] = data.get("usage", {})
                    result["finish_reason"] = data["choices"][0]["message"].get("finish_reason", "") if data.get("choices") else ""
                except:
                    result["error"] = "Failed to parse response JSON"
            else:
                result["error"] = response.text[:200]

        except requests.exceptions.Timeout:
            result = {
                "query": query[:50] + "..." if len(query) > 50 else query,
                "description": description,
                "response_time": 60.0,
                "status_code": 0,
                "success": False,
                "error": "TIMEOUT",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            result = {
                "query": query[:50] + "..." if len(query) > 50 else query,
                "description": description,
                "response_time": time.time() - start_time,
                "status_code": 0,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

        self.results.append(result)
        return result

    def run_test_suite(self):
        """Run comprehensive test suite"""
        print("🧪 MONKEY CHAOS LATENCY TEST SUITE")
        print("=" * 50)

        # Test Categories
        test_categories = {
            "SIMPLE_CONVERSATIONAL": [
                ("hello", "Simple greeting"),
                ("hi there", "Simple greeting 2"),
                ("how are you", "Personal question"),
                ("thank you", "Gratitude"),
                ("goodbye", "Farewell"),
                ("yes", "Affirmation"),
                ("no", "Negation"),
                ("ok", "Acknowledgment"),
                ("sure", "Agreement"),
                ("cool", "Casual positive"),
            ],

            "TIME_LOCATION": [
                ("what time is it", "Time query"),
                ("what's the current time", "Time query 2"),
                ("where am I", "Location query"),
                ("what's my location", "Location query 2"),
                ("what day is it", "Date query"),
                ("what's today's date", "Date query 2"),
            ],

            "COMPLEX_TECHNICAL": [
                ("explain how machine learning works", "ML explanation"),
                ("write a python function to sort a list", "Code generation"),
                ("what are the benefits of using docker", "Docker explanation"),
                ("explain quantum computing", "Quantum computing"),
                ("how does blockchain work", "Blockchain explanation"),
            ],

            "TOOL_TRIGGERING": [
                ("run ls command", "Terminal command"),
                ("execute pwd", "Terminal command 2"),
                ("list files in current directory", "File listing"),
                ("show me the system status", "System status"),
                ("check memory usage", "Memory check"),
            ],

            "EDGE_CASES": [
                ("", "Empty query"),
                ("a" * 1000, "Very long query"),
                ("?" * 50, "Question marks"),
                ("!@#$%^&*()", "Special characters"),
                ("a" * 10 + " " + "b" * 10, "Repeated chars"),
                ("\n\n\nhello\n\n\n", "Newlines"),
                ("<script>alert('xss')</script>", "Potential XSS"),
                ("SELECT * FROM users", "SQL injection attempt"),
                ("../../../etc/passwd", "Path traversal"),
            ],

            "REPEATED_QUERIES": [
                ("hello world", "Repeated 1"),
                ("hello world", "Repeated 2"),
                ("hello world", "Repeated 3"),
                ("what time is it", "Time repeated 1"),
                ("what time is it", "Time repeated 2"),
            ]
        }

        total_start_time = time.time()

        for category, queries in test_categories.items():
            print(f"\n🔬 Testing {category}")
            print("-" * 30)

            for query, description in queries:
                result = self.send_query(query, description=description)

                status_icon = "✅" if result["success"] else "❌"
                time_display = f"{result['response_time']:.2f}s"

                if result["success"]:
                    print(f"  {status_icon} {time_display} | {description}")
                else:
                    print(f"  {status_icon} {time_display} | {description} | ERROR: {result.get('error', 'Unknown')}")

                # Small delay between requests to avoid overwhelming
                time.sleep(0.5)

        total_time = time.time() - total_start_time
        self.analyze_results(total_time)

    def analyze_results(self, total_time: float):
        """Analyze test results"""
        print(f"\n📊 MONKEY CHAOS ANALYSIS")
        print("=" * 50)
        print(f"Total test time: {total_time:.2f}s")

        if not self.results:
            print("No results to analyze")
            return

        successful = [r for r in self.results if r["success"]]
        failed = [r for r in self.results if not r["success"]]

        print(f"Total queries: {len(self.results)}")
        print(f"Successful: {len(successful)} ({len(successful)/len(self.results)*100:.1f}%)")
        print(f"Failed: {len(failed)} ({len(failed)/len(self.results)*100:.1f}%)")

        if successful:
            response_times = [r["response_time"] for r in successful]
            print("\nResponse Time Statistics:")
            print(f"  Mean: {statistics.mean(response_times):.2f}s")
            print(f"  Median: {statistics.median(response_times):.2f}s")
            print(f"  Min: {min(response_times):.2f}s")
            print(f"  Max: {max(response_times):.2f}s")
            print(f"  Std Dev: {statistics.stdev(response_times):.2f}s")

            # Categorize by speed
            fast = len([r for r in response_times if r < 2])
            medium = len([r for r in response_times if 2 <= r < 10])
            slow = len([r for r in response_times if r >= 10])

            print("\nSpeed Distribution:")
            print(f"  Fast (<2s): {fast} queries")
            print(f"  Medium (2-10s): {medium} queries")
            print(f"  Slow (≥10s): {slow} queries")

        # Show slowest queries
        if successful:
            slowest = sorted(successful, key=lambda x: x["response_time"], reverse=True)[:5]
            print("\n🐌 5 Slowest Queries:")
            for i, result in enumerate(slowest, 1):
                print(f"  {i}. {result['response_time']:.2f}s - {result['query']}")

        # Show failed queries
        if failed:
            print("\n❌ Failed Queries:")
            for result in failed:
                print(f"  {result['response_time']:.2f}s - {result['query']} | {result.get('error', 'Unknown')}")

        # Save detailed results
        with open("monkey_chaos_results.json", "w") as f:
            json.dump({
                "summary": {
                    "total_time": total_time,
                    "total_queries": len(self.results),
                    "successful": len(successful),
                    "failed": len(failed),
                    "avg_response_time": statistics.mean([r["response_time"] for r in successful]) if successful else 0
                },
                "results": self.results
            }, f, indent=2)

        print(f"\n📄 Detailed results saved to monkey_chaos_results.json")

def main():
    tester = MonkeyChaosTester()

    try:
        tester.run_test_suite()
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        tester.analyze_results(time.time() - time.time())  # Placeholder
    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()