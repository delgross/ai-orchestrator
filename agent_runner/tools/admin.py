import logging
import os
from typing import Dict, Any, Optional
from agent_runner.state import AgentState
from agent_runner.db_utils import run_query

logger = logging.getLogger("tools.admin")

async def _get_secret_passphrase(state: AgentState) -> str:
    """
    Get admin passphrase from:
    1. Environment variable ADMIN_PASSWORD (highest priority)
    2. Database config_state table (ADMIN_PASSWORD key)
    3. Hardcoded default (fallback only)
    """
    # 1. Check environment variable
    env_pass = os.getenv("ADMIN_PASSWORD")
    if env_pass:
        return env_pass
    
    # 2. Check database (if memory is available)
    if hasattr(state, "memory") and state.memory:
        try:
            result = await run_query(state, """
                SELECT value FROM config_state 
                WHERE key = 'ADMIN_PASSWORD' LIMIT 1;
            """)
            if result and len(result) > 0:
                db_pass = result[0].get("value")
                if db_pass:
                    return str(db_pass)
        except Exception as e:
            logger.debug(f"Failed to load ADMIN_PASSWORD from database: {e}")
    
    # 3. Hardcoded fallback (for initial setup)
    return "lloovies"

async def unlock_session(state: AgentState, password: str) -> Dict[str, Any]:
    """
    Authenticate as the Owner to unlock 'God Mode' for this session.
    Once unlocked, no further passwords are required for sensitive actions.
    """
    secret_passphrase = await _get_secret_passphrase(state)
    if password == secret_passphrase:
        import time
        state.admin_override_active = True
        state.sudo_granted_at = time.time()  # Track when sudo was granted
        logger.info(f"ADMIN: Sudo unlocked. Will persist until system is idle (REFLECTIVE tempo or deeper).")
        return {
            "ok": True, 
            "message": "Sudo unlocked. Will persist until system is idle (REFLECTIVE tempo or deeper).",
            "mode": "SUDO",
            "revert_tempo": state.sudo_revert_tempo
        }
    else:
        logger.warning(f"ADMIN: Failed unlock attempt.")
        return {
            "ok": False, 
            "error": "Access Denied."
        }

async def set_policy(state: AgentState, policy: str, value: Any, password: Optional[str] = None) -> Dict[str, Any]:
    """
    Modify ANY system policy (internet, safety, limits).
    Requires active Admin Session or immediate password.
    """
    # 1. Auth Check
    secret_passphrase = await _get_secret_passphrase(state)
    is_auth = state.admin_override_active or (password == secret_passphrase)
    
    if not is_auth:
        return {
            "ok": False, 
            "error": "Access Denied. Please unlock session or provide password.", 
            "hint": "Use unlock_session() with the admin password"
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
    if password == secret_passphrase:
        import time
        state.admin_override_active = True
        state.sudo_granted_at = time.time()  # Track when sudo was granted
        
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
