#!/usr/bin/env python3
"""
Test script for LLM-based hallucination detection.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "agent_runner"))

async def test_llm_hallucination_detector():
    """Test the LLM-based hallucination detection."""
    try:
        from agent_runner.state import AgentState
        from agent_runner.hallucination_detector import HallucinationDetector, DetectorConfig

        print("🧪 Testing LLM-based Hallucination Detection")
        print("=" * 50)

        # Initialize components
        state = AgentState()
        detector_config = DetectorConfig(enabled=True)
        detector = HallucinationDetector(state, detector_config)

        print("✅ Components initialized")

        # Test cases for LLM analysis
        test_cases = [
            {
                "name": "Coherent response",
                "query": "What is the capital of France?",
                "response": "The capital of France is Paris, a beautiful city known for the Eiffel Tower and Louvre Museum.",
                "expected_low_risk": True
            },
            {
                "name": "Hallucinated response",
                "query": "What is the capital of France?",
                "response": "The capital of France is actually London, but it moved there during the industrial revolution.",
                "expected_high_risk": True
            },
            {
                "name": "Tool call hallucination",
                "query": "What's the weather today?",
                "response": '{"name": "get_weather", "parameters": {"location": "unknown"}}',
                "expected_critical": True
            }
        ]

        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 Test {i}: {test_case['name']}")
            print(f"Query: {test_case['query']}")
            print(f"Response: {test_case['response'][:100]}...")

            # Test hallucination detection
            context = {
                "response": test_case["response"],
                "user_query": test_case["query"],
                "conversation_history": [],
                "model_info": {"model": "llama3.2:latest"}
            }

            result = await detector.detect_hallucinations(**context)

            print("🤖 Detection Results:"            print(f"  Is hallucination: {result.is_hallucination}")
            print(f"  Severity: {result.severity.value}")
            print(f"  Confidence: {result.confidence:.2f}")
            print(f"  Processing time: {result.processing_time_ms:.2f}ms")
            print(f"  Issues found: {len(result.detected_issues)}")

            # Check for LLM-based detections
            llm_issues = [issue for issue in result.detected_issues if "llm_" in issue.get("type", "")]
            if llm_issues:
                print(f"  🤖 LLM analysis found {len(llm_issues)} issues:")
                for issue in llm_issues:
                    print(f"    - {issue['type']}: {issue['description']}")

            # Verify expectation
            if test_case.get("expected_critical") and result.severity == "critical":
                print("✅ Test PASSED - Correctly detected critical hallucination")
            elif test_case.get("expected_high_risk") and result.severity in ["high", "critical"]:
                print("✅ Test PASSED - Correctly detected high-risk hallucination")
            elif test_case.get("expected_low_risk") and not result.is_hallucination:
                print("✅ Test PASSED - Correctly identified low-risk response")
            else:
                print(f"❌ Test result unclear - Severity: {result.severity.value}, Is hallucination: {result.is_hallucination}")

        # Test LLM analyzer directly
        print("\n🔬 Testing LLM Analyzer Directly")
        print("-" * 40)

        if detector.llm_analyzer:
            test_query = "What is 2 + 2?"
            test_response = "2 + 2 equals 5, as we all know from advanced mathematics."

            print(f"Query: {test_query}")
            print(f"Response: {test_response}")

            coherence_score = await detector.llm_analyzer.analyze_semantic_coherence(
                test_query, test_response
            )

            print(f"LLM coherence score: {coherence_score:.2f}")

            quality_analysis = await detector.llm_analyzer.detect_response_quality(
                test_query, test_response
            )

            print(f"LLM quality analysis: {quality_analysis}")
        else:
            print("❌ LLM analyzer not available")

        print("\n📊 System Statistics")
        print("-" * 30)
        print(f"Detector stats: {detector.get_stats()}")

        # Cleanup
        await detector.cleanup()

        print("\n🎉 LLM Hallucination Detection Testing Complete!")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_llm_hallucination_detector())