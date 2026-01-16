#!/usr/bin/env python3
"""
Quick Chaos Monkey for Chat API - Focused Testing
"""

import asyncio
import json
import aiohttp

async def test_chat_endpoint():
    """Run focused chaos tests on chat endpoint"""
    url = "http://127.0.0.1:5455/v1/chat/completions"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer antigravity_router_token_2025'
    }

    test_cases = [
        ("Valid Request", {
            "messages": [{"role": "user", "content": "Hello"}],
            "model": "agent:mcp",
            "stream": False
        }),
        ("Empty Messages", {
            "messages": [],
            "model": "agent:mcp",
            "stream": False
        }),
        ("Missing Content", {
            "messages": [{"role": "user"}],
            "model": "agent:mcp",
            "stream": False
        }),
        ("Special Chars", {
            "messages": [{"role": "user", "content": "Hello 🌟 with émojis"}],
            "model": "agent:mcp",
            "stream": False
        }),
        ("Long Message", {
            "messages": [{"role": "user", "content": "Hello! " * 100}],
            "model": "agent:mcp",
            "stream": False
        }),
    ]

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
        for test_name, payload in test_cases:
            try:
                print(f"🧪 Testing: {test_name}")
                async with session.post(url, json=payload, headers=headers) as response:
                    result = await response.json()
                    print(f"   Status: {response.status}")
                    if response.status == 200 and 'choices' in result:
                        print("   ✅ PASS")
                    else:
                        print("   ⚠️  UNEXPECTED RESPONSE")
                        print(f"   Response: {json.dumps(result, indent=2)[:200]}...")
            except Exception as e:
                print(f"   ❌ FAIL: {e}")

            await asyncio.sleep(1)  # Brief pause between tests

if __name__ == "__main__":
    asyncio.run(test_chat_endpoint())