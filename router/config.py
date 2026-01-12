import asyncio
import os
import sys
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple
import httpx
import yaml
from dotenv import load_dotenv

from common.constants import (
    PREFIX_AGENT,
    PREFIX_OLLAMA,
    PREFIX_RAG,
    OBJ_MODEL,
    OBJ_CHAT_COMPLETION,
    OBJ_LIST,
    ROLE_SYSTEM,
    ROLE_USER,
    ROLE_ASSISTANT,
    OBJ_CHAT_COMPLETION_CHUNK,
)  # noqa: F401


# Load environment variables from multiple files
# Load providers.env first for API keys, then main .env, then router.env
load_dotenv("providers.env")  # Load provider API keys first
load_dotenv()  # Load main .env file (may override)
load_dotenv("router.env")  # Load router-specific settings last


VERSION = "0.8.0-sentinel"

# Helper to load Sovereign Registry
def load_sovereign_config() -> Dict[str, Any]:
    try:
        # ai/router/config.py -> ai/
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base_dir, "config", "sovereign.yaml")
        if os.path.exists(path):
             with open(path, "r") as f:
                 return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"WARN: Failed to load sovereign.yaml: {e}")
    return {}

SOV_CONFIG = load_sovereign_config()
SOV_NET = SOV_CONFIG.get("network", {})
SOV_MODELS = SOV_CONFIG.get("models", {})

# Service URLs
# Precedence: Env Var > Sovereign YAML > Hardcoded Default
OLLAMA_PORT = SOV_NET.get("ollama_port", 11434)
OLLAMA_BASE = os.getenv("OLLAMA_BASE", f"http://127.0.0.1:{OLLAMA_PORT}").rstrip("/")

RAG_PORT = SOV_NET.get("rag_port", 5555)
RAG_BASE = os.getenv("RAG_BASE", f"http://127.0.0.1:{RAG_PORT}").rstrip("/")
RAG_QUERY_PATH = os.getenv("RAG_QUERY_PATH", "/query")

AGENT_PORT = SOV_NET.get("agent_port", 5460)
AGENT_RUNNER_URL = os.getenv("AGENT_RUNNER_URL", f"http://127.0.0.1:{AGENT_PORT}").rstrip("/")

if AGENT_RUNNER_URL.endswith("/v1/chat/completions"):
    AGENT_RUNNER_URL = AGENT_RUNNER_URL[: -len("/v1/chat/completions")].rstrip("/")
elif AGENT_RUNNER_URL.endswith("/v1"):
    AGENT_RUNNER_URL = AGENT_RUNNER_URL[: -len("/v1")].rstrip("/")
AGENT_RUNNER_CHAT_PATH = os.getenv("AGENT_RUNNER_CHAT_PATH", "/v1/chat/completions")

# SurrealDB Config (for Router Config Persistence)
SURREAL_PORT = SOV_NET.get("surreal_port", 8000)
SURREAL_URL = os.getenv("SURREAL_URL", f"http://localhost:{SURREAL_PORT}")
SURREAL_USER = os.getenv("SURREAL_USER", "root")
SURREAL_PASS = os.getenv("SURREAL_PASS", "root")
SURREAL_NS = os.getenv("SURREAL_NS", "orchestrator")
SURREAL_DB = os.getenv("SURREAL_DB", "memory")

# Settings
MODELS_CACHE_TTL_S = float(os.getenv("MODELS_CACHE_TTL_S", "600"))
HTTP_TIMEOUT_S = float(os.getenv("HTTP_TIMEOUT_S", "120"))
MAX_REQUEST_BODY_BYTES = int(os.getenv("MAX_REQUEST_BODY_BYTES", "5_000_000"))
DEFAULT_UPSTREAM_HEADERS = os.getenv("DEFAULT_UPSTREAM_HEADERS", "")
ROUTER_AUTH_TOKEN = os.getenv("ROUTER_AUTH_TOKEN") or ""
# During tests, disable auth token by default
# Default Providers Config
PROVIDERS_YAML = os.path.join(os.path.dirname(__file__), "providers.yaml")

if "pytest" in sys.modules or os.getenv("PYTEST_CURRENT_TEST"):
    ROUTER_AUTH_TOKEN = ""
ROUTER_MAX_CONCURRENCY = int(os.getenv("ROUTER_MAX_CONCURRENCY", "0"))
FS_ROOT = os.getenv("FS_ROOT", os.path.expanduser("~/ai/agent_fs_root"))

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
    _api_key_cache: Optional[str] = None

    async def load_api_key(self, client: Optional[httpx.AsyncClient] = None) -> None:
        """Async refresh of API key from Database."""
        if not self.api_key_env:
            return

        # 1. Environment Variable (Highest Priority for speed/override)
        env_key = os.getenv(self.api_key_env)
        if env_key:
            self._api_key_cache = env_key
            return

        # 2. Database (Source of Truth)
        try:
            from router.routes.config import get_surreal_url, SURREAL_NS, SURREAL_DB, SURREAL_USER, SURREAL_PASS
            
            url = f"{get_surreal_url()}/sql"
            q = f"USE NS {SURREAL_NS} DB {SURREAL_DB}; SELECT value FROM config_state WHERE key = '{self.api_key_env}'"
            
            headers = {"Accept": "application/json", "NS": SURREAL_NS, "DB": SURREAL_DB}
            auth = (SURREAL_USER, SURREAL_PASS) if SURREAL_USER else None
            
            # Use provided client or create one-off
            if client:
                resp = await client.post(url, data=q, auth=auth, headers=headers, timeout=5.0)
            else:
                async with httpx.AsyncClient() as c:
                    resp = await c.post(url, data=q, auth=auth, headers=headers, timeout=5.0)
            
            if resp.status_code == 200:
                data = resp.json() 
                # SurrealDB returns list of implementation results
                # [ { "result": [ { "value": "..." } ], "status": "OK" } ]
                if isinstance(data, list) and len(data) > 0:
                     res = data[0].get("result")
                     if res and isinstance(res, list) and len(res) > 0:
                         self._api_key_cache = res[0].get("value")
        except Exception as e:
            # Don't log spam on connection errors, just keep old cache if any
            pass

    def api_key(self) -> Optional[str]:
        # Fast non-blocking access
        if self._api_key_cache:
            return self._api_key_cache
            
        if not self.api_key_env:
            return None

        # Fallback to env if not cached yet
        return os.getenv(self.api_key_env)

class State:
    def __init__(self) -> None:
        self.started_at = time.time()
        
        # Load overrides from config.yaml
        config_timeout = HTTP_TIMEOUT_S
        config_concurrency = ROUTER_MAX_CONCURRENCY
        
        try:
            # Assuming cwd is ai/ or file is at ai/router/config.py
            # FS_ROOT is usually ~/ai/agent_fs_root
            # We want ~/ai/config/config.yaml or <repo>/config/config.yaml
            # Let's try relative path from this file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            conf_path = os.path.join(base_dir, "config", "config.yaml")
            if os.path.exists(conf_path):
                with open(conf_path, "r") as f:
                    c = yaml.safe_load(f)
                    if c and "router" in c:
                        rc = c["router"]
                        if "http_timeout" in rc:
                            config_timeout = float(rc["http_timeout"])
                            # Debug logging removed - logger not available at module level
                        if "max_concurrency" in rc:
                            config_concurrency = int(rc["max_concurrency"])
        except Exception as e:
            import logging
            logging.warning(f"Failed to load config.yaml in router: {e}")

        self.client = httpx.AsyncClient(
            timeout=config_timeout,
            trust_env=False,
            limits=httpx.Limits(
                max_keepalive_connections=20,
                max_connections=100,
                keepalive_expiry=30.0
            )
        )
        self.providers: Dict[str, Provider] = {}
        self.models_cache: Tuple[float, Dict[str, Any]] = (0.0, {})
        self.max_concurrency = config_concurrency
        self._semaphore: Optional[asyncio.Semaphore] = None

        # Agent Runner Configuration
        self.agent_runner_url = AGENT_RUNNER_URL
        self.router_auth_token = os.getenv("ROUTER_AUTH_TOKEN", "antigravity_router_token_2025")
        
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
        self.ollama_model_options: Dict[str, Any] = {}
        
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
        # Use Sovereign Model or Env Var or Hardcoded Fallback
        sov_router_model = SOV_MODELS.get("router", "ollama:mistral:latest")
        env_router = os.getenv("ROUTER_MODEL", sov_router_model)
        
        if env_router.strip().lower() == "router":
            env_router = sov_router_model # Resolve 'router' string to actual model
            
        self.system_router_model = env_router
        
        # System Toggles
        self.router_mode = "sync" # 'sync' or 'async'

        # Default Embedding Model
        self.default_embedding_model = os.getenv("DEFAULT_EMBEDDING_MODEL", "ollama:mxbai-embed-large:latest")

    @property
    def semaphore(self) -> Optional[asyncio.Semaphore]:
        if self.max_concurrency <= 0:
            return None
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self.max_concurrency)
        return self._semaphore

state = State()
