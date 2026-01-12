import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from router.config import VERSION
from router.routes import router as api_router
from router.admin import router as admin_router
from router.middleware import RequestIDMiddleware
from common.observability import ComponentType
from common.observability_middleware import ObservabilityMiddleware

logger = logging.getLogger("router.app")

def create_app(lifespan=None) -> FastAPI:
    """FastAPI application factory for the Router."""
    app = FastAPI(title="router", version=VERSION, lifespan=lifespan)

    # Middleware
    app.add_middleware(RequestIDMiddleware)
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(
        ObservabilityMiddleware,
        component_type=ComponentType.ROUTER,
        component_id="router-main"
    )

    # Static Files: Dashboard removed as per user request (Jan 2026)
    # dashboard_v2_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dashboard", "v2")
    # if os.path.exists(dashboard_v2_path):
    #     app.mount("/v2", StaticFiles(directory=dashboard_v2_path), name="dashboard_v2")

    # Routers
    app.include_router(admin_router)
    app.include_router(api_router)
    
    # Internal Imports to prevent cycle if placed at top, or just standard import
    from router.routes.clients import router as clients_router
    app.include_router(clients_router)
    
    # System messages router (for pushing warnings/problems to chat)
    from router.routes.system_messages import router as system_messages_router
    app.include_router(system_messages_router)

    return app
