"""
Shared configuration module for AI Orchestrator.

This module provides a unified way to load configuration from multiple sources,
preparing for a future unified configuration file while maintaining backward compatibility.
"""

from .loader import load_config, get_config_value, ConfigSource

__all__ = ["load_config", "get_config_value", "ConfigSource"]












