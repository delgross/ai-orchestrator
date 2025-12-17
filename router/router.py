from __future__ import annotations

import asyncio
import json
import os
import time
import uuid
from dataclasses import dataclass
from typing import Any, AsyncIterator, Dict, List, Optional, Tuple
from contextlib import asynccontextmanager
import logging
from logging.handlers import RotatingFileHandler

import httpx
import yaml
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse, RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

VERSION = "0.7.2"

PROVIDERS_YAML = os.getenv("PROVIDERS_YAML", os.path.expanduser("~/ai/providers.yaml"))
OLLAMA_BASE = os.getenv("OLLAMA_BASE", "http://127.0.0.1:11434").rstrip("/")

# Optional RAG backend (treated as a dedicated provider prefix "rag").
RAG_BASE = os.getenv("RAG_BASE", "http://127.0.0.1:5555").rstrip("/")
RAG_QUERY_PATH = os.getenv("RAG_QUERY_PATH", "/query")

AGENT_RUNNER_URL = os.getenv("AGENT_RUNNER_URL", "http://127.0.0.1:5460").rstrip("/")
if AGENT_RUNNER_URL.endswith("/v1/chat/completions"):
    AGENT_RUNNER_URL = AGENT_RUNNER_URL[: -len("/v1/chat/completions")].rstrip("/")
elif AGENT_RUNNER_URL.endswith("/v1"):
    AGENT_RUNNER_URL = AGENT_RUNNER_URL[: -len("/v1")].rstrip("/")
AGENT_RUNNER_CHAT_PATH = os.getenv("AGENT_RUNNER_CHAT_PATH", "/v1/chat/completions")

MODELS_CACHE_TTL_S = float(os.getenv("MODELS_CACHE_TTL_S", "600"))
HTTP_TIMEOUT_S = float(os.getenv("HTTP_TIMEOUT_S", "120"))
MAX_REQUEST_BODY_BYTES = int(os.getenv("MAX_REQUEST_BODY_BYTES", "5_000_000"))
DEFAULT_UPSTREAM_HEADERS = os.getenv("DEFAULT_UPSTREAM_HEADERS", "")

# Simple LAN protection: optional bearer token and concurrency limit.
ROUTER_AUTH_TOKEN = os.getenv("ROUTER_AUTH_TOKEN") or ""
ROUTER_MAX_CONCURRENCY = int(os.getenv("ROUTER_MAX_CONCURRENCY", "0"))


@dataclass
class Provider:
    name: str
    ptype: str
    base_url: str
    api_key_env: Optional[str] = None
    default_headers: Optional[Dict[str, str]] = None
    chat_path: str = "/chat/completions"
    models_path: str = "/models"

    def api_key(self) -> Optional[str]:
        if not self.api_key_env:
            return None
        v = os.getenv(self.api_key_env)
        return v if v else None


class State:
    def __init__(self) -> None:
        self.started_at = time.time()
        # trust_env=False avoids proxy env vars hijacking localhost calls
        # Configure connection pooling for better performance
        # Connection reuse significantly improves performance for multiple requests
        self.client = httpx.AsyncClient(
            timeout=HTTP_TIMEOUT_S,
            trust_env=False,
            limits=httpx.Limits(
                max_keepalive_connections=20,  # Reuse connections (faster subsequent requests)
                max_connections=100,           # Max concurrent connections
                keepalive_expiry=30.0          # Keep connections alive for 30s
            )
            # Note: http2=True can be enabled if providers support it
            # Some providers may not support HTTP/2, so leaving it disabled for compatibility
        )
        self.providers: Dict[str, Provider] = {}
        self.models_cache: Tuple[float, Dict[str, Any]] = (0.0, {})
        self.semaphore = asyncio.Semaphore(ROUTER_MAX_CONCURRENCY) if ROUTER_MAX_CONCURRENCY > 0 else None
        
        # Statistics tracking
        self.request_count = 0
        self.error_count = 0
        self.total_response_time_ms = 0.0
        self.request_by_method: Dict[str, int] = {}
        self.request_by_path: Dict[str, int] = {}
        self.request_by_status: Dict[int, int] = {}
        self.provider_requests: Dict[str, int] = {}
        self.cache_hits = 0
        self.cache_misses = 0


state = State()
app = FastAPI(title="router", version=VERSION)

# Configure logging to write to logs directory
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("router")
if not logger.handlers:
    # File handler with rotation (10MB max, keep 5 backups)
    log_file = os.path.join(LOG_DIR, "router.log")
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s router %(message)s")
    )
    logger.addHandler(file_handler)
    
    # Also log to console (stdout) for development
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s router %(message)s")
    )
    logger.addHandler(console_handler)

logger.setLevel(logging.INFO)
logger.propagate = False


# Request ID middleware - adds unique ID to each request for tracking
class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        start_time = time.time()
        
        # Log incoming request
        logger.info(
            f"[{request_id}] {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown",
            }
        )
        
        try:
            response = await call_next(request)
            duration_ms = round((time.time() - start_time) * 1000, 2)
            
            # Update statistics
            state.request_count += 1
            state.total_response_time_ms += duration_ms
            state.request_by_method[request.method] = state.request_by_method.get(request.method, 0) + 1
            state.request_by_path[request.url.path] = state.request_by_path.get(request.url.path, 0) + 1
            state.request_by_status[response.status_code] = state.request_by_status.get(response.status_code, 0) + 1
            if response.status_code >= 400:
                state.error_count += 1
            
            # Log response
            logger.info(
                f"[{request_id}] {request.method} {request.url.path} -> {response.status_code} ({duration_ms}ms)",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                }
            )
            
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration_ms}ms"
            return response
        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            state.request_count += 1
            state.error_count += 1
            state.total_response_time_ms += duration_ms
            state.request_by_method[request.method] = state.request_by_method.get(request.method, 0) + 1
            state.request_by_path[request.url.path] = state.request_by_path.get(request.url.path, 0) + 1
            
            logger.error(
                f"[{request_id}] {request.method} {request.url.path} -> ERROR ({duration_ms}ms): {str(e)}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                    "duration_ms": duration_ms,
                },
                exc_info=True
            )
            raise


app.add_middleware(RequestIDMiddleware)


def _log_json_event(event: str, request_id: Optional[str] = None, **fields: Any) -> None:
    """Emit a JSON_EVENT line for machine parsing."""
    try:
        payload = {"event": event, **fields}
        if request_id:
            payload["request_id"] = request_id
        logger.info("JSON_EVENT: %s", json.dumps(payload, ensure_ascii=False))
    except Exception:
        logger.debug("failed to log JSON_EVENT for %s", event)


def _parse_default_headers(env: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    env = env.strip()
    if not env:
        return out
    for part in env.split(","):
        part = part.strip()
        if not part or ":" not in part:
            continue
        k, v = part.split(":", 1)
        out[k.strip()] = v.strip()
    return out


def _merge_headers(*dicts: Optional[Dict[str, str]]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for d in dicts:
        if d:
            out.update(d)
    return out


def _provider_headers(prov: Provider) -> Dict[str, str]:
    headers: Dict[str, str] = {}
    key = prov.api_key()
    if key:
        headers["Authorization"] = f"Bearer {key}"
    headers = _merge_headers(_parse_default_headers(DEFAULT_UPSTREAM_HEADERS), prov.default_headers, headers)
    return headers


def _join_url(base: str, path: str) -> str:
    return base.rstrip("/") + "/" + path.lstrip("/")


def _ensure_messages_list(body: Dict[str, Any]) -> List[Dict[str, Any]]:
    msgs = body.get("messages", [])
    if not isinstance(msgs, list):
        raise HTTPException(status_code=400, detail="messages must be a list")
    out: List[Dict[str, Any]] = []
    for i, m in enumerate(msgs):
        if not isinstance(m, dict):
            raise HTTPException(status_code=400, detail=f"messages[{i}] must be an object")
        out.append(m)
    return out


def _sanitize_messages(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Preserve tool fields, but avoid null content triggering strict validators.
    out: List[Dict[str, Any]] = []
    for m in messages:
        mm = dict(m)
        if "content" in mm and mm["content"] is None:
            mm["content"] = ""
        out.append(mm)
    return out


def _require_auth(request: Request) -> None:
    """
    Lightweight bearer-token check. If ROUTER_AUTH_TOKEN is unset, auth is bypassed.
    """
    if not ROUTER_AUTH_TOKEN:
        return
    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    if not auth or not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    token = auth.split(" ", 1)[1].strip()
    if token != ROUTER_AUTH_TOKEN:
        raise HTTPException(status_code=403, detail="invalid token")


@asynccontextmanager
async def _noop_async_context():
    yield


def _parse_model(model: Any) -> Tuple[str, str]:
    if not isinstance(model, str) or not model.strip():
        raise HTTPException(status_code=400, detail="model must be a non-empty string")
    s = model.strip()
    if ":" in s:
        prefix, rest = s.split(":", 1)
        return prefix.strip(), rest.strip()
    return "ollama", s


async def _read_json_body(request: Request) -> Dict[str, Any]:
    b = await request.body()
    if len(b) > MAX_REQUEST_BODY_BYTES:
        raise HTTPException(status_code=413, detail="request too large")
    try:
        return json.loads(b.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="invalid JSON")


async def _stream_passthrough(method: str, url: str, headers: Dict[str, str], payload: Dict[str, Any]) -> AsyncIterator[bytes]:
    async with state.client.stream(method, url, headers=headers, json=payload) as r:
        if r.status_code >= 400:
            content = await r.aread()
            raise HTTPException(status_code=r.status_code, detail=content.decode("utf-8", errors="replace"))
        async for chunk in r.aiter_bytes():
            if chunk:
                yield chunk


def _sse_line(obj: Any) -> bytes:
    return (f"data: {json.dumps(obj, ensure_ascii=False)}\n\n").encode("utf-8")


def _handle_json_response(r: httpx.Response, default_status: int = 200) -> JSONResponse:
    """Helper to handle JSON or text responses from HTTP requests."""
    ct = r.headers.get("content-type", "")
    if ct.startswith("application/json"):
        return JSONResponse(status_code=r.status_code if r.status_code != 200 else default_status, content=r.json())
    return JSONResponse(status_code=r.status_code if r.status_code != 200 else default_status, content={"detail": r.text})


async def _call_ollama_chat(
    base_url: str,
    model_id: str,
    messages: List[Dict[str, Any]],
    request_id: str,
    provider_name: Optional[str] = None
) -> Dict[str, Any]:
    """Make a chat request to Ollama and return the parsed response."""
    url = _join_url(base_url, "/api/chat")
    ollama_body = {
        "model": model_id,
        "messages": [{"role": m.get("role"), "content": m.get("content", "")} for m in messages],
        "stream": False,  # we wrap streaming ourselves for LibreChat compatibility
    }
    r = await state.client.post(url, json=ollama_body, headers={"Content-Type": "application/json"})
    
    if r.status_code >= 400:
        _log_json_event("ollama_error", request_id=request_id, status_code=r.status_code, model=model_id)
        error_detail = r.text
        if r.status_code == 404:
            error_detail = f"Model '{model_id}' not found. Use /v1/models to list available models."
        elif r.status_code == 503:
            error_detail = "Ollama service is unavailable. Please check if Ollama is running."
        
        error_detail_dict = {
            "error": "Ollama request failed",
            "message": error_detail,
            "model": model_id,
            "suggestion": "Check that Ollama is running and the model is available."
        }
        if provider_name:
            error_detail_dict["provider"] = provider_name
        
        raise HTTPException(status_code=r.status_code, detail=error_detail_dict)
    
    # Parse Ollama response
    try:
        j = r.json()
    except Exception as e:
        _log_json_event("ollama_json_error", request_id=request_id, error=str(e), model=model_id)
        raise HTTPException(
            status_code=502,
            detail={
                "error": "Invalid JSON response from Ollama",
                "message": str(e),
                "model": model_id,
                "suggestion": "Ollama may be returning an error. Check Ollama logs."
            }
        )
    
    content = ""
    if isinstance(j, dict) and isinstance(j.get("message"), dict):
        c = j["message"].get("content")
        if isinstance(c, str):
            content = c
    
    # Build OpenAI-style response
    now = int(time.time())
    return {
        "id": f"ollama-{now}",
        "object": "chat.completion",
        "created": now,
        "model": f"{provider_name or 'ollama'}:{model_id}",
        "choices": [{"index": 0, "message": {"role": "assistant", "content": content}, "finish_reason": "stop"}],
    }


async def _sse_from_full_completion(full: Dict[str, Any], model: str) -> AsyncIterator[bytes]:
    """
    Convert a full OpenAI-style completion into a minimal OpenAI SSE stream:
      data: {chat.completion.chunk ...}
      data: [DONE]
    This is what LibreChat expects when stream=true.
    """
    now = int(time.time())
    cid = full.get("id") if isinstance(full.get("id"), str) else f"chatcmpl-{now}"
    content = ""

    try:
        choices = full.get("choices")
        if isinstance(choices, list) and choices:
            msg = choices[0].get("message") if isinstance(choices[0], dict) else None
            if isinstance(msg, dict):
                c = msg.get("content")
                if isinstance(c, str):
                    content = c
    except Exception:
        content = ""

    chunk = {
        "id": cid,
        "object": "chat.completion.chunk",
        "created": now,
        "model": model,
        "choices": [
            {"index": 0, "delta": {"role": "assistant", "content": content}, "finish_reason": "stop"}
        ],
    }
    yield _sse_line(chunk)
    yield b"data: [DONE]\n\n"


async def _call_rag(model: str, body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Minimal RAG stub: POST to RAG_BASE/RAG_QUERY_PATH with {model, messages}.
    Expects JSON {answer: str, context?: any}. Returns OpenAI-style completion.
    """
    url = _join_url(RAG_BASE, RAG_QUERY_PATH)
    payload = {
        "model": model,
        "messages": body.get("messages", []),
    }
    r = await state.client.post(url, json=payload, headers={"Content-Type": "application/json"})
    if r.status_code >= 400:
        _log_json_event("rag_error", status_code=r.status_code)
        raise HTTPException(status_code=r.status_code, detail=r.text)
    data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {"answer": r.text}
    content = data.get("answer") if isinstance(data, dict) else ""
    return {
        "id": f"rag-{int(time.time())}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": f"rag:{model}",
        "choices": [
            {"index": 0, "message": {"role": "assistant", "content": content}, "finish_reason": "stop"}
        ],
        "rag_context": data.get("context") if isinstance(data, dict) else None,
    }


def _load_providers() -> Dict[str, Provider]:
    """Load providers from YAML with validation."""
    path = os.path.expanduser(PROVIDERS_YAML)
    try:
        raw = yaml.safe_load(open(path, "r", encoding="utf-8")) or {}
    except FileNotFoundError:
        logger.warning(f"Providers YAML not found: {path}")
        return {}
    except Exception as e:
        logger.error(f"Failed to parse providers yaml: {e}")
        raise RuntimeError(f"Failed to parse providers yaml: {e}") from e

    data = raw.get("providers") if isinstance(raw, dict) and "providers" in raw else raw
    if not isinstance(data, dict):
        logger.warning("No providers section found in YAML")
        return {}

    out: Dict[str, Provider] = {}
    errors: List[str] = []
    
    for name, cfg in data.items():
        if not isinstance(cfg, dict):
            errors.append(f"Provider '{name}': config must be a dictionary")
            continue
            
        ptype = str(cfg.get("type", "openai_compat"))
        base_url = str(cfg.get("base_url", "")).rstrip("/")
        
        if not base_url:
            errors.append(f"Provider '{name}': missing or empty base_url")
            continue
            
        # Validate provider type
        valid_types = ["openai_compat", "ollama"]
        if ptype not in valid_types:
            errors.append(f"Provider '{name}': invalid type '{ptype}', must be one of {valid_types}")
            continue
        
        # Validate API key for non-ollama providers
        if ptype == "openai_compat" and not cfg.get("api_key_env"):
            logger.warning(f"Provider '{name}': no api_key_env specified (may fail if API key required)")
        
        try:
            out[str(name)] = Provider(
                name=str(name),
                ptype=ptype,
                base_url=base_url,
                api_key_env=cfg.get("api_key_env"),
                default_headers=cfg.get("default_headers") if isinstance(cfg.get("default_headers"), dict) else None,
                chat_path=str(cfg.get("chat_path", "/chat/completions")),
                models_path=str(cfg.get("models_path", "/models")),
            )
            logger.info(f"Loaded provider: {name} ({ptype})")
        except Exception as e:
            errors.append(f"Provider '{name}': failed to create - {e}")
    
    if errors:
        logger.warning(f"Provider validation errors: {'; '.join(errors)}")
    
    return out


@app.on_event("startup")
async def _startup() -> None:
    state.providers = _load_providers()


@app.on_event("shutdown")
async def _shutdown() -> None:
    await state.client.aclose()


@app.get("/dashboard")
async def dashboard() -> FileResponse:
    """Serve the dashboard HTML page."""
    dashboard_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dashboard", "index.html")
    return FileResponse(dashboard_path, media_type="text/html")


@app.get("/")
async def root(request: Request):
    """Root endpoint: redirect to dashboard for browsers, return JSON for API clients."""
    accept = request.headers.get("Accept", "")
    user_agent = request.headers.get("User-Agent", "")
    # Redirect if HTML is explicitly requested, or if it looks like a browser (has User-Agent but no JSON in Accept)
    is_browser = "text/html" in accept or (user_agent and "application/json" not in accept and not user_agent.startswith("curl") and not user_agent.startswith("httpie"))
    if is_browser:
        return RedirectResponse(url="/dashboard")
    # API client - return JSON
    return {
        "name": "router",
        "ok": True,
        "version": VERSION,
        "uptime_s": round(time.time() - state.started_at, 3),
        "ollama_base": OLLAMA_BASE,
        "agent_runner_url": AGENT_RUNNER_URL,
        "providers_loaded": sorted(list(state.providers.keys())),
        "providers_yaml": os.path.expanduser(PROVIDERS_YAML),
        "models_cache_ttl_s": MODELS_CACHE_TTL_S,
        "auth_enabled": bool(ROUTER_AUTH_TOKEN),
        "max_concurrency": ROUTER_MAX_CONCURRENCY if ROUTER_MAX_CONCURRENCY > 0 else None,
    }


@app.get("/health")
async def health(request: Request) -> Dict[str, Any]:
    """Enhanced health check endpoint with provider status."""
    # Check Ollama
    ollama_ok = False
    ollama_response_time = None
    try:
        start = time.time()
        r = await state.client.get(f"{OLLAMA_BASE}/api/tags", timeout=3.0)
        ollama_response_time = round((time.time() - start) * 1000, 2)
        ollama_ok = r.status_code < 400
    except Exception:
        ollama_ok = False
    
    # Check agent runner
    agent_ok = False
    agent_response_time = None
    try:
        start = time.time()
        r = await state.client.get(f"{AGENT_RUNNER_URL}/", timeout=3.0)
        agent_response_time = round((time.time() - start) * 1000, 2)
        if r.status_code < 400:
            data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
            agent_ok = data.get("ok", False)
    except Exception:
        agent_ok = False
    
    # Quick provider connectivity check (non-blocking, timeout quickly)
    provider_status = {}
    for name, prov in state.providers.items():
        if prov.ptype == "ollama":
            # Ollama already checked above
            provider_status[name] = {
                "reachable": ollama_ok, 
                "type": "ollama",
                "response_time_ms": ollama_response_time
            }
        elif prov.ptype == "openai_compat":
            # For OpenAI-compat, we can't easily test without making a real request
            # Just check if base_url is valid format
            provider_status[name] = {
                "reachable": None, 
                "type": "openai_compat", 
                "base_url": prov.base_url,
                "has_api_key": bool(prov.api_key())
            }
        else:
            provider_status[name] = {"reachable": None, "type": prov.ptype}
    
    # Health is based on router functionality, not provider count
    # Router can be healthy even with no providers configured
    overall_ok = ollama_ok and agent_ok
    
    return {
        "status": "healthy" if overall_ok else "degraded",
        "ok": overall_ok,
        "timestamp": int(time.time()),
        "uptime_s": round(time.time() - state.started_at, 3),
        "services": {
            "router": {"ok": True, "version": VERSION},
            "ollama": {"ok": ollama_ok, "base_url": OLLAMA_BASE, "response_time_ms": ollama_response_time},
            "agent_runner": {"ok": agent_ok, "url": AGENT_RUNNER_URL, "response_time_ms": agent_response_time},
        },
        "providers": {
            "count": len(state.providers),
            "loaded": sorted(list(state.providers.keys())),
            "status": provider_status,
        },
    }


@app.get("/stats")
async def stats(request: Request) -> Dict[str, Any]:
    """Get router statistics and metrics."""
    _require_auth(request)
    
    uptime_s = time.time() - state.started_at
    avg_response_time = state.total_response_time_ms / state.request_count if state.request_count > 0 else 0
    error_rate = (state.error_count / state.request_count * 100) if state.request_count > 0 else 0
    cache_hit_rate = (state.cache_hits / (state.cache_hits + state.cache_misses) * 100) if (state.cache_hits + state.cache_misses) > 0 else 0
    
    # Get connection pool stats
    pool_stats = {}
    try:
        # httpx doesn't expose pool stats directly, but we can infer from limits
        pool_stats = {
            "max_connections": state.client._limits.max_connections if hasattr(state.client, "_limits") else 100,
            "max_keepalive": state.client._limits.max_keepalive_connections if hasattr(state.client, "_limits") else 20,
        }
    except Exception:
        pass
    
    # Get cache info
    ts, cached = state.models_cache
    cache_age_s = time.time() - ts if ts > 0 else 0
    cache_valid = cached and cache_age_s < MODELS_CACHE_TTL_S
    
    return {
        "uptime_s": round(uptime_s, 2),
        "requests": {
            "total": state.request_count,
            "errors": state.error_count,
            "success": state.request_count - state.error_count,
            "error_rate_percent": round(error_rate, 2),
            "avg_response_time_ms": round(avg_response_time, 2),
            "total_response_time_ms": round(state.total_response_time_ms, 2),
        },
        "by_method": dict(sorted(state.request_by_method.items())),
        "by_path": dict(sorted(state.request_by_path.items(), key=lambda x: x[1], reverse=True)[:10]),  # Top 10
        "by_status": dict(sorted(state.request_by_status.items())),
        "providers": {
            "requests": dict(sorted(state.provider_requests.items(), key=lambda x: x[1], reverse=True)),
            "total_providers": len(state.providers),
        },
        "cache": {
            "hits": state.cache_hits,
            "misses": state.cache_misses,
            "hit_rate_percent": round(cache_hit_rate, 2),
            "models_cache": {
                "valid": cache_valid,
                "age_s": round(cache_age_s, 2),
                "ttl_s": MODELS_CACHE_TTL_S,
                "model_count": len(cached.get("data", [])) if cached else 0,
            },
        },
        "connection_pool": pool_stats,
        "concurrency": {
            "max": ROUTER_MAX_CONCURRENCY if ROUTER_MAX_CONCURRENCY > 0 else None,
            "current_available": state.semaphore._value if state.semaphore else None,
        },
    }


@app.post("/admin/reload")
async def admin_reload(request: Request) -> Dict[str, Any]:
    _require_auth(request)
    state.providers = _load_providers()
    state.models_cache = (0.0, {})
    return {"ok": True, "providers_loaded": sorted(list(state.providers.keys()))}


async def _fetch_openai_models(prov: Provider) -> List[Dict[str, Any]]:
    url = _join_url(prov.base_url, prov.models_path)
    r = await state.client.get(url, headers=_provider_headers(prov))
    if r.status_code >= 400:
        return []
    try:
        j = r.json()
    except Exception:
        return []
    data = j.get("data")
    if not isinstance(data, list):
        return []
    out: List[Dict[str, Any]] = []
    for m in data:
        if isinstance(m, dict) and isinstance(m.get("id"), str):
            out.append({"id": f"{prov.name}:{m['id']}", "object": "model", "owned_by": prov.name})
    return out


async def _fetch_ollama_models(base_url: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetch models from an Ollama instance. If base_url is None, uses OLLAMA_BASE."""
    url = _join_url(base_url or OLLAMA_BASE, "/api/tags")
    try:
        r = await state.client.get(url, timeout=5.0)
        if r.status_code >= 400:
            return []
        j = r.json()
        models = j.get("models")
        if not isinstance(models, list):
            return []
        out: List[Dict[str, Any]] = []
        for m in models:
            if isinstance(m, dict) and isinstance(m.get("name"), str):
                out.append({"id": f"ollama:{m['name']}", "object": "model", "owned_by": "ollama"})
        return out
    except Exception:
        return []


@app.get("/v1/models")
async def v1_models(request: Request) -> Dict[str, Any]:
    _require_auth(request)
    
    # Check cache first (outside lock for performance)
    ts, cached = state.models_cache
    now = time.time()
    if cached and (now - ts) < MODELS_CACHE_TTL_S:
        return cached

    # Use semaphore to prevent concurrent cache updates (if concurrency limit is set)
    # Otherwise, use a simple lock to prevent race conditions
    sem = state.semaphore
    lock_ctx = sem if sem else _noop_async_context()
    
    async with lock_ctx:
        # Check cache again after acquiring lock (another request may have updated it)
        ts, cached = state.models_cache
        if cached and (now - ts) < MODELS_CACHE_TTL_S:
            return cached
        
        # Track fetched URLs to avoid duplicates
        fetched_urls = set()
        tasks = []
        
        # Fetch Ollama models (from hardcoded OLLAMA_BASE for backward compatibility)
        if OLLAMA_BASE not in fetched_urls:
            fetched_urls.add(OLLAMA_BASE)
            tasks.append(_fetch_ollama_models())
        
        # Also fetch from any Ollama providers in providers.yaml (avoid duplicates)
        for prov in state.providers.values():
            if prov.ptype == "ollama":
                if prov.base_url not in fetched_urls:
                    fetched_urls.add(prov.base_url)
                    tasks.append(_fetch_ollama_models(prov.base_url))
            elif prov.ptype == "openai_compat":
                tasks.append(_fetch_openai_models(prov))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        data: List[Dict[str, Any]] = []
        for r in results:
            if isinstance(r, list):
                data.extend(r)

        # Add agent models
        data.append({"id": "agent:mcp", "object": "model", "owned_by": "agent_runner"})

        payload = {"object": "list", "data": data}
        state.models_cache = (now, payload)
        return payload


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    request_id = getattr(request.state, "request_id", "unknown")
    _require_auth(request)
    body = await _read_json_body(request)
    prefix, model_id = _parse_model(body.get("model"))
    
    # Validate model_id is not empty
    if not model_id or not model_id.strip():
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Model ID cannot be empty",
                "model": f"{prefix}:{model_id}",
                "suggestion": "Provide a valid model name after the provider prefix (e.g., 'ollama:llama2')"
            }
        )
    
    # Request logging is handled by RequestIDMiddleware

    msgs = _ensure_messages_list(body)
    body["messages"] = _sanitize_messages(msgs)

    stream = bool(body.get("stream", False))

    # Optional concurrency guard - protects ALL request types
    sem = state.semaphore
    lock_ctx = sem if sem else _noop_async_context()

    async with lock_ctx:
        # --- agent routing ---
        if prefix == "agent":
            url = _join_url(AGENT_RUNNER_URL, AGENT_RUNNER_CHAT_PATH)
            if stream:
                # agent-runner streaming is not guaranteed; wrap into OpenAI SSE
                b2 = dict(body)
                b2["stream"] = False
                r = await state.client.post(url, json=b2, headers={"Content-Type": "application/json"})
                if r.status_code >= 400:
                    _log_json_event("agent_runner_error", request_id=request_id, status_code=r.status_code)
                    return _handle_json_response(r)
                full = r.json() if r.headers.get("content-type", "").startswith("application/json") else {"choices": [{"message": {"content": r.text}}]}
                return StreamingResponse(_sse_from_full_completion(full, f"agent:{model_id}"), media_type="text/event-stream")

            r = await state.client.post(url, json=body, headers={"Content-Type": "application/json"})
            return _handle_json_response(r)

        # --- RAG routing ---
        if prefix == "rag":
            completion = await _call_rag(model_id, body)
            if stream:
                return StreamingResponse(_sse_from_full_completion(completion, f"rag:{model_id}"), media_type="text/event-stream")
            return JSONResponse(content=completion)

        # --- provider routing ---
        prov = state.providers.get(prefix)
        if not prov:
            # Fallback: check if it's hardcoded ollama (for backward compatibility)
            if prefix == "ollama":
                # Use hardcoded OLLAMA_BASE for backward compatibility
                full = await _call_ollama_chat(OLLAMA_BASE, model_id, body["messages"], request_id)
                if stream:
                    return StreamingResponse(_sse_from_full_completion(full, f"ollama:{model_id}"), media_type="text/event-stream")
                return JSONResponse(content=full)
            available = sorted(list(state.providers.keys()))
            raise HTTPException(
                status_code=400,
                detail={
                    "error": f"Unknown provider prefix: '{prefix}'",
                    "model": f"{prefix}:{model_id}",
                    "available_providers": available,
                    "suggestion": f"Use one of: {', '.join(available)}. Format: provider:model-name"
                }
            )
        
        # Handle Ollama provider type
        if prov.ptype == "ollama":
            state.provider_requests[prefix] = state.provider_requests.get(prefix, 0) + 1
            full = await _call_ollama_chat(prov.base_url, model_id, body["messages"], request_id, prefix)
            if stream:
                return StreamingResponse(_sse_from_full_completion(full, f"{prefix}:{model_id}"), media_type="text/event-stream")
            return JSONResponse(content=full)
        
        # Handle OpenAI-compatible providers
        if prov.ptype != "openai_compat":
            raise HTTPException(
                status_code=400,
                detail={
                    "error": f"Unsupported provider type: '{prov.ptype}'",
                    "provider": prov.name,
                    "model": f"{prefix}:{model_id}",
                    "supported_types": ["openai_compat", "ollama"],
                    "suggestion": f"Provider '{prov.name}' has unsupported type. Check providers.yaml configuration."
                }
            )

        state.provider_requests[prefix] = state.provider_requests.get(prefix, 0) + 1
        body["model"] = model_id
        url = _join_url(prov.base_url, prov.chat_path)

        headers = _provider_headers(prov)
        headers["Content-Type"] = "application/json"

        if stream:
            # pass through OpenAI-compatible SSE
            return StreamingResponse(_stream_passthrough("POST", url, headers, body), media_type="text/event-stream")

        r = await state.client.post(url, headers=headers, json=body)
        return _handle_json_response(r)
