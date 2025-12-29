"""
Observability Middleware for FastAPI

Provides automatic observability integration for all FastAPI applications.
This ensures consistent observability across all system components.
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from common.observability import (
    get_observability,
    RequestStage,
    ComponentType,
)

logger = logging.getLogger("observability_middleware")


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """
    Middleware that automatically tracks all requests with observability.
    
    This ensures every component using FastAPI gets consistent observability
    without manual integration.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        component_type: ComponentType,
        component_id: str,
        track_health_endpoints: bool = False,
    ):
        """
        Initialize observability middleware.
        
        Args:
            app: The ASGI application
            component_type: Type of component (ROUTER, AGENT_RUNNER, etc.)
            component_id: Unique identifier for this component instance
            track_health_endpoints: Whether to track health check endpoints (default: False)
        """
        super().__init__(app)
        self.component_type = component_type
        self.component_id = component_id
        self.track_health_endpoints = track_health_endpoints
        self.obs = get_observability()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with full observability tracking."""
        # Skip tracking for health endpoints unless explicitly enabled
        if not self.track_health_endpoints and request.url.path in ("/health", "/metrics", "/"):
            return await call_next(request)
        
        # Generate request ID if not present
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())[:8]
        
        # Store in request state for access by handlers
        request.state.request_id = request_id
        
        # Also set ContextVar if available (for router logging compatibility)
        try:
            # Try to get the router's request_id_var if it exists
            import sys
            router_module = sys.modules.get('router.router')
            if router_module and hasattr(router_module, 'request_id_var'):
                router_module.request_id_var.set(request_id)
        except Exception:
            # ContextVar not available or router module not loaded - continue without it
            pass
        
        # Start tracking
        lifecycle = await self.obs.start_request(
            request_id=request_id,
            method=request.method,
            path=str(request.url.path),
            metadata={
                "component_type": self.component_type.value,
                "component_id": self.component_id,
                "query_params": dict(request.query_params),
                "client": request.client.host if request.client else None,
            }
        )
        lifecycle.record_stage(RequestStage.RECEIVED)
        
        try:
            # Track auth check (if applicable)
            lifecycle.record_stage(RequestStage.AUTH_CHECKED)
            
            # Parse stage - minimize overhead
            lifecycle.record_stage(RequestStage.PARSED)
            
            # Process request
            lifecycle.record_stage(RequestStage.PROCESSING)
            process_start = time.time()
            
            response = await call_next(request)
            
            process_duration = (time.time() - process_start) * 1000
            lifecycle.add_metric(
                self.component_id,
                "process_request",
                process_duration,
                {"status_code": response.status_code}
            )
            
            # Record component health based on response (async, non-blocking)
            status = "healthy" if response.status_code < 500 else "unhealthy"
            # Don't await - let it run in background to avoid blocking response
            asyncio.create_task(self.obs.record_component_health(
                self.component_type,
                self.component_id,
                status,
                response_time_ms=process_duration,
                metadata={"status_code": response.status_code}
            ))
            
            # Add request ID to response
            response.headers["X-Request-ID"] = request_id
            
            lifecycle.record_stage(RequestStage.RESPONSE_SENT, {
                "status_code": response.status_code
            })
            
            return response
            
        except Exception as e:
            lifecycle.add_error(e, {
                "path": str(request.url.path),
                "method": request.method
            })
            # Don't await - let it run in background
            asyncio.create_task(self.obs.record_component_health(
                self.component_type,
                self.component_id,
                "unhealthy",
                metadata={"error": str(e)}
            ))
            raise
        finally:
            await self.obs.complete_request(request_id)

