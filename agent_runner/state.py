import os
import time
import asyncio
import httpx
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load env from project root
load_dotenv(Path(__file__).parent.parent / ".env")


class AgentState:
    def __init__(self):
        # Configuration
        # Configuration
        # Configuration
        self.gateway_base = os.getenv("GATEWAY_BASE", "http://127.0.0.1:5455").rstrip("/")
        self.agent_model = os.getenv("AGENT_MODEL", "openai:gpt-4o-mini")
        self.task_model = os.getenv("TASK_MODEL", "ollama:mistral:latest")
        self.vision_model = os.getenv("VISION_MODEL", "openai:gpt-4o") # Default to high-quality vision, can be overridden
        self.mcp_model = os.getenv("MCP_MODEL", "openai:gpt-4o-mini") # Missing generic tool model
        self.router_model = os.getenv("ROUTER_MODEL", "ollama:mistral:latest")
        self.finalizer_model = os.getenv("FINALIZER_MODEL", "openai:gpt-5.2") # User requested High-End model
        self.finalizer_enabled = os.getenv("FINALIZER_ENABLED", "true").lower() == "true"
        self.router_enabled = os.getenv("ROUTER_ENABLED", "true").lower() == "true"
        self.summarization_model = os.getenv("SUMMARIZATION_MODEL", "openai:gpt-4o")
        self.fallback_model = os.getenv("FALLBACK_MODEL", "ollama:mistral:latest")
        self.fallback_enabled = os.getenv("FALLBACK_ENABLED", "true").lower() == "true"
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "ollama:mxbai-embed-large:latest")
        
        self.agent_fs_root = os.getenv("FS_ROOT", os.path.expanduser("~/ai/agent_fs_root"))
        self.max_read_bytes = int(os.getenv("AGENT_MAX_READ_BYTES", "50_000_000"))
        self.max_list_entries = int(os.getenv("AGENT_MAX_LIST_ENTRIES", "5000"))
        self.max_tool_steps = int(os.getenv("AGENT_MAX_TOOL_STEPS", "20"))
        self.http_timeout = float(os.getenv("AGENT_HTTP_TIMEOUT_S", "120.0"))
        self.router_auth_token = os.getenv("ROUTER_AUTH_TOKEN")
        
        # Performance & Readiness
        self.cloud_gpu_ready = False # Dynamic state
        
        # Load Overrides from Disk
        self._load_config_file()

    def _load_config_file(self):
        config_path = Path(__file__).parent.parent / "system_config.json"
        
        if config_path.exists():
            try:
                import json
                with open(config_path, "r") as f:
                    cfg = json.load(f)
                    self.agent_model = cfg.get("agent_model", self.agent_model)
                    self.summarization_model = cfg.get("summarization_model", self.summarization_model)
                    self.task_model = cfg.get("task_model", self.task_model)
                    self.vision_model = cfg.get("vision_model", self.vision_model)
                    self.router_model = cfg.get("router_model", self.router_model)
            except Exception as e:
                print(f"Failed to load system_config.json: {e}")

        # Global Registries (Formerly module-level globals)
        self.config: Dict[str, Any] = {}
        self.mcp_servers: Dict[str, Dict[str, Any]] = {}
        # Stdio Management
        self.stdio_processes: Dict[str, Any] = {}
        self.stdio_process_locks: Dict[str, asyncio.Lock] = {}
        self.stdio_process_initialized: Dict[str, bool] = {}
        self.stdio_process_health: Dict[str, float] = {}
        self.mcp_subprocess_semaphore = asyncio.Semaphore(5)
        
        # Reliability (Circuit Breakers)
        from common.circuit_breaker import CircuitBreakerRegistry
        cb_threshold = int(os.getenv("CIRCUIT_BREAKER_THRESHOLD") or os.getenv("MCP_CB_THRESHOLD") or "5")
        cb_timeout = float(os.getenv("CIRCUIT_BREAKER_TIMEOUT_S") or os.getenv("MCP_CB_TIMEOUT") or "60.0")
        self.mcp_circuit_breaker = CircuitBreakerRegistry(
            default_threshold=cb_threshold,
            default_timeout=cb_timeout
        )
        
        # Clients & Lifecycle
        self.http_client: Optional[httpx.AsyncClient] = None
        self.task_manager = None # Will be initialized in main
        self.started_at = time.time()

        # Dashboard & Metrics
        self.internet_available = True
        self.last_internet_check = 0.0
        self.request_count = 0
        self.error_count = 0
        self.total_response_time_ms = 0.0
        self.last_error: Optional[str] = None
        self.system_mode = "Production"
        self.hardware_verified = True
        
        # Idle State Tracking
        self.active_requests = 0
        self.last_interaction_time = 0.0

    async def get_http_client(self) -> httpx.AsyncClient:
        if self.http_client is None:
            headers = {}
            if self.router_auth_token:
                headers["Authorization"] = f"Bearer {self.router_auth_token}"
            self.http_client = httpx.AsyncClient(timeout=self.http_timeout, headers=headers)
        return self.http_client

    async def close_http_client(self):
        if self.http_client:
            await self.http_client.aclose()
            self.http_client = None

    async def add_mcp_server(self, name: str, config: Dict[str, Any]) -> None:
        """Dynamically add or update an MCP server at runtime."""
        from agent_runner.transports.stdio import get_or_create_stdio_process, initialize_stdio_process
        
        # 1. Update In-Memory State
        self.mcp_servers[name] = config
        
        # 2. Persist to config.yaml (so it survives restart)
        try:
            import yaml
            config_path = Path(__file__).parent.parent / "config" / "config.yaml"
            if config_path.exists():
                with open(config_path, "r") as f:
                    data = yaml.safe_load(f) or {}
                
                if "mcp_servers" not in data:
                    data["mcp_servers"] = {}
                
                # Normalize command/args for storage if needed, but usually we store as is
                data["mcp_servers"][name] = config
                
                with open(config_path, "w") as f:
                    yaml.dump(data, f, default_flow_style=False)
        except Exception as e:
            print(f"Failed to persist MCP server '{name}': {e}")

        # 3. If it's a STDIO server, try to warm it up immediately (Optional but good for feedback)
        if config.get("type") == "stdio":
            # Just try to get process, it will auto-start
            try:
                proc = await get_or_create_stdio_process(self, name, config["cmd"], config.get("env", {}))
                if proc:
                    await initialize_stdio_process(self, name, proc)
            except Exception as e:
                print(f"Failed to warm/init new MCP server '{name}': {e}")
    
    async def remove_mcp_server(self, name: str) -> bool:
        """Dynamically remove an MCP server at runtime."""
        if name not in self.mcp_servers:
            return False
            
        # 1. Terminate Process if STDIO
        if name in self.stdio_processes:
            try:
                process = self.stdio_processes[name]
                process.terminate()
                try:
                    await asyncio.wait_for(process.wait(), timeout=2.0)
                except asyncio.TimeoutError:
                    process.kill()
                
                del self.stdio_processes[name]
            except Exception as e:
                print(f"Error terminating MCP server '{name}': {e}")
                
        # 2. Update In-Memory State
        del self.mcp_servers[name]
        
        # 3. Persist to config.yaml
        try:
            import yaml
            config_path = Path(__file__).parent.parent / "config" / "config.yaml"
            if config_path.exists():
                with open(config_path, "r") as f:
                    data = yaml.safe_load(f) or {}
                
                if "mcp_servers" in data and name in data["mcp_servers"]:
                    del data["mcp_servers"][name]
                    
                    with open(config_path, "w") as f:
                        yaml.dump(data, f, default_flow_style=False)
        except Exception as e:
            print(f"Failed to persist MCP removal '{name}': {e}")
            
        return True
