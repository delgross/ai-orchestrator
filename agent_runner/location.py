
import logging
import httpx
import asyncio
from typing import Dict, Any, Optional

logger = logging.getLogger("agent_runner")

async def get_location(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Determine the system's physical location.
    
    Priority:
    1. Config Override (system.location in config.yaml)
    2. IP-API Auto-detection
    3. Fallback to "Unknown"
    
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
            "lat": loc.get("lat", 0.0),
            "lon": loc.get("lon", 0.0),
            "timezone": loc.get("timezone", "UTC"),
            "source": "config"
        }

    # 2. Auto-Detect via IP-API
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
        logger.warning(f"Location auto-detection failed: {e}")

    # 3. Fallback
    return {
        "city": "Unknown City",
        "region": "Unknown Region",
        "country": "Unknown Country",
        "lat": 0.0,
        "lon": 0.0,
        "timezone": "UTC",
        "source": "fallback"
    }
