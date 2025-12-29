import os
import yaml
import logging
import time
from typing import Any, Dict, List, Optional
from fastapi import HTTPException
from router.config import Provider, state, PROVIDERS_YAML, DEFAULT_UPSTREAM_HEADERS, OLLAMA_BASE, PREFIX_OLLAMA, OBJ_CHAT_COMPLETION, ROLE_ASSISTANT
from router.utils import join_url, parse_default_headers, merge_headers

logger = logging.getLogger("router.providers")

def provider_headers(prov: Provider) -> Dict[str, str]:
    headers: Dict[str, str] = {}
    key = prov.api_key()
    if key:
        headers["Authorization"] = f"Bearer {key}"
    headers = merge_headers(parse_default_headers(DEFAULT_UPSTREAM_HEADERS), prov.default_headers, headers)
    return headers

def load_providers() -> Dict[str, Provider]:
    path = os.path.expanduser(PROVIDERS_YAML)
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
    except FileNotFoundError:
        logger.warning(f"Providers YAML not found: {path}")
        return {}
    except Exception as e:
        logger.error(f"Failed to parse providers yaml: {e}")
        return {}

    data = raw.get("providers") if isinstance(raw, dict) and "providers" in raw else raw
    if not isinstance(data, dict):
        return {}

    out: Dict[str, Provider] = {}
    for name, cfg in data.items():
        if not isinstance(cfg, dict):
            continue
        ptype = str(cfg.get("type", "openai-compat"))
        base_url = str(cfg.get("base_url", "")).rstrip("/")
        if not base_url:
            continue
        
        out[str(name)] = Provider(
            name=str(name),
            ptype=ptype,
            base_url=base_url,
            api_key_env=cfg.get("api_key_env"),
            default_headers=cfg.get("default_headers") if isinstance(cfg.get("default_headers"), dict) else None,
            chat_path=str(cfg.get("chat_path", "/chat/completions")),
            models_path=str(cfg.get("models_path", "/models")),
            embeddings_path=str(cfg.get("embeddings_path", "/embeddings")),
        )
    return out

async def call_ollama_chat(
    model_id: str,
    messages: List[Dict[str, Any]],
    request_id: str,
    num_ctx: Optional[int] = None
) -> Dict[str, Any]:
    url = join_url(OLLAMA_BASE, "/api/chat")
    ollama_body = {
        "model": model_id,
        "messages": [{"role": m.get("role"), "content": m.get("content", "")} for m in messages],
        "stream": False,
    }
    
    options = {}
    ctx_size = num_ctx or state.ollama_num_ctx
    if ctx_size:
        options["num_ctx"] = ctx_size
    
    if state.ollama_model_options:
        model_opts = state.ollama_model_options.get(model_id, state.ollama_model_options.get("default", {}))
        for k, v in model_opts.items():
            if k not in options:
                options[k] = v
            
    if options:
        ollama_body["options"] = options

    if not state.circuit_breakers.is_allowed("ollama"):
        raise HTTPException(status_code=503, detail="Ollama service is currently disabled via circuit breaker")

    try:
        r = await state.client.post(url, json=ollama_body, headers={"Content-Type": "application/json"})
        if r.status_code >= 400:
            state.circuit_breakers.record_failure("ollama")
            raise HTTPException(status_code=r.status_code, detail=r.text)
        
        state.circuit_breakers.record_success("ollama")
        j = r.json()
    except Exception as e:
        state.circuit_breakers.record_failure("ollama")
        logger.error(f"Ollama call failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    content = j.get("message", {}).get("content", "")
    
    usage = {
        "prompt_tokens": j.get("prompt_eval_count", 0),
        "completion_tokens": j.get("eval_count", 0),
        "total_tokens": j.get("prompt_eval_count", 0) + j.get("eval_count", 0)
    }
    
    now = int(time.time())
    return {
        "id": f"ollama-{now}",
        "object": OBJ_CHAT_COMPLETION,
        "created": now,
        "model": f"{PREFIX_OLLAMA}:{model_id}",
        "choices": [{"index": 0, "message": {"role": ROLE_ASSISTANT, "content": content}, "finish_reason": "stop"}],
        "usage": usage
    }
