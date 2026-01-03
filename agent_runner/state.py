import os
import time
import asyncio
import httpx
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from common.circuit_breaker import CircuitBreakerRegistry

# Load env from project root
load_dotenv(Path(__file__).parent.parent / ".env")

from enum import Enum, auto
import logging

logger = logging.getLogger("agent_state")

class Tempo(Enum):
    FOCUSED = auto()    # User present (< 60s idle)
    ALERT = auto()      # User just left (< 5m idle)
    REFLECTIVE = auto() # Active Research (< 30m idle)
    DEEP = auto()       # Maintenance (> 30m idle)


from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List

@dataclass
class ClientSession:
    client_id: str
    name: str              # Friendly name (e.g. "Debug Console")
    capabilities: List[str]# ["logs", "terminal", "webview"]
    priority: int          # 0=Observer, 1=Standard, 2=Primary
    first_seen: float
    last_seen: float
    metadata: Dict[str, Any] = field(default_factory=dict)

class AgentState:
    def __init__(self):
        # Init Circuit Breakers (Safety System)
        self.mcp_circuit_breaker = CircuitBreakerRegistry()
        
        # Client Registry (Orchestration)
        self.clients: Dict[str, ClientSession] = {}
        self.active_client_id: Optional[str] = None
        
        
        # Configuration
        self.gateway_base = os.getenv("GATEWAY_BASE", "http://127.0.0.1:5455").rstrip("/")
        self.location: Dict[str, Any] = {"city": "Unknown"} # Safe default
        
        # --- 1. THE CORE ROLES ---
        # --- 1. THE CORE ROLES ---
        # Backing storage for properties
        self._agent_model = os.getenv("AGENT_MODEL", "ollama:llama3.3:70b-instruct-q8_0")
        self._router_model = os.getenv("ROUTER_MODEL", "ollama:mistral:latest")
        self._task_model = os.getenv("TASK_MODEL", self._agent_model)
        self._summarization_model = os.getenv("SUMMARIZATION_MODEL", self._agent_model)

        # --- 2. THE UNVEILED (Previously Hidden) ---
        self._vision_model = os.getenv("VISION_MODEL", "ollama:llama3.2-vision") 
        self._mcp_model = os.getenv("MCP_MODEL", self._agent_model)
        self._finalizer_model = os.getenv("FINALIZER_MODEL", self._agent_model)
        self._fallback_model = os.getenv("FALLBACK_MODEL", self._router_model)

        # --- 3. THE NEW INTELLIGENCES (Enhancements) ---
        self._intent_model = os.getenv("INTENT_MODEL", self._router_model) # Maître d'
        self._pruner_model = os.getenv("PRUNER_MODEL", self._router_model) # Context Surgeon
        self._healer_model = os.getenv("HEALER_MODEL", self._agent_model) # System Repair
        self._critic_model = os.getenv("CRITIC_MODEL", self._agent_model) # Safety Validator

        # --- 4. THE UNIFIED FOUNDATION ---
        # Single Source of Truth for Vectors. RAG/Memory servers must respect this.
        self._embedding_model = os.getenv("EMBEDDING_MODEL", "ollama:mxbai-embed-large:latest")
        
        # Flags
        self.finalizer_enabled = os.getenv("FINALIZER_ENABLED", "true").lower() == "true"
        self.router_enabled = os.getenv("ROUTER_ENABLED", "true").lower() == "true"
        self.fallback_enabled = os.getenv("FALLBACK_ENABLED", "true").lower() == "true"
        
        # Path Resolution (Canonical)
        # 1. FS_ROOT env var (highest priority)
        # 2. ~/ai/agent_fs_root (fallback)
        env_fs_root = os.getenv("FS_ROOT")
        if env_fs_root:
            self.agent_fs_root = Path(env_fs_root).resolve()
        else:
             # Fallback: relative to this file (agent_runner/state.py -> ai/agent_fs_root)
             project_root = Path(__file__).parent.parent
             self.agent_fs_root = (project_root / "agent_fs_root").resolve()
             
        # Ensure it exists
        self.agent_fs_root.mkdir(parents=True, exist_ok=True)
        
        self.max_read_bytes = int(os.getenv("AGENT_MAX_READ_BYTES", "50_000_000"))
        self.max_list_entries = int(os.getenv("AGENT_MAX_LIST_ENTRIES", "5000"))
        self.max_tool_steps = int(os.getenv("AGENT_MAX_TOOL_STEPS", "20"))
        self.http_timeout = float(os.getenv("AGENT_HTTP_TIMEOUT_S", "300.0"))
        self.router_auth_token = os.getenv("ROUTER_AUTH_TOKEN")
        
        # Performance & Readiness
        self.cloud_gpu_ready = False # Dynamic state
        
        # 1. Load Defaults (Hardcoded Baseline)
        self._load_defaults()
        
        # NOTE: We DO NOT load config.yaml here anymore. 
        # Sovereign Principle: DB is Truth. Disk is Backup.
        # We load config in initialize() (Async).
        
        # Global Registries (Formerly module-level globals)
        if not hasattr(self, 'config'):
            self.config: Dict[str, Any] = {}
        self.mcp_servers: Dict[str, Dict[str, Any]] = {}
        # Stdio Management
        self.stdio_processes: Dict[str, Any] = {}
        self.stdio_process_locks: Dict[str, asyncio.Lock] = {}
        self.stdio_process_initialized: Dict[str, bool] = {}
        self.stdio_process_health: Dict[str, float] = {}
        self.mcp_subprocess_semaphore = asyncio.Semaphore(5)
        
        # Reliability (Circuit Breakers)
        # from common.circuit_breaker import CircuitBreakerRegistry  <-- Removed to fix UnboundLocalError
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
        self.internet_policy_enabled = True # User-defined policy
        self.admin_override_active = False # Session-based override (Sudo)
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
        self.is_initialized = False
        
    async def initialize(self):
        """Entry point for shared state initialization."""
        if self.is_initialized:
            return
            
        from agent_runner.memory_server import MemoryServer
        # Initialize Memory Server Schema
        self.memory = MemoryServer(self) # Ensure instance exists
        await self.memory.initialize()
        
        self.is_initialized = True
        logger.info("AgentState initialized.")

        # [PHASE 46] Initialize Config Manager
        from agent_runner.config_manager import ConfigManager
        self.config_manager = ConfigManager(self)
        
        # Start Watchdog for Hot-Swap
        self.config_manager.start_watcher()

        # [PHASE 45] Sovereign Boot Protocol
        # 1. Attempt Load from Memory (DB)
        loaded_from_db = await self._load_runtime_config_from_db()
        
        # 2. If DB Empty (Fresh Boot), Bootstrap from Disk
        if not loaded_from_db:
             logger.info("Sovereign Memory Empty. Bootstrapping from Disk (config.yaml)...")
             await self._bootstrap_from_disk()
        else:
             logger.info("Sovereign Boot Successful. Disk config ignored (DB is Truth).")

    async def _load_runtime_config_from_db(self) -> bool:
        """
        Load configuration and secrets from Memory (SurrealDB).
        Returns True if data was found, False if empty.
        """
        try:
            # Query the config_state table
            query = "SELECT key, value FROM config_state"
            results = await self.memory._execute_query(query)
            
            if not results:
                return False

            count = 0
            for item in results:
                key = item.get("key")
                val = item.get("value")
                
                if key and val:
                    # 1. Update Environment
                    if key not in os.environ or os.environ[key] != str(val):
                        os.environ[key] = str(val)
                        
                    # 2. Update Self Attributes
                    self._update_attribute_from_config(key, val)
                    count += 1
            
            if count > 0:
                logger.info(f"Loaded {count} keys from Sovereign Memory.")
                return True
            return False
            
        except Exception as e:
            logger.warning(f"Failed to load Sovereign Config: {e}")
            return False

    async def _bootstrap_from_disk(self):
        """
        Fallback: Load config.yaml and populates DB.
        Only runs if DB is empty.
        """
        self._load_base_config() # Reads yaml to self.config and self.* attributes
        
        # Now Push to DB so next boot is Sovereign
        if self.config:
            logger.info("Bootstrapping Sovereign Memory from Disk...")
            # We iterate known keys or the whole config blob?
            # Ideally we iterate mapped keys.
            
            # Map attributes back to keys
            to_sync = {
                "AGENT_MODEL": self.agent_model,
                "ROUTER_MODEL": self.router_model,
                "TASK_MODEL": self.task_model,
                "VISION_MODEL": self.vision_model,
                "EMBEDDING_MODEL": self.embedding_model,
                # Add limits?
            }
            
            for k, v in to_sync.items():
                await self.config_manager.set_config_value(k, v)
                
    def _update_attribute_from_config(self, key: str, val: Any):
        """Helper to map Upper Keys to attributes."""
        if key == "AGENT_MODEL": self.agent_model = val
        elif key == "ROUTER_MODEL": self.router_model = val
        elif key == "TASK_MODEL": self.task_model = val
        elif key == "VISION_MODEL": self.vision_model = val
        elif key == "EMBEDDING_MODEL": self.embedding_model = val
        elif key == "MCP_MODEL": self.mcp_model = val
        elif key == "INTENT_MODEL": self.intent_model = val
        elif key == "PRUNER_MODEL": self.pruner_model = val
        elif key == "HEALER_MODEL": self.healer_model = val
        elif key == "CRITIC_MODEL": self.critic_model = val
        elif key == "FINALIZER_MODEL": self.finalizer_model = val
        elif key == "FALLBACK_MODEL": self.fallback_model = val
        elif key == "SUMMARIZATION_MODEL": self.summarization_model = val

    def _load_defaults(self):
        """Hardcoded safety defaults."""
        self.config = {}
    
    def _load_base_config(self):
        """Load limits and general config from config.yaml as the baseline."""
        import yaml
        config_path = Path(__file__).parent.parent / "config" / "config.yaml"
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    cfg_data = yaml.safe_load(f)
                    if cfg_data:
                        self.config = cfg_data
                        
                        agent_cfg = cfg_data.get("agent", cfg_data.get("agent_runner", {}))
                        
                        if agent_cfg:
                            if "limits" in agent_cfg:
                                limits = agent_cfg["limits"]
                                self.max_read_bytes = int(limits.get("max_read_bytes", self.max_read_bytes))
                                self.max_list_entries = int(limits.get("max_list_entries", self.max_list_entries))
                                self.max_tool_steps = int(limits.get("max_tool_steps", self.max_tool_steps))
                            
                            self.agent_model = agent_cfg.get("model", self.agent_model)
                            
                            if "fallback" in agent_cfg and "model" in agent_cfg["fallback"]:
                                self.fallback_model = agent_cfg["fallback"]["model"]
                                self.fallback_enabled = agent_cfg["fallback"].get("enabled", self.fallback_enabled)
                                
                            if "summarization" in agent_cfg and "model" in agent_cfg["summarization"]:
                                self.summarization_model = agent_cfg["summarization"]["model"]

                            if "tasks" in agent_cfg and "model" in agent_cfg["tasks"]:
                                self.task_model = agent_cfg["tasks"]["model"]
                                
            except Exception as e:
                print(f"Failed to load config.yaml as base: {e}")
        
    
    

        # Location Awareness
        self.location: Dict[str, Any] = {} # Populated by main.py on startup

    def is_local_model(self, model_name: str) -> bool:
        """Check if a model is hosted locally (e.g. Ollama, Test) and safe for offline use."""
        if not model_name:
            return False
        # Centralized safety check
        # We could load this from config, but these prefixes are standard for our architecture.
        return model_name.startswith(("ollama:", "local:", "test:"))

    # --- SOVEREIGN SWITCHOVER PROPERTIES ---
    # These properties intercept model access to enforce local models when offline.
    # Setters update the backing storage (user preference).
    
    def _resolve_sovereign_model(self, preferred_model: str, fallback_override: Optional[str] = None) -> str:
        """
        Return the preferred model if online or if it's already local.
        Otherwise, return a safe local fallback.
        """
        # If Online -> Preferred
        if self.internet_available:
            return preferred_model
            
        # If Offline but Preferred is Local -> Preferred
        if self.is_local_model(preferred_model):
            return preferred_model
            
        # If Offline and Preferred is Cloud -> Fallback
        # Use specific override if provided (e.g. for Vision), otherwise generic fallback
        safe_fallback = fallback_override or self.fallback_model
        
        # DOUBLE CHECK: Ensure the fallback itself is local
        if not self.is_local_model(safe_fallback):
             # Deep Fallback: Hardcoded safe model
             if "vision" in preferred_model.lower():
                 return "ollama:llama3.2-vision"
             return "ollama:mistral:latest"
             
        return safe_fallback

    @property
    def agent_model(self): return self._resolve_sovereign_model(self._agent_model)
    @agent_model.setter
    def agent_model(self, value): self._agent_model = value

    @property
    def router_model(self): return self._resolve_sovereign_model(self._router_model)
    @router_model.setter
    def router_model(self, value): self._router_model = value

    @property
    def task_model(self): return self._resolve_sovereign_model(self._task_model)
    @task_model.setter
    def task_model(self, value): self._task_model = value

    @property
    def summarization_model(self): return self._resolve_sovereign_model(self._summarization_model)
    @summarization_model.setter
    def summarization_model(self, value): self._summarization_model = value

    @property
    def vision_model(self): 
        # Specific fallback for vision
        return self._resolve_sovereign_model(self._vision_model, fallback_override="ollama:llama3.2-vision")
    @vision_model.setter
    def vision_model(self, value): self._vision_model = value

    @property
    def mcp_model(self): return self._resolve_sovereign_model(self._mcp_model)
    @mcp_model.setter
    def mcp_model(self, value): self._mcp_model = value

    @property
    def finalizer_model(self): return self._resolve_sovereign_model(self._finalizer_model)
    @finalizer_model.setter
    def finalizer_model(self, value): self._finalizer_model = value
    
    @property
    def fallback_model(self): 
        # Fallback model MUST be local. If configured as cloud, we override even the fallback.
        if self.internet_available:
             return self._fallback_model
        if self.is_local_model(self._fallback_model):
             return self._fallback_model
        return "ollama:mistral:latest"
    @fallback_model.setter
    def fallback_model(self, value): self._fallback_model = value

    @property
    def intent_model(self): return self._resolve_sovereign_model(self._intent_model)
    @intent_model.setter
    def intent_model(self, value): self._intent_model = value

    @property
    def pruner_model(self): return self._resolve_sovereign_model(self._pruner_model)
    @pruner_model.setter
    def pruner_model(self, value): self._pruner_model = value

    @property
    def healer_model(self): return self._resolve_sovereign_model(self._healer_model)
    @healer_model.setter
    def healer_model(self, value): self._healer_model = value

    @property
    def critic_model(self): return self._resolve_sovereign_model(self._critic_model)
    @critic_model.setter
    def critic_model(self, value): self._critic_model = value

    @property
    def embedding_model(self): return self._resolve_sovereign_model(self._embedding_model, fallback_override="ollama:mxbai-embed-large:latest")
    @embedding_model.setter
    def embedding_model(self, value): self._embedding_model = value


    def get_current_tempo(self) -> "Tempo":
        """
        Determine the system's operational tempo based on macOS system idle time.
        Returns a Tempo enum (FOCUSED, ALERT, REFLECTIVE, DEEP).
        """
        if self.active_requests > 0:
            return Tempo.FOCUSED
        
        # Get System Idle Time via ioreg (nanoseconds -> seconds)
        idle_seconds = 0.0
        try:
            import subprocess
            # ioreg -c IOHIDSystem | awk '/HIDIdleTime/ {print $NF/1000000000; exit}'
            cmd = ["ioreg", "-c", "IOHIDSystem"]
            # We run this synchronously because it's fast (<20ms) and critical for decision making
            # but ideally should be cached or async. For now, subprocess.run is safe enough for a property-like check.
            result = subprocess.run(cmd, capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if "HIDIdleTime" in line:
                    # Line format: "HIDIdleTime" = 123456789
                    parts = line.split("=")
                    if len(parts) > 1:
                        nanos = int(parts[1].strip())
                        idle_seconds = nanos / 1_000_000_000.0
                        break
        except Exception:
            # Fallback to internal interaction time if OS check fails
            idle_seconds = time.time() - (self.last_interaction_time or time.time())

        # Logic
        if idle_seconds < 60:
            return Tempo.FOCUSED # User is actively typing/mousing
        elif idle_seconds < 300: # < 5 mins
            return Tempo.ALERT
        elif idle_seconds < 1800: # < 30 mins
            return Tempo.REFLECTIVE
        else:
            return Tempo.DEEP


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
        
        # 0. Normalization (Consistent with load_mcp_servers)
        if "command" in config:
            cmd = [config["command"]]
            if "args" in config:
                cmd.extend(config["args"])
            config["cmd"] = cmd

        # 1. Update In-Memory State
        self.mcp_servers[name] = config
        
        # 2. Persist to Sovereign Memory + Disk (via ConfigManager)
        if hasattr(self, "config_manager"):
            await self.config_manager.save_mcp_config(self.mcp_servers)
            # Also update DB row specifically
            await self.config_manager.update_mcp_server(name, config)
        else:
            logger.warning("ConfigManager not ready, changes transient.")

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
        
        # 3. Persist to Sovereign Memory + Disk
        if hasattr(self, "config_manager"):
            await self.config_manager.save_mcp_config(self.mcp_servers)
            # Delete from DB
            await self.config_manager.memory._execute_query(f"DELETE FROM mcp_server WHERE name = '{name}'")
        else:
             logger.error("ConfigManager not ready for MCP removal.")
            
        return True

    async def toggle_mcp_server(self, name: str, enabled: bool) -> bool:
        """Dynamically enable or disable an MCP server."""
        if name not in self.mcp_servers:
            return False
            
        # 1. Update In-Memory State
        self.mcp_servers[name]["enabled"] = enabled
        
        # 2. If Disabling, Terminate Process
        if not enabled:
            if name in self.stdio_processes:
                try:
                    process = self.stdio_processes[name]
                    process.terminate()
                    try:
                        await asyncio.wait_for(process.wait(), timeout=2.0)
                    except asyncio.TimeoutError:
                        process.kill()
                    
                    del self.stdio_processes[name]
                    print(f"Terminated process for disabled MCP server '{name}'")
                except Exception as e:
                    print(f"Error terminating MCP server '{name}': {e}")
            
            # Also clear from tool cache via Engine (but State doesn't have engine ref directly easily)
            # We will handle cache clearing in the Route handler.

        # 3. Persist to Sovereign Memory + Disk
        if hasattr(self, "config_manager"):
            await self.config_manager.save_mcp_config(self.mcp_servers)
            
            # DB Update: Retrieve current config + update
            # Doing full upsert is safest
            cfg = self.mcp_servers[name]
            await self.config_manager.update_mcp_server(name, cfg)
        else:
             print(f"ConfigManager not ready for MCP toggle '{name}'")
            
        return True

    async def cleanup_all_stdio_processes(self) -> None:
        """Terminate all active stdio processes to allow for a clean reload."""
        # Create a list of keys to avoid modification during iteration
        for name in list(self.stdio_processes.keys()):
            try:
                # Reuse logic from remove_mcp_server or generic cleanup
                # Check for locks first?
                from agent_runner.transports.stdio import cleanup_stdio_process
                await cleanup_stdio_process(self, name)
            except Exception as e:
                print(f"Error cleaning up STDIO process '{name}': {e}")
                # Fallback manual kill
                if name in self.stdio_processes:
                    del self.stdio_processes[name]
