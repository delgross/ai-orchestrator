import os
import yaml
import logging
import time
import json
from typing import Any, Dict, List, Optional
from fastapi import HTTPException
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception, before_sleep_log

logger = logging.getLogger("router.providers")

# Mirascope imports for enhanced LLM interactions
try:
    from mirascope import llm
    MIRASCOPE_AVAILABLE = True
    logger.info("Mirascope available - enhanced LLM interactions enabled")
except ImportError:
    MIRASCOPE_AVAILABLE = False
    logger.warning("Mirascope not available - falling back to direct HTTP calls")

from router.config import Provider, state, PROVIDERS_YAML, DEFAULT_UPSTREAM_HEADERS, OLLAMA_BASE, PREFIX_OLLAMA, OBJ_CHAT_COMPLETION, ROLE_ASSISTANT, OBJ_CHAT_COMPLETION_CHUNK
from router.utils import join_url, parse_default_headers, merge_headers

# Retry predicate for 429s (Rate Limits)
def is_rate_limit_error(e: Exception) -> bool:
    if isinstance(e, HTTPException) and e.status_code == 429:
        return True
    return False

# Custom waiter that respects Retry-After headers
def wait_retry_after_header(retry_state) -> float:
    """
    Parse Retry-After header from HTTP response and wait accordingly.
    Falls back to exponential backoff if header is missing or invalid.
    """
    from datetime import datetime
    from email.utils import parsedate_to_datetime
    
    # Default exp backoff
    exp = wait_exponential(multiplier=1, min=2, max=10)
    default_wait = exp(retry_state)
    
    last_exc = retry_state.outcome.exception()
    if isinstance(last_exc, HTTPException) and last_exc.status_code == 429:
        # Try to extract Retry-After from exception detail
        # Format: detail can be a dict with retry_after, or a string with JSON
        retry_after_value = None
        
        if isinstance(last_exc.detail, dict):
            retry_after_value = last_exc.detail.get("retry_after")
        elif isinstance(last_exc.detail, str):
            try:
                import json
                detail_dict = json.loads(last_exc.detail)
                if isinstance(detail_dict, dict):
                    retry_after_value = detail_dict.get("retry_after")
            except (json.JSONDecodeError, ValueError):
                pass
        
        if retry_after_value:
            try:
                # Try as seconds (integer or float)
                wait_seconds = float(retry_after_value)
                if wait_seconds > 0:
                    logger.debug(f"Using Retry-After header: {wait_seconds} seconds")
                    return min(wait_seconds, 300)  # Cap at 5 minutes
            except (ValueError, TypeError):
                try:
                    # Try as HTTP date string
                    dt = parsedate_to_datetime(retry_after_value)
                    now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
                    wait_seconds = (dt - now).total_seconds()
                    if wait_seconds > 0:
                        logger.debug(f"Using Retry-After header (date): {wait_seconds} seconds")
                        return min(wait_seconds, 300)  # Cap at 5 minutes
                except (ValueError, TypeError):
                    pass
    
    # Fallback to exponential backoff
    return default_wait

retry_policy = retry(
    retry=retry_if_exception(is_rate_limit_error),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=2, min=4, max=60), # Increased aggression on the wait (slower retry)
    before_sleep=before_sleep_log(logger, logging.WARNING)
)

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

# Local Model Handlers
# helper to flatten content
def flatten_content(c: Any) -> str:
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        # Join text parts, ignore images for Ollama (unless using llava, but for now we assume text-only fallback)
        parts = []
        for item in c:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(item.get("text", ""))
            elif isinstance(item, str):
                parts.append(item)
        return "\n".join(parts)
    return str(c)

# Mirascope-enhanced LLM calling functions
if MIRASCOPE_AVAILABLE:
    from pydantic import BaseModel

    class OllamaChatResponse(BaseModel):
        content: str
        done: bool = True
        model: str = ""
        total_duration: int = 0
        load_duration: int = 0
        prompt_eval_count: int = 0
        prompt_eval_duration: int = 0
        eval_count: int = 0
        eval_duration: int = 0

    @llm.call(provider="ollama", model=os.getenv("AGENT_MODEL"), stream=True)
    async def mirascope_ollama_stream(
        messages: List[Dict[str, Any]],
        model: str = os.getenv("AGENT_MODEL"),
        num_ctx: Optional[int] = None,
        **kwargs
    ):
        """Mirascope-enhanced Ollama streaming call."""
        # Convert messages to simple format for Mirascope
        prompt = ""
        for msg in messages:
            role = msg.get("role", "")
            content = flatten_content(msg.get("content", ""))
            if role == "system":
                prompt += f"System: {content}\n\n"
            elif role == "user":
                prompt += f"User: {content}\n\n"
            elif role == "assistant":
                prompt += f"Assistant: {content}\n\n"

        # Add model options if specified
        options = {}
        if num_ctx:
            options["num_ctx"] = num_ctx

        return prompt

    @llm.call(provider="ollama", model=os.getenv("AGENT_MODEL"), response_model=OllamaChatResponse)
    async def mirascope_ollama_call(
        messages: List[Dict[str, Any]],
        model: str = os.getenv("AGENT_MODEL"),
        num_ctx: Optional[int] = None,
        **kwargs
    ) -> OllamaChatResponse:
        """Mirascope-enhanced Ollama call with structured response."""
        # Convert messages to prompt format
        prompt = ""
        for msg in messages:
            role = msg.get("role", "")
            content = flatten_content(msg.get("content", ""))
            if role == "system":
                prompt += f"System: {content}\n\n"
            elif role == "user":
                prompt += f"User: {content}\n\n"
            elif role == "assistant":
                prompt += f"Assistant: {content}\n\n"

        return prompt

# Configuration flag for Mirascope usage
USE_MIRASCOPE = os.getenv("USE_MIRASCOPE", "false").lower() == "true"

async def call_ollama_chat_stream(
    model_id: str,
    messages: List[Dict[str, Any]],
    request_id: str,
    num_ctx: Optional[int] = None,
    **kwargs
):
    """Yields OpenAI-compatible SSE chunks from Ollama stream."""

    # Use Mirascope if enabled and available
    if USE_MIRASCOPE and MIRASCOPE_AVAILABLE:
        try:
            logger.info(f"Using Mirascope for Ollama streaming call: {model_id}")
            async for chunk in mirascope_ollama_stream(messages, model=model_id, num_ctx=num_ctx):
                # Convert Mirascope chunk format to OpenAI-compatible format
                if hasattr(chunk, 'content') and chunk.content:
                    yield {
                        "id": f"mirascope-{int(time.time())}",
                        "object": OBJ_CHAT_COMPLETION_CHUNK,
                        "created": int(time.time()),
                        "model": f"{PREFIX_OLLAMA}:{model_id}",
                        "choices": [{"index": 0, "delta": {"content": chunk.content}, "finish_reason": None}]
                    }
                elif hasattr(chunk, 'done') and chunk.done:
                    yield {
                        "id": f"mirascope-{int(time.time())}",
                        "object": OBJ_CHAT_COMPLETION_CHUNK,
                        "created": int(time.time()),
                        "model": f"{PREFIX_OLLAMA}:{model_id}",
                        "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]
                    }
            return
        except Exception as e:
            logger.warning(f"Mirascope streaming failed, falling back to direct HTTP: {e}")
            # Fall through to original implementation

    # Original implementation as fallback
    url = join_url(OLLAMA_BASE, "/api/chat")
    
    ollama_body = {
        "model": model_id,
        "messages": [{"role": m.get("role"), "content": flatten_content(m.get("content", ""))} for m in messages],
        "stream": True,
    }
    
    # [PATCH] Merge top-level kwargs (like keep_alive)
    ollama_body.update(kwargs)
    
    # [Optimization] Smart Context Sizing (Gateway Level)
    # Ensure the Gateway respects VRAM constraints even if the client didn't specify limits.
    CONTEXT_WINDOW_MAP = {
        "llama3.3:70b": 32768,      # Brain (Deep Context)
        "ollama:llama3.3:70b": 32768,
        "qwen2.5:32b": 8192,        # Auditor (Medium Context)
        "ollama:qwen2.5:32b": 8192,
        "llama3.1:latest": 2048,    # Router (Transactional)
        "ollama:llama3.1:latest": 2048,
        "llama3.2:latest": 2048,    # Small Tasks (Transactional)
        "ollama:llama3.2:latest": 2048,
        "llama3.2-vision:latest": 2048, # Vision (Transactional)
        "ollama:llama3.2-vision:latest": 2048,
        "qwen2.5:7b-instruct": 2048, # Query Refinement (Transactional)
        "ollama:qwen2.5:7b-instruct": 2048,
    }
    
    # Priority: 1. Request Options (num_ctx) -> 2. Map -> 3. Global Env -> 4. Default 2048
    options = {}
    base_ctx = CONTEXT_WINDOW_MAP.get(model_id, CONTEXT_WINDOW_MAP.get(f"ollama:{model_id}"))
    
    # Priority: 1. Request Options (num_ctx) -> 2. Map -> 3. Global Env -> 4. Default 2048
    options = {}
    base_ctx = CONTEXT_WINDOW_MAP.get(model_id, CONTEXT_WINDOW_MAP.get(f"ollama:{model_id}"))
    
    # Use request-provided ctx, or map, or global default
    ctx_size = num_ctx or base_ctx or state.ollama_num_ctx
    
    logger.warning(f"🔍 [CTX_DEBUG] Stream Call: Model='{model_id}' | MapCtx={base_ctx} | ReqCtx={num_ctx} | Final={ctx_size}")

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
        async with state.client.stream("POST", url, json=ollama_body, headers={"Content-Type": "application/json"}, timeout=300.0) as r:
            if r.status_code >= 400:
                state.circuit_breakers.record_failure("ollama")
                content = await r.aread()
                raise HTTPException(status_code=r.status_code, detail=content.decode())
            
            state.circuit_breakers.record_success("ollama")
            
            # OpenAI Chunk Envelope
            chunk_id = f"ollama-{int(time.time())}"
            
            async for line in r.aiter_lines():
                if not line.strip(): continue
                
                try:
                    data = json.loads(line)
                    if data.get("done"):
                        # Final chunk with finish reason
                        usage = {
                            "prompt_tokens": data.get("prompt_eval_count", 0),
                            "completion_tokens": data.get("eval_count", 0),
                            "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
                        }
                        
                        yield {
                            "id": chunk_id,
                            "object": OBJ_CHAT_COMPLETION_CHUNK,
                            "created": int(time.time()),
                            "model": f"{PREFIX_OLLAMA}:{model_id}",
                            "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
                            "usage": usage
                        }
                        break
                    
                    content = data.get("message", {}).get("content", "")
                    if content:
                        yield {
                            "id": chunk_id,
                            "object": OBJ_CHAT_COMPLETION_CHUNK,
                            "created": int(time.time()),
                            "model": f"{PREFIX_OLLAMA}:{model_id}",
                            "choices": [{"index": 0, "delta": {"content": content}, "finish_reason": None}]
                        }
                except Exception as e:
                    logger.warning(f"Failed to parse Ollama stream line: {e}")
                    continue

    except Exception as e:
        state.circuit_breakers.record_failure("ollama")
        logger.error(f"Ollama stream call failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def call_ollama_chat(
    model_id: str,
    messages: List[Dict[str, Any]],
    request_id: str,
    num_ctx: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:

    # Use Mirascope if enabled and available
    if USE_MIRASCOPE and MIRASCOPE_AVAILABLE:
        try:
            logger.info(f"Using Mirascope for Ollama call: {model_id}")
            response = await mirascope_ollama_call(messages, model=model_id, num_ctx=num_ctx)

            # Convert Mirascope response to OpenAI-compatible format
            return {
                "id": f"mirascope-{int(time.time())}",
                "object": OBJ_CHAT_COMPLETION,
                "created": int(time.time()),
                "model": f"{PREFIX_OLLAMA}:{model_id}",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": ROLE_ASSISTANT,
                        "content": response.content if hasattr(response, 'content') else str(response)
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": getattr(response, 'prompt_eval_count', 0),
                    "completion_tokens": getattr(response, 'eval_count', 0),
                    "total_tokens": getattr(response, 'prompt_eval_count', 0) + getattr(response, 'eval_count', 0)
                }
            }
        except Exception as e:
            logger.warning(f"Mirascope call failed, falling back to direct HTTP: {e}")
            # Fall through to original implementation

    # Original implementation as fallback
    url = join_url(OLLAMA_BASE, "/api/chat")
    
    ollama_body = {
        "model": model_id,
        "messages": [{"role": m.get("role"), "content": flatten_content(m.get("content", ""))} for m in messages],
        "stream": False,
    }
    
    # [PATCH] Merge top-level kwargs (like keep_alive)
    ollama_body.update(kwargs)
    
    # [Optimization] Smart Context Sizing (Gateway Level)
    CONTEXT_WINDOW_MAP = {
        "llama3.3:70b": 32768,      # Brain (Deep Context)
        "ollama:llama3.3:70b": 32768,
        "qwen2.5:32b": 8192,        # Auditor (Medium Context)
        "ollama:qwen2.5:32b": 8192,
        "llama3.1:latest": 2048,    # Router (Transactional)
        "ollama:llama3.1:latest": 2048,
        "llama3.2:latest": 2048,    # Small Tasks (Transactional)
        "ollama:llama3.2:latest": 2048,
        "llama3.2-vision:latest": 2048, # Vision (Transactional)
        "ollama:llama3.2-vision:latest": 2048,
        "qwen2.5:7b-instruct": 2048, # Query Refinement (Transactional)
        "ollama:qwen2.5:7b-instruct": 2048,
    }
    
    options = {}
    base_ctx = CONTEXT_WINDOW_MAP.get(model_id, CONTEXT_WINDOW_MAP.get(f"ollama:{model_id}"))
    
    ctx_size = num_ctx or base_ctx or state.ollama_num_ctx
    
    logger.warning(f"🔍 [CTX_DEBUG] Sync Call: Model='{model_id}' | MapCtx={base_ctx} | ReqCtx={num_ctx} | Final={ctx_size}")

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
    except HTTPException:
        raise
    except Exception as e:
        state.circuit_breakers.record_failure("ollama")
        logger.error(f"Ollama call failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    msg_obj = j.get("message", {})
    if isinstance(msg_obj, dict):
        content = msg_obj.get("content", "")
    else:
        # Fallback if message is string or other
        content = str(msg_obj)
    
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
