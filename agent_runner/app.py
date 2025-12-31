import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from common.observability import ComponentType
from common.observability_middleware import ObservabilityMiddleware
from agent_runner.routes import chat, mcp, admin, files, notifications

def create_app() -> FastAPI:
    app = FastAPI(title="Agent Runner (Modularized)")

    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    # Observability Middlewae
    app.add_middleware(
        ObservabilityMiddleware,
        component_type=ComponentType.AGENT_RUNNER,
        component_id="agent-runner"
    )

    # Include Routers
    app.include_router(chat.router)
    app.include_router(mcp.router)
    app.include_router(admin.router)
    app.include_router(files.router)
    app.include_router(notifications.router)

    return app
