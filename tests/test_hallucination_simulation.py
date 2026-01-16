#!/usr/bin/env python3
"""
Simulate hallucinated MCP response to test detection.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "agent_runner"))

async def simulate_hallucination_detection():
    """Simulate the hallucinated MCP response that the user is seeing."""

    # Import required components
    from agent_runner.state import AgentState
    from agent_runner.hallucination_detector import HallucinationDetector, DetectorConfig

    print("🧠 Testing Hallucination Detection on MCP Response")
    print("=" * 60)

    # Create a mock state (minimal)
    state = AgentState()
    detector_config = DetectorConfig(enabled=True)
    detector = HallucinationDetector(state, detector_config)

    # The exact hallucinated response the user showed
    hallucinated_content = """To add an MCP (Microcomputer Communications Protocol) server, I can guide you through a step-by-step process.

Firstly, let's set up the necessary dependencies within the Orchestrator. Since we're working on macOS, we'll use Homebrew to install and manage packages:

brew install openssh

This will ensure that Secure Shell (SSH), which is essentially an implementation of SCP, is installed and running successfully. Once this installation finishes:"""

    # Test context
    context = {
        "response": hallucinated_content,
        "user_query": "How do I add an MCP server to the system?",
        "conversation_history": [],
        "model_info": {"model": "agent:mcp"}
    }

    print("📝 Testing Response:")
    print(f"Query: {context['user_query']}")
    print(f"Response: {hallucinated_content[:200]}...")
    print()

    # Run hallucination detection
    print("🔍 Running Hallucination Detection...")
    result = await detector.detect_hallucinations(**context)

    print("📊 Detection Results:")
    print(f"  Is hallucination: {result.is_hallucination}")
    print(f"  Severity: {result.severity.value}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Processing time: {result.processing_time_ms:.2f}ms")
    print(f"  Issues found: {len(result.detected_issues)}")

    print("\n🔎 Detected Issues:")
    for i, issue in enumerate(result.detected_issues, 1):
        print(f"  {i}. {issue.get('type', 'unknown')}: {issue.get('description', 'no desc')}")
        print(f"     Severity: {issue.get('severity', 'unknown')}, Confidence: {issue.get('confidence', 0):.2f}")

    # Check LLM-based detection
    llm_issues = [issue for issue in result.detected_issues if "llm_" in issue.get("type", "")]
    if llm_issues:
        print("\n🤖 LLM Analysis Results:")
        for issue in llm_issues:
            print(f"  - {issue['type']}: {issue['description']}")
    else:
        print("\n🤖 No LLM-specific issues detected")

    # Test what the corrected response would look like
    print("\n🔧 Simulated Corrected Response:")
    if result.severity.value == "critical":
        corrected = "I apologize, but I cannot provide accurate information about that topic. Please consult the official documentation or try rephrasing your question."
        print(f"CRITICAL: {corrected}")
    elif result.severity.value == "high":
        corrected = hallucinated_content + "\n\n⚠️ *Note: This response may contain inaccuracies. Please verify the information.*"
        print(f"HIGH: {corrected[:200]}... [WARNING ADDED]")
    else:
        print("No correction needed")

    # Cleanup
    await detector.cleanup()

    print("\n✅ Hallucination Detection Test Complete!")
    return result

if __name__ == "__main__":
    asyncio.run(simulate_hallucination_detection())