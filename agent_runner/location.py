
import logging
import httpx
import asyncio
from typing import Dict, Any, Optional

logger = logging.getLogger("agent_runner")

async def get_location(config: Dict[str, Any], memory=None) -> Dict[str, Any]:
    """
    Determine the system's physical location.

    Priority:
    1. Config Override (system.location in config.yaml)
    2. User Profile Location (from config file)
    3. User Profile Location (from permanent memory)
    4. Database DEFAULT_LOCATION (if memory available)
    5. IP-API Auto-detection (if internet available)
    6. Generic fallback location

    Returns:
        Dict with keys: city, region, country, lat, lon, timezone, source
    """
    
    # 1. Check Configuration Override
    system_cfg = config.get("system", {})
    if "location" in system_cfg and system_cfg["location"].get("enabled", False):
        loc = system_cfg["location"]
        logger.info(f"Using Configured Location: {loc.get('city')}, {loc.get('region')}")
        return {
            "city": loc.get("city", "Unknown City"),
            "region": loc.get("region", "Unknown Region"),
            "country": loc.get("country", "Unknown Country"),
            "postal_code": loc.get("postal_code", ""),
            "lat": loc.get("lat", 0.0),
            "lon": loc.get("lon", 0.0),
            "timezone": loc.get("timezone", "UTC"),
            "source": "config"
        }

    # 2. Check User Profile Location (from config file)
    try:
        import os
        # Try to find the config directory relative to this file
        current_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(current_dir)  # Go up one level from agent_runner
        config_profile_path = os.path.join(project_root, "config", "user_profile.txt")

        if os.path.exists(config_profile_path):
            with open(config_profile_path, 'r') as f:
                profile_content = f.read().lower()

            # Look for location indicators in user profile
            if "granville" in profile_content and ("ohio" in profile_content or "oh" in profile_content):
                logger.info("Using User Profile Location: Granville, Ohio")
                return {
                    "city": "Granville",
                    "region": "Ohio",
                    "country": "United States",
                    "postal_code": "43023",
                    "lat": 40.0681,
                    "lon": -82.5190,
                    "timezone": "America/New_York",
                    "source": "user_profile"
                }
            elif "newark" in profile_content and ("ohio" in profile_content or "oh" in profile_content):
                # Primary residence is Granville, farm is in Newark
                # Default to primary residence
                logger.info("Using User Profile Location: Granville, Ohio (primary residence)")
                return {
                    "city": "Granville",
                    "region": "Ohio",
                    "country": "United States",
                    "postal_code": "43023",
                    "lat": 40.0681,
                    "lon": -82.5190,
                    "timezone": "America/New_York",
                    "source": "user_profile"
                }
    except Exception as e:
        logger.debug(f"User profile location check failed: {e}")

    # 2.5. Check User Profile Location (from permanent memory as fallback)
    if memory:
        try:
            # Query user profile from permanent memory
            profile_result = await memory.query_facts("user location OR user address OR lives in", kb_id="project_registry/user_profile", limit=5)
            if profile_result and profile_result.get("ok"):
                facts = profile_result.get("result", [])
                for fact in facts:
                    content = fact.get("content", "").lower()
                    # Look for location indicators in user profile
                    if "granville" in content and "ohio" in content:
                        logger.info("Using Permanent Memory Location: Granville, Ohio")
                        return {
                            "city": "Granville",
                            "region": "Ohio",
                            "country": "United States",
                            "postal_code": "43023",
                            "lat": 40.0681,
                            "lon": -82.5190,
                            "timezone": "America/New_York",
                            "source": "permanent_memory"
                        }
        except Exception as e:
            logger.debug(f"Permanent memory location check failed: {e}")

    # 4. Auto-Detect via IP-API (if internet available)
    # We use ip-api.com (free for non-commercial use, 45 requests/min)
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get("http://ip-api.com/json/")
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "success":
                    location = {
                        "city": data.get("city", "Unknown"),
                        "region": data.get("regionName", "Unknown"),
                        "country": data.get("country", "Unknown"),
                        "postal_code": data.get("zip", ""),
                        "lat": data.get("lat", 0.0),
                        "lon": data.get("lon", 0.0),
                        "timezone": data.get("timezone", "UTC"),
                        "source": "auto (ip-api)"
                    }
                    logger.info(f"Auto-Detected Location: {location['city']}, {location['region']}")
                    return location
                else:
                    logger.warning(f"Location detection returned error status: {data}")
    except Exception as e:
        logger.debug(f"Location auto-detection failed (expected if offline): {e}")

    # 5. Check database for DEFAULT_LOCATION (if memory is available)
    if memory:
        try:
            from agent_runner.db_utils import run_query_with_memory
            query = "SELECT value FROM config_state WHERE key = 'DEFAULT_LOCATION' LIMIT 1;"
            result = await run_query_with_memory(memory, query)
            if result and len(result) > 0:
                default_loc = result[0].get("value")
                if default_loc:
                    # Handle both dict and JSON string
                    if isinstance(default_loc, str):
                        import json
                        default_loc = json.loads(default_loc)
                    
                    logger.info(f"Using Database Default Location: {default_loc.get('city')}, {default_loc.get('region')}")
                    return {
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

    # 7. Generic fallback location
    logger.info("Using Generic Fallback Location")
    return {
        "city": "Unknown",
        "region": "Unknown",
        "country": "Unknown",
        "postal_code": "",
        "lat": 0.0,
        "lon": 0.0,
        "timezone": "UTC",
        "source": "generic_fallback"
    }
