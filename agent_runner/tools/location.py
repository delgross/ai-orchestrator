"""
Location Service Tools

Provides location as a core service with database fallback.
"""
import logging
from typing import Dict, Any, Optional
from agent_runner.db_utils import run_query

logger = logging.getLogger("agent_runner.tools.location")


async def tool_get_location(state) -> Dict[str, Any]:
    """
    Get current location from state or database default.

    Priority:
    1. state.location (if set and valid)
    2. Database config_state.DEFAULT_LOCATION
    3. Generic fallback location

    Returns:
        Dict with location information
    """
    try:
        # 1. Check state.location (if set and valid)
        if hasattr(state, 'location') and state.location:
            loc = state.location
            # Validate it's not just a fallback/error state
            if loc.get("city") and loc.get("city") != "Unknown" and loc.get("source") not in ["timeout", "error", "fallback"]:
                return {
                    "ok": True,
                    "city": loc.get("city", "Unknown"),
                    "region": loc.get("region", "Unknown"),
                    "country": loc.get("country", "Unknown"),
                    "postal_code": loc.get("postal_code", ""),
                    "lat": loc.get("lat", 0.0),
                    "lon": loc.get("lon", 0.0),
                    "timezone": loc.get("timezone", "America/New_York"),
                    "source": loc.get("source", "state")
                }
        
        # 2. Check database for DEFAULT_LOCATION
        if hasattr(state, 'memory') and state.memory:
            try:
                query = "SELECT value FROM config_state WHERE key = 'DEFAULT_LOCATION' LIMIT 1;"
                result = await run_query(state, query)
                if result and len(result) > 0:
                    default_loc = result[0].get("value")
                    if default_loc:
                        # Handle both dict and JSON string
                        if isinstance(default_loc, str):
                            import json
                            default_loc = json.loads(default_loc)
                        
                        return {
                            "ok": True,
                            "city": default_loc.get("city", "Unknown"),
                            "region": default_loc.get("region", "Unknown"),
                            "country": default_loc.get("country", "Unknown"),
                            "postal_code": default_loc.get("postal_code", ""),
                            "lat": default_loc.get("lat", 0.0),
                            "lon": default_loc.get("lon", 0.0),
                            "timezone": default_loc.get("timezone", "UTC"),
                            "source": "database_default"
                        }
            except Exception as db_err:
                logger.debug(f"Failed to load DEFAULT_LOCATION from database: {db_err}")
        
        # 3. Generic fallback location
        return {
            "ok": True,
            "city": "Unknown",
            "region": "Unknown",
            "country": "Unknown",
            "postal_code": "",
            "lat": 0.0,
            "lon": 0.0,
            "timezone": "UTC",
            "source": "generic_fallback"
        }
    except Exception as e:
        logger.error(f"Failed to get location: {e}", exc_info=True)
        # Final fallback
        return {
            "ok": True,
            "city": "Unknown",
            "region": "Unknown",
            "country": "Unknown",
            "postal_code": "",
            "lat": 0.0,
            "lon": 0.0,
            "timezone": "UTC",
            "source": "fallback"
        }






