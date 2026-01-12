from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Any, Optional
import httpx
import logging

from router.config import (
    state, 
    SURREAL_URL, SURREAL_USER, SURREAL_PASS, SURREAL_NS, SURREAL_DB
)

router = APIRouter(tags=["config"])
logger = logging.getLogger("router.config")

class ConfigUpdate(BaseModel):
    value: str

def get_surreal_url():
    # Helper to format URL
    url = SURREAL_URL.replace("ws://", "http://").replace("wss://", "https://")
    url = url.replace("/rpc", "")
    if not url.endswith("/sql"):
        url = f"{url.rstrip('/')}/sql"
    return url

@router.get("/config/{key}")
async def get_config(key: str):
    """Retrieve a system configuration value."""
    # Special internal state keys
    if key == "router_mode":
        return {"key": key, "value": state.router_mode}
        
    url = get_surreal_url()
    
    # Query config_state table
    q = "USE NS " + SURREAL_NS + " DB " + SURREAL_DB + "; SELECT value FROM config_state WHERE key = $key"
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                content=q,
                auth=(SURREAL_USER, SURREAL_PASS), # Direct HTTP auth
                headers={"Accept": "application/json", "NS": SURREAL_NS, "DB": SURREAL_DB},
                params={"key": key} # Does not work for vars in body unless parsed? 
                # Surreal HTTP uses body vars? No, usually LET $x = ...
            )
            # Use raw string construction for simplicity in REST or LET prefix
            q_safe = f"USE NS {SURREAL_NS} DB {SURREAL_DB}; SELECT value FROM config_state WHERE key = '{key}'"
            resp = await client.post(
                 url,
                 content=q_safe,
                 auth=(SURREAL_USER, SURREAL_PASS),
                 headers={"Accept": "application/json", "NS": SURREAL_NS, "DB": SURREAL_DB}
            )
            
            if resp.status_code != 200:
                logger.error(f"Surreal Error: {resp.text}")
                return {"key": key, "value": None}
            
            data = resp.json()
            # Parse result: [{"status": "OK", "result": [{"value": "foo"}]}]
            if isinstance(data, list) and data:
                last = data[-1]
                if last.get("status") == "OK" and last.get("result"):
                    return {"key": key, "value": last["result"][0].get("value")}
                    
            return {"key": key, "value": None}
            
    except Exception as e:
        logger.error(f"DB Config Fetch Failed: {e}")
        # Fallback to environment variable if database is inaccessible
        import os
        env_value = os.getenv(key)
        if env_value is not None:
            logger.info(f"Using environment variable fallback for {key}")
            return {"key": key, "value": env_value}
        # Re-raise if neither database nor environment has the value
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/config/{key}")
async def set_config(key: str, update: ConfigUpdate):
    """Update a system configuration value."""
    
    # 1. Update In-Memory State for known keys
    if key == "router_mode":
        if update.value not in ["sync", "async"]:
            raise HTTPException(400, "router_mode must be 'sync' or 'async'")
        state.router_mode = update.value
        logger.info(f"Updated state.router_mode to {state.router_mode}")
    
    # 2. Persist to DB
    url = get_surreal_url()
    
    # Upsert Logic
    q = f"""
    USE NS {SURREAL_NS} DB {SURREAL_DB};
    LET $key = '{key}';
    LET $val = '{update.value}';
    LET $existing = (SELECT id FROM config_state WHERE key = $key);
    IF count($existing) > 0 THEN
        UPDATE config_state SET value = $val, last_updated = time::now() WHERE key = $key;
    ELSE
        CREATE config_state SET key = $key, value = $val, source = 'api', last_updated = time::now();
    END;
    """
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                 url,
                 content=q,
                 auth=(SURREAL_USER, SURREAL_PASS),
                 headers={"Accept": "application/json", "NS": SURREAL_NS, "DB": SURREAL_DB}
            )
            if resp.status_code != 200:
                logger.error(f"DB Config Write Failed: {resp.text}")
                return {"status": "memory_error", "key": key, "value": update.value}
            
            return {"status": "updated", "key": key, "value": update.value}

    except Exception as e:
        logger.error(f"DB Config Write Exception: {e}")
        # We updated memory, so we return partial success?
        return {"status": "updated_memory_only", "warning": str(e), "key": key, "value": update.value}
