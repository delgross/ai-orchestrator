import time
import uuid
import logging
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from router import config
from router.config import state

logger = logging.getLogger("router.middleware")

def require_auth(request: Request) -> None:
    """Authenticate incoming requests based on ROUTER_AUTH_TOKEN.
    Checks config.ROUTER_AUTH_TOKEN first, then falls back to router.router.ROUTER_AUTH_TOKEN.
    """
    # 1. Primary token from config (standard for refactored tests)
    auth_token = getattr(config, "ROUTER_AUTH_TOKEN", "")

    # 2. Fallback to router.router (entry point often monkeypatched in older tests)
    if not auth_token:
        try:
            import importlib
            router_mod = importlib.import_module("router.router")
            auth_token = getattr(router_mod, "ROUTER_AUTH_TOKEN", "")
        except Exception:
            pass

    # 3. If no token is set, authentication is disabled
    if not auth_token:
        return

    auth = request.headers.get("authorization")
    if not auth or not auth.lower().startswith("bearer "):
        logger.warning(f"Auth failed: missing bearer token. Header: '{auth[:50] if auth else 'None'}'")
        raise HTTPException(status_code=401, detail={"error": "Missing or invalid authorization header"})

    token = auth.split(" ", 1)[1].strip()
    
    if token != auth_token:
        logger.warning(f"Auth failed: Token mismatch (Expected len={len(auth_token)}, Got len={len(token)})")
        raise HTTPException(status_code=403, detail="invalid token")

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        start_time = time.time()
        try:
            response = await call_next(request)
            duration_ms = round((time.time() - start_time) * 1000, 2)
            # Update global stats
            state.request_count += 1
            state.total_response_time_ms += duration_ms
            state.request_by_status[response.status_code] = state.request_by_status.get(response.status_code, 0) + 1
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration_ms}ms"
            return response
        except Exception as e:
            state.error_count += 1
            raise e

