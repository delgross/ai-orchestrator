#!/usr/bin/env python3
"""
Test script for the expanded capability detection system.
Tests the new taxonomy and multi-capability recognition.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_runner.tool_categories import (
    detect_query_capabilities,
    get_tools_for_capabilities,
    resolve_capability_conflicts,
    get_capability_context_window_adjustment
)

def test_capability_detection():
    """Test various queries against the capability detection system."""

    test_queries = [
        # Single capability queries
        ("How widespread is the rioting in Iran?", ["web_search"]),
        ("What have we talked about before?", ["memory"]),
        ("Run this Python script for me", ["code_execution"]),
        ("List all files in my home directory", ["file_access"]),
        ("Check system health and performance", ["system_admin"]),

        # Multi-capability queries
        ("Analyze the sales data and create a chart", ["data_analysis", "creative"]),
        ("Write an article about recent news in tech", ["creative", "web_search"]),
        ("Research academic papers and create citations", ["research", "creative"]),
        ("Schedule a meeting and send email reminders", ["communication"]),
        ("Automate file backup and system monitoring", ["automation", "system_admin"]),

        # Complex multi-capability queries
        ("Find recent research on AI, analyze the data, and write a summary report", ["research", "data_analysis", "creative"]),
        ("Check memory usage, clean up old files, and send status report", ["system_admin", "file_access", "communication"]),

        # Conflict resolution test cases
        ("Write code and save it to a file", ["creative", "file_access"]),  # Potential conflict between creative writing and file operations
        ("Research data online and create a statistical analysis", ["research", "data_analysis"]),  # Web research + data analysis
    ]

    print("🧪 TESTING CAPABILITY DETECTION SYSTEM")
    print("=" * 60)

    for query, expected_capabilities in test_queries:
        print(f"\n📝 Query: '{query}'")
        print(f"🎯 Expected: {expected_capabilities}")

        # Detect capabilities
        detected = detect_query_capabilities(query)
        print(f"🔍 Detected: {list(detected.keys())}")

        # Resolve conflicts if any
        if len(detected) > 1:
            resolved = resolve_capability_conflicts(detected)
            if resolved != detected:
                print(f"⚖️  Resolved conflicts: {list(resolved.keys())}")

        # Get tool recommendations
        tools = get_tools_for_capabilities(detected)
        print(f"🛠️  Categories: {tools['categories']}")
        print(f"⭐ Priority tools: {tools['priority_tools']}")

        # Context window adjustment
        context_window = get_capability_context_window_adjustment(detected)
        print(f"📏 Context window: {context_window} tokens")

        # Show conflict resolution if applicable
        resolved = resolve_capability_conflicts(detected)
        if resolved != detected:
            print(f"⚖️  Conflicts resolved: {list(resolved.keys())}")

        # Calculate accuracy
        detected_caps = set(detected.keys())
        expected_caps = set(expected_capabilities)
        accuracy = len(detected_caps & expected_caps) / len(expected_caps) if expected_caps else 0
        print(f"✅ Accuracy: {accuracy:.1f}")
        print("-" * 40)

if __name__ == "__main__":
    test_capability_detection()