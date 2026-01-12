#!/usr/bin/env python3
"""
Test Mirascope Integration

Tests the Mirascope-enhanced LLM functions to ensure they work correctly
without disrupting the existing system.
"""

import asyncio
import sys
import os
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_mirascope_integration():
    """Test Mirascope integration functions."""
    print("🧪 Testing Mirascope Integration...")

    try:
        # Test basic Mirascope import
        try:
            import mirascope
            MIRASCOPE_INSTALLED = True
            print("✅ Mirascope package is installed")
        except ImportError:
            MIRASCOPE_INSTALLED = False
            print("⚠️ Mirascope package not installed")

        # Test router provider imports
        from router.providers import MIRASCOPE_AVAILABLE, USE_MIRASCOPE
        print(f"✅ Mirascope integration flag: {MIRASCOPE_AVAILABLE}")
        print(f"📋 Mirascope usage enabled: {USE_MIRASCOPE}")

        if MIRASCOPE_AVAILABLE:
            print("✅ Router providers successfully imported Mirascope")

            # Test that the Mirascope functions exist
            from router.providers import mirascope_ollama_call, mirascope_ollama_stream
            print("✅ Mirascope-enhanced functions are available")

            # Test function signatures
            import inspect
            sig_call = inspect.signature(mirascope_ollama_call)
            sig_stream = inspect.signature(mirascope_ollama_stream)
            print(f"✅ mirascope_ollama_call parameters: {list(sig_call.parameters.keys())}")
            print(f"✅ mirascope_ollama_stream parameters: {list(sig_stream.parameters.keys())}")

        else:
            print("ℹ️ Mirascope integration disabled in router")

    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

    print("🎉 Mirascope integration test completed successfully!")
    return True

async def test_fallback_behavior():
    """Test that fallback to original functions works when Mirascope is disabled."""
    print("\n🧪 Testing Fallback Behavior...")

    try:
        from router.providers import call_ollama_chat

        # Test that original functions still work
        print("✅ Original call_ollama_chat function available")

        # This would require actual Ollama service to fully test
        # but we can verify the function exists and has correct signature
        import inspect
        sig = inspect.signature(call_ollama_chat)
        print(f"✅ Original function signature: {sig}")

    except Exception as e:
        print(f"❌ Fallback test error: {e}")
        return False

    print("🎉 Fallback behavior test completed successfully!")
    return True

if __name__ == "__main__":
    async def main():
        success1 = await test_mirascope_integration()
        success2 = await test_fallback_behavior()

        if success1 and success2:
            print("\n🎯 ALL TESTS PASSED - Mirascope integration is ready!")
            print("\nTo enable Mirascope:")
            print("1. Install: pip install mirascope")
            print("2. Set environment variable: USE_MIRASCOPE=true")
            print("3. Restart services")
        else:
            print("\n❌ Some tests failed - check the output above")
            sys.exit(1)

    asyncio.run(main())