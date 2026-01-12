"""
Quality vs Speed Control System - Tier Definitions

Provides 5-tier quality/speed control system that adjusts multiple layers simultaneously.
"""

from typing import Dict, Any, Literal
from enum import Enum


class QualityTier(str, Enum):
    """Quality tier enumeration."""
    FASTEST = "fastest"
    FAST = "fast"
    BALANCED = "balanced"
    QUALITY = "quality"
    MAXIMUM = "maximum"


QUALITY_TIER_CONFIGS: Dict[QualityTier, Dict[str, Any]] = {
    # Remote-optimized tiers - less aggressive compression for better quality
    QualityTier.FASTEST: {
        "skip_refinement": True,
        "memory_retrieval": {"enabled": False, "limit": 0},
        "architecture_context": {"enabled": False, "limit": 0},
        "tool_filtering": {"mode": "core_only", "max_tools": 12},
        "context_pruning": {"enabled": True, "limit": 8},
        "file_context": {"enabled": False},
        "service_alerts": {"enabled": False},
        "remote_compression": {"enabled": True, "max_messages": 3, "max_message_length": 800, "max_tools": 12, "system_prompt_limit": 1200}
    },
    QualityTier.FAST: {
        "skip_refinement": True,
        "memory_retrieval": {"enabled": False, "limit": 0},
        "architecture_context": {"enabled": False, "limit": 0},
        "tool_filtering": {"mode": "core_only", "max_tools": 8},  # Reduced from 25
        "context_pruning": {"enabled": True, "limit": 12},
        "file_context": {"enabled": False},
        "service_alerts": {"enabled": True},
        "remote_compression": {"enabled": True, "max_messages": 4, "max_message_length": 1200, "max_tools": 6, "system_prompt_limit": 1500}  # Reduced
    },
    QualityTier.BALANCED: {  # NEW DEFAULT - optimized for performance on Mac Studio
        "skip_refinement": False,
        "memory_retrieval": {"enabled": True, "limit": 8},
        "architecture_context": {"enabled": True, "limit": 20},  # Reduced from 35
        "tool_filtering": {"mode": "core_only", "max_tools": 15},  # Reduced from 40
        "context_pruning": {"enabled": True, "limit": 25},
        "file_context": {"enabled": True},
        "service_alerts": {"enabled": True},
        "remote_compression": {"enabled": True, "max_messages": 6, "max_message_length": 1800, "max_tools": 12, "system_prompt_limit": 2000}  # Reduced
    },
    QualityTier.QUALITY: {  # Better quality for complex tasks
        "skip_refinement": False,
        "memory_retrieval": {"enabled": True, "limit": 12},
        "architecture_context": {"enabled": True, "limit": 60},
        "tool_filtering": {"mode": "intent_based", "max_tools": 60},
        "context_pruning": {"enabled": True, "limit": 30},
        "file_context": {"enabled": True},
        "service_alerts": {"enabled": True},
        "remote_compression": {"enabled": True, "max_messages": 8, "max_message_length": 2500, "max_tools": 50, "system_prompt_limit": 3500}
    },
    QualityTier.MAXIMUM: {  # Maximum quality, minimal compression
        "skip_refinement": False,
        "memory_retrieval": {"enabled": True, "limit": 25},
        "architecture_context": {"enabled": True, "limit": 75},
        "tool_filtering": {"mode": "all", "max_tools": 100},
        "context_pruning": {"enabled": False},
        "file_context": {"enabled": True},
        "service_alerts": {"enabled": True},
        "remote_compression": {"enabled": False, "max_messages": 12, "max_message_length": 5000, "max_tools": 80, "system_prompt_limit": 5000}  # Full context for critical tasks
    }
}


def get_tier_config(tier: QualityTier) -> Dict[str, Any]:
    """Get configuration for a quality tier."""
    return QUALITY_TIER_CONFIGS.get(tier, QUALITY_TIER_CONFIGS[QualityTier.BALANCED])


def get_tier_performance_estimate(tier: QualityTier) -> Dict[str, Any]:
    """Get estimated performance metrics for a tier."""
    estimates = {
        QualityTier.FASTEST: {"latency_ms": (50, 100), "context_tokens": (200, 300)},
        QualityTier.FAST: {"latency_ms": (100, 150), "context_tokens": (300, 500)},
        QualityTier.BALANCED: {"latency_ms": (150, 250), "context_tokens": (500, 1000)},
        QualityTier.QUALITY: {"latency_ms": (200, 350), "context_tokens": (1000, 1500)},
        QualityTier.MAXIMUM: {"latency_ms": (300, 500), "context_tokens": (1500, 2500)}
    }
    return estimates.get(tier, estimates[QualityTier.BALANCED])


def get_tier_description(tier: QualityTier) -> str:
    """Get human-readable description of a tier."""
    descriptions = {
        QualityTier.FASTEST: "Minimal quality, maximum speed - fastest responses with minimal context",
        QualityTier.FAST: "Reduced quality, high speed - quick responses with limited context",
        QualityTier.BALANCED: "Good balance between quality and speed - default setting",
        QualityTier.QUALITY: "High quality, moderate speed - comprehensive context and tools",
        QualityTier.MAXIMUM: "Best quality, slower speed - full context, all tools, no pruning"
    }
    return descriptions.get(tier, descriptions[QualityTier.BALANCED])







