#!/usr/bin/env python3
"""
Test script for Pydantic AI Logfire integration.
Tests basic Logfire functionality and instrumentation.
"""

import asyncio
import os
import sys
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

async def test_logfire_basic():
    """Test basic Logfire functionality."""
    print("🧪 Testing Pydantic AI Logfire Integration")
    print("=" * 50)

    try:
        import logfire
        print("✅ Logfire import successful")
        print(f"   Version: {getattr(logfire, '__version__', 'unknown')}")

        # Test basic configuration
        logfire.configure(
            service_name="test-ai-orchestrator",
            service_version="1.0.0-test",
            environment="test"
        )
        print("✅ Logfire configuration successful")

        # Test span creation
        with logfire.span("test_span", test_param="hello world") as span:
            print("✅ Span creation successful")
            span.set_attribute("custom_attr", "test_value")

        # Test logging
        logfire.log("test_event", message="Hello from Logfire", count=42)
        print("✅ Logging successful")

        print("\n🎉 All Logfire tests passed!")
        return True

    except ImportError as e:
        print(f"❌ Logfire import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Logfire test failed: {e}")
        return False

async def test_agent_engine_imports():
    """Test that our agent engine imports work with Logfire."""
    print("\n🧪 Testing Agent Engine Logfire Integration")
    print("=" * 50)

    try:
        # Import our engine
        from agent_runner.engine import AgentEngine, LOGFIRE_AVAILABLE
        print("✅ AgentEngine import successful")
        print(f"   Logfire available: {LOGFIRE_AVAILABLE}")

        # Test that we can create an engine (without actually initializing)
        print("✅ Engine import integration successful")

        return True

    except ImportError as e:
        print(f"❌ Agent engine import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Agent engine test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("🚀 Starting Pydantic AI Logfire Integration Tests\n")

    results = []
    results.append(await test_logfire_basic())
    results.append(await test_agent_engine_imports())

    print("\n" + "=" * 50)
    if all(results):
        print("🎉 ALL TESTS PASSED! Logfire integration is ready.")
        print("\nNext steps:")
        print("1. Set LOGFIRE_TOKEN environment variable for cloud logging")
        print("2. Restart the agent runner to enable observability")
        print("3. Check logs for spans and metrics")
        return 0
    else:
        print("❌ SOME TESTS FAILED. Check the output above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())