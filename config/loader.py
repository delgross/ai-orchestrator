"""
Configuration loader that supports multiple sources and prepares for unified config.

Currently supports:
- Environment variables (highest priority)
- .env files (router.env, agent_runner.env)
- Future: unified config.yaml (when implemented)

This allows gradual migration to a unified config file.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional, Union
from enum import Enum

try:
    import yaml
except ImportError:
    yaml = None


class ConfigSource(Enum):
    """Configuration source priority."""
    ENV = 1  # Environment variables (highest priority)
    ENV_FILE = 2  # .env files
    UNIFIED = 3  # Future: unified config.yaml (lowest priority, not yet implemented)


# Cache for loaded config
_config_cache: Optional[Dict[str, Any]] = None
_config_source: Optional[Path] = None


def _load_env_file(path: Path) -> Dict[str, str]:
    """Load a .env file and return as dict."""
    result = {}
    if not path.exists():
        return result
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith("#"):
                    continue
                # Handle inline comments (split on # but preserve quoted values)
                if "=" in line:
                    # Simple split on first =, then remove inline comments
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    # Remove inline comment if present (but preserve # in quoted strings)
                    if "#" in value and not (value.startswith('"') or value.startswith("'")):
                        value = value.split("#", 1)[0].strip()
                    # Remove quotes if present
                    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    result[key] = value
    except Exception:
        pass
    
    return result


def _load_unified_config(path: Path) -> Dict[str, Any]:
    """Load unified config.yaml (future feature, not yet implemented)."""
    if not yaml:
        return {}
    if not path.exists():
        return {}
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def load_config(
    service: str = "all",
    project_root: Optional[Union[str, Path]] = None,
    unified_config_path: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """
    Load configuration from all available sources.
    
    Args:
        service: "router", "agent_runner", or "all"
        project_root: Project root directory (defaults to detecting from this file)
        unified_config_path: Path to unified config.yaml (future feature)
    
    Returns:
        Dictionary of configuration values with source priority:
        1. Environment variables (highest)
        2. Service-specific .env files
        3. Unified config.yaml (future, lowest)
    """
    global _config_cache, _config_source
    
    # Detect project root if not provided
    if project_root is None:
        # This file is in config/, so go up one level
        project_root = Path(__file__).parent.parent
    else:
        project_root = Path(project_root)
    
    config: Dict[str, Any] = {}
    
    # 1. Load unified config.yaml (future feature, lowest priority)
    if unified_config_path:
        unified_path = Path(unified_config_path)
        if unified_path.exists():
            unified = _load_unified_config(unified_path)
            if service == "all":
                config.update(unified)
            elif service in unified:
                config.update(unified.get(service, {}))
    
    # 2. Load service-specific .env files (medium priority)
    if service in ("router", "all"):
        router_env = project_root / "router.env"
        config.update(_load_env_file(router_env))
    
    if service in ("agent_runner", "all"):
        agent_env = project_root / "agent_runner" / "agent_runner.env"
        config.update(_load_env_file(agent_env))
    
    # 3. Environment variables override everything (highest priority)
    # Only override if the env var exists
    for key in list(config.keys()):
        env_value = os.getenv(key)
        if env_value is not None:
            config[key] = env_value
    
    # Also add any env vars that start with known prefixes
    known_prefixes = ["AGENT_", "ROUTER_", "MCP_", "GATEWAY_", "OLLAMA_", "RAG_", "DEV_MODE"]
    for key, value in os.environ.items():
        if any(key.startswith(prefix) for prefix in known_prefixes):
            config[key] = value
    
    _config_cache = config
    _config_source = project_root
    
    return config


def get_config_value(
    key: str,
    default: Any = None,
    service: str = "all",
    project_root: Optional[Union[str, Path]] = None,
) -> Any:
    """
    Get a single configuration value.
    
    Args:
        key: Configuration key name
        default: Default value if not found
        service: "router", "agent_runner", or "all"
        project_root: Project root directory
    
    Returns:
        Configuration value or default
    """
    config = load_config(service=service, project_root=project_root)
    return config.get(key, default)


def get_config_path(service: str) -> Optional[Path]:
    """Get the path to the service's config file."""
    if _config_source is None:
        return None
    
    if service == "router":
        return _config_source / "router.env"
    elif service == "agent_runner":
        return _config_source / "agent_runner" / "agent_runner.env"
    
    return None




















