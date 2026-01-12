import os
import yaml
import logging
from typing import Any, Dict, Optional, List

logger = logging.getLogger(__name__)

def load_sovereign_config() -> Dict[str, Any]:
    """
    Load the Sovereign Registry (sovereign.yaml) from disk.
    This provides the Single Source of Truth for Models, Ports, and Policies.
    """
    try:
        # Standardize path: repo_root/config/sovereign.yaml
        # This file is in repo_root/common/sovereign.py
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Priority 1: config/sovereign.yaml
        path = os.path.join(base_dir, "config", "sovereign.yaml")
        
        if os.path.exists(path):
             with open(path, "r") as f:
                 return yaml.safe_load(f) or {}
                 
        # Priority 2: Try to find config dir if structure is different
        # (e.g. running from inside agent_runner)
        # But base_dir linkage above is fairly robust for this project structure.
        
    except Exception as e:
        logger.warning(f"Failed to load sovereign.yaml: {e}")
        
    return {}

# Singleton instance for easy import
# from common.sovereign import SOVEREIGN_CONFIG, get_model, get_port
SOVEREIGN_CONFIG = load_sovereign_config()

def get_sovereign_model(role: str, default: Optional[str] = None) -> Optional[str]:
    """Get a model ID from the registry."""
    return SOVEREIGN_CONFIG.get("models", {}).get(role, default)

def get_sovereign_port(service: str, default: Optional[int] = None) -> Optional[int]:
    """Get a port number from the registry."""
    return SOVEREIGN_CONFIG.get("network", {}).get(f"{service}_port", default)

def get_sovereign_policy(policy_name: str, default: Any = None) -> Any:
    """Get a policy value from the registry."""
    return SOVEREIGN_CONFIG.get("policies", {}).get(policy_name, default)

def get_sovereign_triggers() -> List[Dict[str, Any]]:
    """Get all trigger definitions."""
    return SOVEREIGN_CONFIG.get("triggers", [])

def get_sovereign_roles() -> List[Dict[str, Any]]:
    """Get all role definitions/models."""
    models = SOVEREIGN_CONFIG.get("models", {})
    roles = []
    for role, model in models.items():
        roles.append({
            "id": role,
            "name": role.title(),
            "description": f"Sovereign Role: {role}", # Description is implied/hardcoded in old registry, simplifying here
            "default_model": model
        })
    return roles

def get_sovereign_toggles() -> List[Dict[str, Any]]:
    """Get all policy toggles as 'toggle' objects for tool compat."""
    policies = SOVEREIGN_CONFIG.get("policies", {})
    toggles = []
    for key, val in policies.items():
        # Heuristic mapping for compatibility
        options = ["true", "false"] if isinstance(val, bool) else []
        toggles.append({
            "key": f"policy:{key}",
            "name": key.title().replace("_", " "),
            "description": f"Sovereign Policy: {key}",
            "options": options,
            "default": str(val),
            "requires_admin": True
        })
    return toggles

