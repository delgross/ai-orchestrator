#!/usr/bin/env python3
"""
Test script for the hallucination detection system.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "agent_runner"))

async def test_hallucination_detector():
    """Test the hallucination detection system."""
    try:
        from agent_runner.state import AgentState
        from agent_runner.hallucination_detector import HallucinationDetector, DetectorConfig
        from agent_runner.knowledge_base import KnowledgeBase

        print("🧪 Testing Hallucination Detection System")
        print("=" * 50)

        # Initialize components
        state = AgentState()
        detector_config = DetectorConfig(enabled=True)
        detector = HallucinationDetector(state, detector_config)
        kb = KnowledgeBase(state)

        print("✅ Components initialized")

        # Test cases
        test_cases = [
            {
                "name": "Normal response",
                "response": "The weather in Columbus Ohio is sunny today with temperatures around 75°F.",
                "user_query": "What's the weather like in Columbus?",
                "expected_hallucination": False
            },
            {
                "name": "Mathematical error",
                "response": "2 + 2 = 5, which is a well-known mathematical fact.",
                "user_query": "What is 2 + 2?",
                "expected_hallucination": True
            },
            {
                "name": "Factual error",
                "response": "The capital of France is London, as everyone knows.",
                "user_query": "What is the capital of France?",
                "expected_hallucination": True
            },
            {
                "name": "Tool call hallucination",
                "response": '{"name": "web_search", "parameters": {"query": "test"}}',
                "user_query": "Search for something",
                "expected_hallucination": True
            }
        ]

        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 Test {i}: {test_case['name']}")
            print(f"Query: {test_case['user_query']}")
            print(f"Response: {test_case['response'][:100]}...")

            # Test hallucination detection
            context = {
                "response": test_case["response"],
                "user_query": test_case["user_query"],
                "conversation_history": [],
                "model_info": {"model": "test-model"}
            }

            result = await detector.detect_hallucinations(**context)

            print(f"Result: {'❌ HALLUCINATION' if result.is_hallucination else '✅ OK'}")
            print(f"Severity: {result.severity.value}")
            print(f"Confidence: {result.confidence:.2f}")
            print(f"Processing time: {result.processing_time_ms:.2f}ms")

            if result.detected_issues:
                print(f"Issues found: {len(result.detected_issues)}")
                for issue in result.detected_issues[:2]:  # Show first 2 issues
                    print(f"  - {issue['type']}: {issue['description'][:60]}...")

            # Verify expectation
            expected = test_case["expected_hallucination"]
            actual = result.is_hallucination

            if expected == actual:
                print("✅ Test PASSED")
            else:
                print(f"❌ Test FAILED - Expected {expected}, got {actual}")

        # Test knowledge base
        print("\n🧠 Testing Knowledge Base")
        print("-" * 30)

        facts_to_test = [
            "2 + 2 = 4",
            "The capital of France is Paris",
            "The sky is blue"
        ]

        for fact in facts_to_test:
            result = await kb.verify_fact(fact)
            print(f"Fact: '{fact}' -> Verified: {result.verified} (confidence: {result.confidence:.2f})")

        print("\n📊 System Statistics")
        print("-" * 30)
        print(f"Detector stats: {detector.get_stats()}")
        print(f"KB stats: {kb.get_stats()}")

        print("\n🎉 Hallucination Detection Testing Complete!")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_hallucination_detector())