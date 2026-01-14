#!/usr/bin/env python3
"""
Test router-level hallucination detection.
"""

import asyncio
import json
import httpx
import time

async def test_hallucination_detection():
    """Test hallucination detection at router level."""

    test_cases = [
        {
            "name": "Normal response",
            "query": "What is the capital of France?",
            "expected_normal": True
        },
        {
            "name": "Hallucinated MCP instructions",
            "query": "How do I add an MCP server?",
            "expected_hallucination": True
        },
        {
            "name": "Technical question",
            "query": "How do I install Python packages?",
            "expected_normal": True
        }
    ]

    async with httpx.AsyncClient(timeout=30.0) as client:
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🧪 Test {i}: {test_case['name']}")
            print(f"Query: {test_case['query']}")

            # Make request to router (you'll need to add authentication)
            try:
                # Note: This will fail without proper authentication
                # For testing, you might need to modify the router to allow unauthenticated requests
                # or provide the proper bearer token
                payload = {
                    "messages": [{"role": "user", "content": test_case["query"]}],
                    "model": "agent:mcp",
                    "stream": False
                }

                response = await client.post(
                    "http://127.0.0.1:5455/v1/chat/completions",
                    json=payload,
                    headers={"Authorization": "Bearer test-token"}  # You'll need proper auth
                )

                if response.status_code == 401:
                    print("❌ Authentication required - cannot test router directly")
                    continue

                result = response.json()
                choice = result.get("choices", [{}])[0]
                message = choice.get("message", {})

                # Check for hallucination metadata
                hallucination_check = message.get("hallucination_check", {})
                detected = hallucination_check.get("detected", False)
                severity = hallucination_check.get("severity", "low")
                confidence = hallucination_check.get("confidence", 0.0)

                print(f"Hallucination detected: {detected}")
                print(f"Severity: {severity}")
                print(f"Confidence: {confidence:.2f}")

                content = message.get("content", "")
                if len(content) > 100:
                    print(f"Response preview: {content[:100]}...")
                else:
                    print(f"Response: {content}")

                # Check if result matches expectation
                if test_case.get("expected_hallucination") and detected:
                    print("✅ Test PASSED - Hallucination correctly detected")
                elif test_case.get("expected_normal") and not detected:
                    print("✅ Test PASSED - Normal response not flagged")
                else:
                    print("❌ Test result unclear")

            except Exception as e:
                print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    print("🔍 Testing Router-Level Hallucination Detection")
    print("=" * 50)
    asyncio.run(test_hallucination_detection())