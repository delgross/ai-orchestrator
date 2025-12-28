from __future__ import annotations
import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union
import httpx
import yaml
from dotenv import load_dotenv

load_dotenv()

from common.constants import (
    PROVIDER_OPENAI_COMPAT, PROVIDER_OLLAMA, PREFIX_AGENT, PREFIX_OLLAMA, PREFIX_RAG,
    OBJ_CHAT_COMPLETION, OBJ_CHAT_COMPLETION_CHUNK, OBJ_MODEL, OBJ_LIST,
    MODEL_AGENT_MCP, MODEL_ROUTER, ROLE_ASSISTANT
)

VERSION = f"0.8.0-sentinel"

# Paths
PROVIDERS_YAML = os.getenv("PROVIDERS_YAML", os.path.expanduser("~/ai/providers.yaml"))

# Service URLs
OLLAMA_BASE = os.getenv("OLLAMA_BASE", "http://127.0.0.1:11434").rstrip("/")
RAG_BASE = os.getenv("RAG_BASE", "http://127.0.0.1:5555").rstrip("/")
RAG_QUERY_PATH = os.getenv("RAG_QUERY_PATH", "/query")

AGENT_RUNNER_URL = os.getenv("AGENT_RUNNER_URL", "http://127.0.0.1:5460").rstrip("/")
if AGENT_RUNNER_URL.endswith("/v1/chat/completions"):
    AGENT_RUNNER_URL = AGENT_RUNNER_URL[: -len("/v1/chat/completions")].rstrip("/")
elif AGENT_RUNNER_URL.endswith("/v1"):
    AGENT_RUNNER_URL = AGENT_RUNNER_URL[: -len("/v1")].rstrip("/")
AGENT_RUNNER_CHAT_PATH = os.getenv("AGENT_RUNNER_CHAT_PATH", "/v1/chat/completions")

# Settings
MODELS_CACHE_TTL_S = float(os.getenv("MODELS_CACHE_TTL_S", "600"))
HTTP_TIMEOUT_S = float(os.getenv("HTTP_TIMEOUT_S", "120"))
MAX_REQUEST_BODY_BYTES = int(os.getenv("MAX_REQUEST_BODY_BYTES", "5_000_000"))
DEFAULT_UPSTREAM_HEADERS = os.getenv("DEFAULT_UPSTREAM_HEADERS", "")
ROUTER_AUTH_TOKEN = os.getenv("ROUTER_AUTH_TOKEN") or ""; print(f"DEBUG: Router Token Loaded: {ROUTER_AUTH_TOKEN}")
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
    embeddings_path: str = "/embeddings"

    def api_key(self) -> Optional[str]:
        if not self.api_key_env:
            return None
        return os.getenv(self.api_key_env)

class State:
    def __init__(self) -> None:
        self.started_at = time.time()
        self.client = httpx.AsyncClient(
            timeout=HTTP_TIMEOUT_S,
            trust_env=False,
            limits=httpx.Limits(
                max_keepalive_connections=20,
                max_connections=100,
                keepalive_expiry=30.0
            )
        )
        self.providers: Dict[str, Provider] = {}
        self.models_cache: Tuple[float, Dict[str, Any]] = (0.0, {})
        self.max_concurrency = ROUTER_MAX_CONCURRENCY
        
        # MCP & Agent Health
        cb_threshold = int(os.getenv("CIRCUIT_BREAKER_THRESHOLD", "5"))
        cb_timeout = float(os.getenv("CIRCUIT_BREAKER_TIMEOUT_S", "60.0"))
        from common.circuit_breaker import CircuitBreakerRegistry
        self.circuit_breakers = CircuitBreakerRegistry(default_threshold=cb_threshold, default_timeout=cb_timeout)
        
        self.mcp_tool_access_enabled = True
        self.mcp_auto_toggle_enabled = False
        self.agent_runner_health_check_interval = 10.0
        self.agent_runner_last_health_check = 0.0
        self.agent_runner_last_healthy = True
        self.agent_runner_consecutive_failures = 0
        self.agent_runner_health_check_failures_threshold = 3
        
        # Ollama config
        self.ollama_num_ctx = 32768
        self.ollama_auto_adjust_context = False
        self.ollama_model_options = {}
        
        # Stats
        self.request_count = 0
        self.error_count = 0
        self.total_response_time_ms = 0.0
        self.request_by_method: Dict[str, int] = {}
        self.request_by_path: Dict[str, int] = {}
        self.request_by_status: Dict[int, int] = {}
        self.provider_requests: Dict[str, int] = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Alias resolution
        env_router = os.getenv("ROUTER_MODEL", "ollama:mistral:latest")
        if env_router.strip().lower() == "router":
            env_router = "ollama:mistral:latest"
        self.system_router_model = env_router

        # Default Embedding Model
        self.default_embedding_model = os.getenv("DEFAULT_EMBEDDING_MODEL", "ollama:mxbai-embed-large:latest")

state = State()
