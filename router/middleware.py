import time
import uuid
import logging
from typing import Any
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from router import config
from router.config import state

logger = logging.getLogger("router.middleware")

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

def require_auth(request: Request) -> None:
    if not config.ROUTER_AUTH_TOKEN:
        return
    auth = request.headers.get("authorization")
    if not auth or not auth.lower().startswith("bearer "):
        print(f"DEBUG: Auth Header: {auth}"); raise HTTPException(status_code=401, detail="missing bearer token")
    token = auth.split(" ", 1)[1].strip()
    if token != config.ROUTER_AUTH_TOKEN:
        raise HTTPException(status_code=403, detail="invalid token")
