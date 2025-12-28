"""
Configuration validation and environment setup.
"""

from __future__ import annotations

import os
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger("agent_runner.config_validator")


class ConfigValidator:
    """Validates configuration and environment setup."""
    
    @staticmethod
    def validate_config() -> Dict[str, Any]:
        """
        Validate configuration and return validation results.
        
        Returns:
            Dict with validation status and any issues found
        """
        issues: List[str] = []
        warnings: List[str] = []
        
        # Check required environment variables
        required_vars = [
            "AGENT_MODEL",
            "GATEWAY_BASE",
            "AGENT_FS_ROOT",
        ]
        
        for var in required_vars:
            if not os.getenv(var):
                issues.append(f"Missing required environment variable: {var}")
        
        # Validate AGENT_FS_ROOT
        fs_root = os.getenv("AGENT_FS_ROOT", "~/ai/agent_fs_root")
        fs_root_path = Path(fs_root).expanduser().resolve()
        if not fs_root_path.exists():
            try:
                fs_root_path.mkdir(parents=True, exist_ok=True)
                warnings.append(f"Created AGENT_FS_ROOT directory: {fs_root_path}")
            except Exception as e:
                issues.append(f"Cannot create AGENT_FS_ROOT directory: {e}")
        
        # Validate GATEWAY_BASE format
        gateway_base = os.getenv("GATEWAY_BASE", "")
        if gateway_base and not (gateway_base.startswith("http://") or gateway_base.startswith("https://")):
            warnings.append(f"GATEWAY_BASE should start with http:// or https://: {gateway_base}")
        
        # Check log directory
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
        log_path = Path(log_dir)
        if not log_path.exists():
            try:
                log_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                warnings.append(f"Cannot create log directory: {e}")
        
        # Validate numeric settings
        numeric_settings = [
            ("AGENT_MAX_READ_BYTES", int, 1, 10_000_000),
            ("AGENT_MAX_LIST_ENTRIES", int, 1, 10000),
            ("AGENT_MAX_TOOL_STEPS", int, 1, 100),
            ("AGENT_HTTP_TIMEOUT_S", float, 1.0, 600.0),
        ]
        
        for var, var_type, min_val, max_val in numeric_settings:
            value_str = os.getenv(var)
            if value_str:
                try:
                    value = var_type(value_str)
                    if value < min_val or value > max_val:
                        warnings.append(
                            f"{var}={value} is outside recommended range [{min_val}, {max_val}]"
                        )
                except ValueError:
                    issues.append(f"{var} must be a valid {var_type.__name__}: {value_str}")
        
        # Check optional dependencies
        optional_deps = {
            "yaml": "pyyaml (for config.yaml support)",
            "websockets": "websockets (for WebSocket MCP servers)",
        }
        
        for module, description in optional_deps.items():
            try:
                __import__(module)
            except ImportError:
                warnings.append(f"Optional dependency not installed: {description}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
        }
    
    @staticmethod
    def get_config_summary() -> Dict[str, Any]:
        """Get a summary of current configuration."""
        return {
            "agent_model": os.getenv("AGENT_MODEL", "not set"),
            "gateway_base": os.getenv("GATEWAY_BASE", "not set"),
            "agent_fs_root": os.getenv("AGENT_FS_ROOT", "not set"),
            "dev_mode": os.getenv("DEV_MODE", "0") == "1",
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "max_tool_steps": int(os.getenv("AGENT_MAX_TOOL_STEPS", "8")),
            "max_read_bytes": int(os.getenv("AGENT_MAX_READ_BYTES", "200000")),
            "http_timeout": float(os.getenv("AGENT_HTTP_TIMEOUT_S", "120.0")),
            "tool_cache_enabled": os.getenv("TOOL_CACHE_ENABLED", "true").lower() == "true",
        }






