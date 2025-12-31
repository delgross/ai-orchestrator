import time
import logging
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from router.config import state, VERSION, OLLAMA_BASE
from router.agent_manager import check_agent_runner_health
from router.middleware import require_auth

router = APIRouter()
logger = logging.getLogger("router.misc")

@router.get("/")
async def root(request: Request):
    # Return JSON health info when client explicitly requests JSON
    accept = request.headers.get("accept", "")
    if "application/json" in accept.lower():
        return {"ok": True, "version": VERSION}
    # Default: redirect to dashboard UI
    return RedirectResponse(url="/v2/index.html")

@router.get("/dashboard")
async def dashboard_redirect():
    """Redirect /dashboard to the UI index page."""
    return RedirectResponse(url="/v2/index.html")

@router.get("/sw.js")
async def service_worker_killer():
    """Serve a self-destructing Service Worker."""
    content = """
    self.addEventListener('install', function(e) {
        self.skipWaiting();
    });
    self.addEventListener('activate', function(e) {
        self.registration.unregister()
            .then(function() { return self.clients.matchAll(); })
            .then(function(clients) {
                clients.forEach(client => client.navigate(client.url));
            });
    });
    """
    return HTMLResponse(content, media_type="application/javascript")

@router.get("/health")
async def health(request: Request):
    ollama_ok = False
    try:
        r = await state.client.get(f"{OLLAMA_BASE}/api/tags", timeout=2.0)
        ollama_ok = r.status_code < 400
    except Exception:
        pass
    
    agent_ok = await check_agent_runner_health()
    overall_ok = ollama_ok and agent_ok
    
    return {
        "status": "healthy" if overall_ok else "degraded",
        "ok": overall_ok,
        "services": {
            "router": {"ok": True, "version": VERSION},
            "ollama": {"ok": ollama_ok},
            "agent_runner": {"ok": agent_ok},
        }
    }

@router.get("/stats")
async def stats(request: Request):
    require_auth(request)
    return {
        "uptime_s": round(time.time() - state.started_at, 2),
        "requests": state.request_count,
        "errors": state.error_count,
        "avg_response_time_ms": round(state.total_response_time_ms / max(1, state.request_count), 2),
        "cache": {
            "hits": state.cache_hits,
            "misses": state.cache_misses
        },
        "providers": state.provider_requests,
        "status_codes": state.request_by_status
    }
