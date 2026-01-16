#!/usr/bin/env python3
"""
Chaos Monkey for Chat Completions API
Tests system resilience with various edge cases and failure scenarios
"""

import asyncio
import json
import time
import random
import string
from typing import Dict, List, Any
import aiohttp
import sys

class ChaosMonkey:
    def __init__(self, base_url: str = "http://127.0.0.1:5455", auth_token: str = "antigravity_router_token_2025"):
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.session = None
        self.results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': []
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def log_result(self, test_name: str, success: bool, details: str = "", response_data: Dict = None):
        self.results['total_tests'] += 1
        if success:
            self.results['passed'] += 1
            status = "✅ PASS"
        else:
            self.results['failed'] += 1
            status = "❌ FAIL"

        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        if response_data:
            print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")

    async def make_request(self, payload: Dict[str, Any], expected_status: int = 200) -> Dict[str, Any]:
        """Make a request and return response data"""
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.auth_token}'
        }

        try:
            async with self.session.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response_data = await response.json()
                return {
                    'status': response.status,
                    'data': response_data,
                    'expected': expected_status
                }
        except Exception as e:
            return {
                'status': 'error',
                'data': {'error': str(e)},
                'expected': expected_status
            }

    # Test Cases
    async def test_valid_request(self):
        """Test a normal, valid request"""
        payload = {
            "messages": [{"role": "user", "content": "Hello, how are you?"}],
            "model": "agent:mcp",
            "stream": False
        }

        result = await self.make_request(payload)
        success = result['status'] == 200 and 'choices' in result['data']
        self.log_result("Valid Request", success, f"Status: {result['status']}", result['data'])

    async def test_streaming_request(self):
        """Test streaming functionality"""
        payload = {
            "messages": [{"role": "user", "content": "Tell me a short story"}],
            "model": "agent:mcp",
            "stream": True
        }

        try:
            async with self.session.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_token}'
                },
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                # Read streaming response
                data_received = False
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        data_received = True
                        break

                success = response.status == 200 and data_received
                self.log_result("Streaming Request", success, f"Status: {response.status}, Data received: {data_received}")

        except Exception as e:
            self.log_result("Streaming Request", False, f"Exception: {e}")

    async def test_empty_messages(self):
        """Test with empty messages array"""
        payload = {
            "messages": [],
            "model": "agent:mcp",
            "stream": False
        }

        result = await self.make_request(payload)
        # Should handle gracefully, not crash
        success = result['status'] in [200, 400]  # Either success or proper validation error
        self.log_result("Empty Messages", success, f"Status: {result['status']}")

    async def test_missing_content(self):
        """Test message without content field"""
        payload = {
            "messages": [{"role": "user"}],  # Missing content
            "model": "agent:mcp",
            "stream": False
        }

        result = await self.make_request(payload)
        success = result['status'] in [200, 400, 500]  # Should handle gracefully
        self.log_result("Missing Content", success, f"Status: {result['status']}")

    async def test_very_long_message(self):
        """Test with extremely long message"""
        long_content = "Hello! " * 1000  # 7,000 characters
        payload = {
            "messages": [{"role": "user", "content": long_content}],
            "model": "agent:mcp",
            "stream": False
        }

        result = await self.make_request(payload, expected_status=200)
        success = result['status'] == 200 or result['status'] == 'error'  # Should handle or timeout gracefully
        self.log_result("Very Long Message", success, f"Status: {result['status']}")

    async def test_special_characters(self):
        """Test with special characters and unicode"""
        special_content = "Hello 🌟 with émojis, spëcial chärs, and 日本語"
        payload = {
            "messages": [{"role": "user", "content": special_content}],
            "model": "agent:mcp",
            "stream": False
        }

        result = await self.make_request(payload)
        success = result['status'] == 200 and 'choices' in result['data']
        self.log_result("Special Characters", success, f"Status: {result['status']}")

    async def test_invalid_model(self):
        """Test with invalid model name"""
        payload = {
            "messages": [{"role": "user", "content": "Hello"}],
            "model": "invalid-model-name-that-does-not-exist",
            "stream": False
        }

        result = await self.make_request(payload)
        success = result['status'] in [200, 400]  # Should either work or give proper error
        self.log_result("Invalid Model", success, f"Status: {result['status']}")

    async def test_malformed_json(self):
        """Test with malformed JSON in message content"""
        payload = {
            "messages": [{"role": "user", "content": '{"incomplete": "json"'}],  # Malformed JSON
            "model": "agent:mcp",
            "stream": False
        }

        result = await self.make_request(payload)
        success = result['status'] in [200, 400, 500]  # Should handle gracefully
        self.log_result("Malformed JSON", success, f"Status: {result['status']}")

    async def test_missing_model(self):
        """Test request without model field"""
        payload = {
            "messages": [{"role": "user", "content": "Hello"}],
            "stream": False
            # Missing model field
        }

        result = await self.make_request(payload)
        success = result['status'] in [200, 400]  # Should either work or validate
        self.log_result("Missing Model", success, f"Status: {result['status']}")

    async def test_multiple_messages(self):
        """Test with conversation history"""
        payload = {
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
                {"role": "user", "content": "How are you?"}
            ],
            "model": "agent:mcp",
            "stream": False
        }

        result = await self.make_request(payload)
        success = result['status'] == 200 and 'choices' in result['data']
        self.log_result("Multiple Messages", success, f"Status: {result['status']}")

    async def test_rate_limiting(self):
        """Test rapid successive requests"""
        success_count = 0
        for i in range(5):
            payload = {
                "messages": [{"role": "user", "content": f"Request {i+1}"}],
                "model": "agent:mcp",
                "stream": False
            }

            result = await self.make_request(payload)
            if result['status'] == 200:
                success_count += 1
            await asyncio.sleep(0.1)  # Small delay

        success = success_count >= 3  # At least 3 should succeed
        self.log_result("Rate Limiting", success, f"Successful requests: {success_count}/5")

    async def test_empty_content(self):
        """Test with empty string content"""
        payload = {
            "messages": [{"role": "user", "content": ""}],
            "model": "agent:mcp",
            "stream": False
        }

        result = await self.make_request(payload)
        success = result['status'] in [200, 400]  # Should handle gracefully
        self.log_result("Empty Content", success, f"Status: {result['status']}")

    async def test_sql_injection_attempt(self):
        """Test potential security issues"""
        payload = {
            "messages": [{"role": "user", "content": "'; DROP TABLE users; --"}],
            "model": "agent:mcp",
            "stream": False
        }

        result = await self.make_request(payload)
        success = result['status'] in [200, 400, 500]  # Should not crash the system
        self.log_result("SQL Injection Attempt", success, f"Status: {result['status']}")

    async def run_all_tests(self):
        """Run all chaos tests"""
        print("🐵 CHAOS MONKEY: Starting Chat API Chaos Testing")
        print("=" * 60)

        tests = [
            self.test_valid_request,
            self.test_streaming_request,
            self.test_empty_messages,
            self.test_missing_content,
            self.test_very_long_message,
            self.test_special_characters,
            self.test_invalid_model,
            self.test_malformed_json,
            self.test_missing_model,
            self.test_multiple_messages,
            self.test_rate_limiting,
            self.test_empty_content,
            self.test_sql_injection_attempt,
        ]

        # Run tests with delays to avoid overwhelming
        for test in tests:
            try:
                await test()
            except Exception as e:
                self.log_result(f"{test.__name__}", False, f"Test crashed: {e}")

            # Random delay between tests
            await asyncio.sleep(random.uniform(0.5, 2.0))

        print("\n" + "=" * 60)
        print("🐵 CHAOS MONKEY: Testing Complete")
        print(f"📊 Results: {self.results['passed']}/{self.results['total_tests']} tests passed")
        print(f"❌ Failed: {self.results['failed']}")

        if self.results['errors']:
            print("\n🔥 Critical Errors:")
            for error in self.results['errors'][:5]:  # Show first 5
                print(f"   - {error}")

        return self.results

async def main():
    async with ChaosMonkey() as monkey:
        results = await monkey.run_all_tests()

        # Exit with appropriate code
        if results['failed'] == 0:
            print("🎉 All tests passed!")
            sys.exit(0)
        else:
            print(f"⚠️  {results['failed']} tests failed")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())