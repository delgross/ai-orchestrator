import logging
from typing import Dict, Any, Optional
from agent_runner.state import AgentState

logger = logging.getLogger("tools.admin")

SECRET_PASSPHRASE = "lloovies"

def unlock_session(state: AgentState, password: str) -> Dict[str, Any]:
    """
    Authenticate as the Owner to unlock 'God Mode' for this session.
    Once unlocked, no further passwords are required for sensitive actions.
    """
    if password == SECRET_PASSPHRASE:
        state.admin_override_active = True
        logger.info(f"ADMIN: Session unlocked by Owner.")
        return {
            "ok": True, 
            "message": "Session Unlocked. You have absolute control.",
            "mode": "SUDO"
        }
    else:
        logger.warning(f"ADMIN: Failed unlock attempt.")
        return {
            "ok": False, 
            "error": "Access Denied."
        }

def set_policy(state: AgentState, policy: str, value: Any, password: Optional[str] = None) -> Dict[str, Any]:
    """
    Modify ANY system policy (internet, safety, limits).
    Requires active Admin Session or immediate password.
    """
    # 1. Auth Check
    is_auth = state.admin_override_active or (password == SECRET_PASSPHRASE)
    
    if not is_auth:
        return {
            "ok": False, 
            "error": "Access Denied. Please unlock session or provide password.", 
            "hint": "Use unlock_session(password='lloovies')"
        }
    
    # 2. Apply Policy
    if policy == "internet":
        state.internet_policy_enabled = bool(value)
        state.internet_available = bool(value) # Force the flag too
    elif policy == "safety":
        # Placeholder for future safety overrides (e.g. LLM prompts)
        state.system_state["safety_override"] = bool(value)
    elif policy == "limits":
         if str(value).lower() == "infinity":
             state.max_tool_steps = 1000
             state.max_read_bytes = 1_000_000_000
    
    # Generic State Set for other policies
    state.system_state[f"policy_{policy}"] = value
    
    # If successful and password provided, imply unlock? 
    # User said "once I have given one" -> lets auto-unlock if password correct here too.
    if password == SECRET_PASSPHRASE:
        state.admin_override_active = True
        
    return {
        "ok": True,
        "message": f"Policy '{policy}' set to {value}.",
        "admin_active": True
    }


def check_admin_status(state: AgentState) -> Dict[str, Any]:
    return {
        "admin_active": state.admin_override_active,
        "internet_policy": state.internet_policy_enabled,
        "internet_available": state.internet_available
    }
