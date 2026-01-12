import asyncio
import logging
import time

from fastapi import APIRouter, Request
from common.constants import (
    PREFIX_AGENT, PREFIX_OLLAMA,
    OBJ_MODEL, OBJ_LIST,
    MODEL_AGENT_MCP, MODEL_ROUTER
)
from router.config import state, OLLAMA_BASE, MODELS_CACHE_TTL_S
from router.utils import join_url
from router.providers import provider_headers
from router.agent_manager import get_agent_models
from router.middleware import require_auth

router = APIRouter(tags=["models"])
logger = logging.getLogger("router.models")

@router.get("/v1/models")
async def v1_models(request: Request):
    require_auth(request)
    # Cache logic
    ts, cached = state.models_cache
    if cached and (time.time() - ts) < MODELS_CACHE_TTL_S:
        state.cache_hits += 1
        return cached
    
    state.cache_misses += 1
    data = []
    
    now = int(time.time())
    
    # Helper for compliant structure
    def make_model(mid, owner):
        return {
            "id": mid, 
            "object": OBJ_MODEL, 
            "created": now, 
            "owned_by": owner,
            "permission": [],
            "root": mid,
            "parent": None
        }

    # 1. Base models
    data.append(make_model(MODEL_AGENT_MCP, "agent_runner"))
    data.append(make_model(MODEL_ROUTER, "router"))
    
    # 2. Agent Runner models
    agent_models = await get_agent_models()
    for m in agent_models:
        m_id = m.get("id", "")
        if not m_id.startswith(f"{PREFIX_AGENT}:"):
            m["id"] = f"{PREFIX_AGENT}:{m_id}"
        data.append(m)
        
    # 3. Ollama models
    try:
        r = await state.client.get(f"{OLLAMA_BASE}/api/tags", timeout=3.0)
        if r.status_code == 200:
            for m in r.json().get("models", []):
                name = m.get("name", "")
                data.append({"id": f"{PREFIX_OLLAMA}:{name}", "object": OBJ_MODEL, "owned_by": "ollama"})
    except Exception:
        pass

    # 4. Providers
    async def fetch_provider_models(p_name, p):
        try:
            url = join_url(p.base_url, p.models_path)
            logger.warning(f"🔍 FETCHING models from {p_name} at {url}")

            # Check if API key is available
            api_key = p.api_key()
            logger.warning(f"🔑 API key for {p_name}: {'Available' if api_key else 'NOT FOUND'}")

            # Increased timeout for remote APIs
            r = await state.client.get(url, headers=provider_headers(p), timeout=15.0)

            logger.warning(f"📡 Provider {p_name} response status: {r.status_code}")
            if r.status_code != 200:
                logger.warning(f"❌ Response body: {r.text[:200]}")

            if r.status_code == 200:
                response_data = r.json()
                p_models = response_data.get("data", [])
                logger.info(f"Successfully fetched {len(p_models)} models from {p_name}")
                return [{"id": f"{p_name}:{m.get('id', '')}", "object": OBJ_MODEL, "owned_by": p_name} for m in p_models]
            elif r.status_code == 401:
                logger.warning(f"Authentication failed for provider {p_name} - check API keys")
            elif r.status_code == 403:
                logger.warning(f"Access forbidden for provider {p_name}")
            else:
                logger.warning(f"Unexpected status {r.status_code} from provider {p_name}")

        except asyncio.TimeoutError:
            logger.warning(f"Timeout fetching models from provider {p_name} (15s)")
        except Exception as e:
            logger.warning(f"Failed to fetch models for provider {p_name}: {e}")

        # Return empty list on failure - don't break the entire models list
        return []

    provider_tasks = [fetch_provider_models(name, prov) for name, prov in state.providers.items()]
    provider_results = await asyncio.gather(*provider_tasks)
    for res in provider_results:
        data.extend(res)
    
    payload = {"object": OBJ_LIST, "data": data}
    state.models_cache = (time.time(), payload)
    return payload
