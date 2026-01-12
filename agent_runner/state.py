import os
import time
import asyncio
import httpx
from typing import Dict, Any, Optional
from pathlib import Path
from common.circuit_breaker import CircuitBreakerRegistry
from agent_runner.db_utils import run_query

# NOTE: .env file is NOT loaded here. Database is the source of truth.
# .env values are ingested into database via SystemIngestor, then loaded via _load_runtime_config_from_db()
# If .env file changes, ConfigManager.sync_env_from_disk() syncs disk → DB

from enum import Enum, auto
import logging

logger = logging.getLogger("agent_runner")

class Tempo(Enum):
    FOCUSED = auto()    # User present (< 60s idle)
    ALERT = auto()      # User just left (< 5m idle)
    REFLECTIVE = auto() # Active Research (< 30m idle)
    DEEP = auto()       # Maintenance (> 30m idle)


from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
import contextvars

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
        
        
        # System Event Queue for Nexus Multiplexing
        self.system_event_queue: asyncio.Queue = asyncio.Queue()
        
        # Configuration
        self.gateway_base = os.getenv("GATEWAY_BASE", "http://127.0.0.1:5455").rstrip("/")
        self.location: Dict[str, Any] = {"city": "Unknown"} # Safe default
        
        # --- 1. THE CORE ROLES ---
        # Backing storage for properties
        #Backing storage for properties
        self._agent_model = os.getenv("AGENT_MODEL", "ollama:llama3.3:70b")
        self._router_model = os.getenv("ROUTER_MODEL", "ollama:llama3.3:70b") # Consolidated
        self._task_model = os.getenv("TASK_MODEL", self._agent_model)
        self._summarization_model = os.getenv("SUMMARIZATION_MODEL", "ollama:llama3.3:70b") # Consolidated

        # --- 2. THE UNVEILED (Previously Hidden) ---
        self._vision_model = os.getenv("VISION_MODEL", "ollama:llama3.2-vision:latest") 
        self._mcp_model = os.getenv("MCP_MODEL", self._agent_model)
        self._finalizer_model = os.getenv("FINALIZER_MODEL", self._agent_model)
        self._fallback_model = os.getenv("FALLBACK_MODEL", "ollama:llama3.3:70b") # Consolidated

        # --- 3. THE NEW INTELLIGENCES (Enhancements) ---
        self._intent_model = os.getenv("INTENT_MODEL", "ollama:llama3.3:70b") # Consolidated
        self._pruner_model = os.getenv("PRUNER_MODEL", "ollama:llama3.3:70b") # Consolidated
        self._healer_model = os.getenv("HEALER_MODEL", "ollama:qwq:latest") # Specialized
        self._critic_model = os.getenv("CRITIC_MODEL", "ollama:llama3.3:70b") # Specialized
        self._query_refinement_model = os.getenv("QUERY_REFINEMENT_MODEL", "ollama:llama3.3:70b") # Consolidated

        # --- 4. THE UNIFIED FOUNDATION ---
        # Single Source of Truth for Vectors. RAG/Memory servers must respect this.
        self._embedding_model = os.getenv("EMBEDDING_MODEL", "ollama:mxbai-embed-large:latest")
        
        # Flags
        self.finalizer_enabled = os.getenv("FINALIZER_ENABLED", "true").lower() == "true"
        self.router_enabled = os.getenv("ROUTER_ENABLED", "true").lower() == "true"
        self.fallback_enabled = os.getenv("FALLBACK_ENABLED", "true").lower() == "true"
        
        # Degraded Mode Tracking
        self.degraded_mode = False
        self.degraded_reasons: List[str] = []
        self.degraded_features: List[str] = []
        
        # Ingestion Status Tracking
        self.ingestion_status: Dict[str, Any] = {"status": "pending", "error": None, "completed": False}
        
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
        self.max_tool_count = int(os.getenv("AGENT_MAX_TOOLS", "120"))
        self.http_timeout = float(os.getenv("AGENT_HTTP_TIMEOUT_S", "300.0"))
        self.router_auth_token = os.getenv("ROUTER_AUTH_TOKEN") or "antigravity_router_token_2025"
        
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
        self.last_user_query: str = "" # Store last user query for analytics
        
        # Reliability (Circuit Breakers)
        # from common.circuit_breaker import CircuitBreakerRegistry  <-- Removed to fix UnboundLocalError
        cb_threshold = int(os.getenv("CIRCUIT_BREAKER_THRESHOLD") or os.getenv("MCP_CB_THRESHOLD") or "5")
        cb_timeout = float(os.getenv("CIRCUIT_BREAKER_TIMEOUT_S") or os.getenv("MCP_CB_TIMEOUT") or "60.0")
        from agent_runner.constants import CORE_MCP_SERVERS
        self.mcp_circuit_breaker = CircuitBreakerRegistry(
            default_threshold=cb_threshold,
            default_timeout=cb_timeout,
            core_services=CORE_MCP_SERVERS
        )
        
        # Clients & Lifecycle
        self.http_client: Optional[httpx.AsyncClient] = None
        self.task_manager = None # Will be initialized in main
        self.started_at = time.time()
        self.system_start_time = time.time()  # Track system start time for staggered health checks
        
        # MCP Server Health Status
        self.mcp_server_health: Dict[str, Dict[str, Any]] = {}
        # Format: {
        #   "server-name": {
        #       "healthy": bool,
        #       "last_check": float,
        #       "last_success": float | None,
        #       "last_failure": float | None,
        #       "consecutive_failures": int,
        #       "error": str | None
        #   }
        # }

        # Dashboard & Metrics
        self.internet_available = True
        self.internet_policy_enabled = True # User-defined policy
        self.admin_override_active = False # Session-based override (Sudo)
        self.sudo_granted_at: Optional[float] = None  # When sudo was granted (for sticky sudo)
        self.sudo_revert_tempo = "REFLECTIVE"  # Default: revert when REFLECTIVE or deeper
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
        self.active_requests = 0
        self.last_interaction_time = 0.0
        self.is_initialized = False
        
        # --- STATEFUL MODE SYSTEM ---
        # Tracks current interaction mode (e.g. 'chat', 'coding', 'writer')
        # Tracks current interaction mode (e.g. 'chat', 'coding', 'writer')
        self._active_mode: str = "chat"
        self.modes: Dict[str, Any] = {} # Populated from Sovereign Config
        
        # --- QUALITY/SPEED CONTROL SYSTEM ---
        from agent_runner.quality_tiers import QualityTier, get_tier_config
        self.quality_tier: QualityTier = QualityTier.BALANCED  # Default - optimized for remote models
        self.quality_tier_config: Dict[str, Any] = get_tier_config(self.quality_tier)
        # Use ContextVar for request-specific state to prevent race conditions
        self._request_quality_tier_var: contextvars.ContextVar = contextvars.ContextVar("request_quality_tier", default=None)
        
        # [ESCALATION PROTOCOL] Track consecutive failures within a request context
        self._tool_consecutive_failures_var: contextvars.ContextVar = contextvars.ContextVar("tool_consecutive_failures", default=0)

        # Remote-first system optimization
        self.remote_first: bool = True  # System predominantly uses remote models
        
        # Layer control settings
        self.skip_refinement_default: bool = False  # Default: refinement enabled
        self.memory_retrieval_limit: int = 10  # Default memory facts
        self.architecture_context_limit: int = 50  # Default architecture facts
        self.context_prune_limit: Optional[int] = 20  # Default: 20 messages
        self.tool_category_filter: Optional[List[str]] = None  # None = no filtering

    @property
    def tool_consecutive_failures(self) -> int:
        return self._tool_consecutive_failures_var.get()

    @tool_consecutive_failures.setter
    def tool_consecutive_failures(self, value: int):
        self._tool_consecutive_failures_var.set(value)
    
    def set_quality_tier(self, tier: 'QualityTier'):
        """Set the default quality tier."""
        try:
            from agent_runner.quality_tiers import get_tier_config, QualityTier
            
            if tier is None:
                logger.warning("set_quality_tier: tier is None, using BALANCED default")
                tier = QualityTier.BALANCED
            
            self.quality_tier = tier
            self.quality_tier_config = get_tier_config(tier)
            
            # Apply tier configuration to layer settings
            config = self.quality_tier_config
            self.skip_refinement_default = config.get("skip_refinement", False)
            memory_config = config.get("memory_retrieval", {})
            arch_config = config.get("architecture_context", {})
            prune_config = config.get("context_pruning", {})
            
            if memory_config.get("enabled", True):
                self.memory_retrieval_limit = memory_config.get("limit", 10)
            else:
                self.memory_retrieval_limit = 0
            
            if arch_config.get("enabled", True):
                self.architecture_context_limit = arch_config.get("limit", 50)
            else:
                self.architecture_context_limit = 0
            
            if prune_config.get("enabled", True):
                self.context_prune_limit = prune_config.get("limit", 20)
            else:
                self.context_prune_limit = None
                
            logger.debug(f"Quality tier set to {tier.value}")
        except ImportError as e:
            logger.error(f"set_quality_tier: failed to import quality_tiers: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"set_quality_tier: unexpected error: {e}", exc_info=True)
            raise
    
    @property
    def _request_quality_tier(self) -> Optional['QualityTier']:
        """Thread-safe access to request-specific quality tier."""
        return self._request_quality_tier_var.get()

    @_request_quality_tier.setter
    def _request_quality_tier(self, value: Optional['QualityTier']):
        self._request_quality_tier_var.set(value)

    def get_quality_tier_for_request(self, request_id: Optional[str] = None) -> 'QualityTier':
        """Get quality tier for a specific request (allows per-request override)."""
        tier = self._request_quality_tier_var.get()
        if tier:
            return tier
        return self.quality_tier
        
    async def initialize(self):
        """Entry point for shared state initialization."""
        if self.is_initialized:
            return
            
        t_start = time.time()
        logger.info("[PROFILE] Starting AgentState.initialize()...")

        from agent_runner.memory_server import MemoryServer
        logger.info(f"[PROFILE] Imported MemoryServer ({time.time() - t_start:.3f}s)")
        
        # Initialize Memory Server Schema
        self.memory = MemoryServer(self) # Ensure instance exists
        t_mem_inst = time.time()
        await self.memory.initialize()
        logger.info(f"[PROFILE] MemoryServer.initialize() took {time.time() - t_mem_inst:.3f}s")
        
        self.is_initialized = True
        logger.info("AgentState initialized.")

        # [PHASE 46] Initialize Config Manager
        try:
            t_conf_import = time.time()
            from agent_runner.config_manager import ConfigManager
            logger.info(f"[PROFILE] Imported ConfigManager ({time.time() - t_conf_import:.3f}s)")
            
            self.config_manager = ConfigManager(self)
            
            # Start Watchdog for Hot-Swap
            try:
                self.config_manager.start_watcher()
            except Exception as watcher_err:
                logger.warning(f"File watcher failed to start: {watcher_err}")
                # Continue without file watching - manual reload still works
        except Exception as e:
            logger.warning(f"ConfigManager initialization failed: {e}")
            # Continue without config manager - no hot-reload, but system can run
            self.config_manager = None

        # [PHASE 45] Sovereign Boot Protocol
        # 1. Attempt Load from Memory (DB) - Database is source of truth
        t_db_load = time.time()
        loaded_from_db = await self._load_runtime_config_from_db()
        logger.info(f"[PROFILE] _load_runtime_config_from_db took {time.time() - t_db_load:.3f}s")
        
        # 2. [REMOVED] Sovereign Sync Check - Now handled by file watcher only
        # File watcher (started in step 0) handles disk → DB sync when files actually change.
        # Running sync on every boot was wasting 8+ seconds reading/hashing files unnecessarily.
        # Database is always the source of truth; disk files are cold backup.
        
        if loaded_from_db:
             logger.info("Sovereign Boot Successful. Runtime config loaded from Memory.")
        else:
             logger.info("Fresh Boot. Config populated from Disk.")
             # Only bootstrap if DB is confirmed empty
             await self._bootstrap_from_disk()
        
        logger.info(f"[PROFILE] AgentState.initialize() TOTAL took {time.time() - t_start:.3f}s")

    async def _load_runtime_config_from_db(self) -> bool:
        """
        Load configuration and secrets from Memory (SurrealDB).
        Returns True if data was found, False if empty.
        """
        try:
            # Query the config_state table
            query = "SELECT key, value FROM config_state"
            results = await run_query(self, query)
            
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
        Only runs if DB is confirmed empty (checked in initialize() before calling this).
        This is the ONLY place _load_base_config() should be called.
        NOTE: This method assumes DB is empty - no redundant DB check here.
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
        elif key == "QUERY_REFINEMENT_MODEL": self.query_refinement_model = val
        elif key == "FINALIZER_MODEL": self.finalizer_model = val
        elif key == "FALLBACK_MODEL": self.fallback_model = val
        elif key == "SUMMARIZATION_MODEL": self.summarization_model = val
        elif key == "ROUTER_AUTH_TOKEN": self.router_auth_token = val
        elif key == "ACTIVE_MODE": self._active_mode = val
        elif key == "MODES":
             import json
             try:
                 self.modes = json.loads(val) if isinstance(val, str) else val
             except Exception as e:
                 logger.debug(f"Failed to parse MODES: {e}")
                 self.modes = {}
        elif key == "LOCATION":
             import json
             try:
                 self.location = json.loads(val) if isinstance(val, str) else val
             except Exception as e:
                 logger.debug(f"Failed to parse LOCATION: {e}")
                 self.location = {"city": "Unknown", "error": "Parse Error"}

    def _load_defaults(self):
        """Hardcoded safety defaults."""
        self.config = {}
    
    def _load_base_config(self):
        """
        Load limits and general config from config.yaml as the baseline.
        WARNING: This should ONLY be called during bootstrap when database is confirmed empty.
        Database is the source of truth - this is only for initial population.
        """
        import yaml
        config_path = Path(__file__).parent.parent / "config" / "config.yaml"
        if config_path.exists():
            try:
                # Use async file I/O (but this is a sync method, so use to_thread)
                import aiofiles
                import asyncio
                # This is a sync method, so we need to use asyncio.to_thread for async file I/O
                # Or just use regular file I/O since this is called during sync initialization
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
            
                # [Fix] Load Location from Config
                if "location" in self.config:
                    self.location = self.config["location"]
                                
            except Exception as e:
                logger.warning(f"Failed to load config.yaml as base: {e}", exc_info=True)
        
    
    

        # Location Awareness
        self.location: Dict[str, Any] = {} # Populated by main.py on startup

    def is_local_model(self, model_name: str) -> bool:
        """Check if a model is hosted locally (e.g. Ollama, Test) and safe for offline use."""
        if not model_name:
            return False
        # Centralized safety check
        # We could load this from config, but these prefixes are standard for our architecture.
        return model_name.startswith(("ollama:", "local:", "test:"))

    def is_high_tier_model(self, model_name: str) -> bool:
        """
        Check if a model is considered 'High Tier' (Smart/Reasoning).
        High Tier models can skip auxiliary steps like Router Analysis and Finalization
        because their zero-shot instruction following is trustworthy.
        """
        if not model_name:
            return False
            
        name = model_name.lower()
        
        # 1. Known Cloud Powerhouses
        if any(x in name for x in ["gpt-4", "gpt-5", "claude-3", "gemini-1.5", "gemini-exp", "grok"]):
            return True
            
        # 2. Known Local Powerhouses
        if "70b" in name:
            return True
            
        # 3. Reasoning Models (QwQ, etc)
        if "qwq" in name or "reasoning" in name:
            return True
            
        return False

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
    def query_refinement_model(self): return self._resolve_sovereign_model(self._query_refinement_model)
    @query_refinement_model.setter
    def query_refinement_model(self, value): self._query_refinement_model = value

    @property
    def embedding_model(self): return self._resolve_sovereign_model(self._embedding_model, fallback_override="ollama:mxbai-embed-large:latest")
    @embedding_model.setter
    def embedding_model(self, value): self._embedding_model = value

    @property
    def active_mode(self): return self._active_mode
    
    @active_mode.setter
    def active_mode(self, value):
        self._active_mode = value
        # Persist to Sovereign Memory
        if hasattr(self, "config_manager"):
            # We fire and forget the async save, or rely on caller to await?
            # Property setters can't be async.
            # We must schedule it on the loop.
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self.config_manager.set_config_value("ACTIVE_MODE", value))
            except RuntimeError:
                # No loop running (e.g. during init)
                pass


    async def get_current_tempo(self) -> "Tempo":
        """
        Determine the system's operational tempo based on macOS system idle time.
        Returns a Tempo enum (FOCUSED, ALERT, REFLECTIVE, DEEP).
        """
        if self.active_requests > 0:
            return Tempo.FOCUSED
        
        # Get System Idle Time via ioreg (nanoseconds -> seconds)
        idle_seconds = 0.0
        try:
            cmd = ["ioreg", "-c", "IOHIDSystem"]
            # Non-blocking subprocess call
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await process.communicate()
            
            output = stdout.decode()
            for line in output.split('\n'):
                if "HIDIdleTime" in line:
                    parts = line.split('=')
                    if len(parts) > 1:
                        nanos = int(parts[1].strip())
                        idle_seconds = nanos / 1_000_000_000.0
                        break
        except Exception as e:
            logger.warning(f"Failed to get system tempo: {e}")
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

    async def check_and_revert_sudo(self) -> bool:
        """
        Check if system is idle and revert sudo if needed.
        Default: Revert when tempo is REFLECTIVE or deeper (user away 5+ minutes).
        Returns True if sudo was reverted, False otherwise.
        """
        if not self.admin_override_active or not self.sudo_granted_at:
            return False
        
        # Get current tempo
        current_tempo = await self.get_current_tempo()
        
        # Revert if REFLECTIVE or deeper (user away, system idle)
        tempo_values = {
            "FOCUSED": 0,
            "ALERT": 1,
            "REFLECTIVE": 2,
            "DEEP": 3
        }
        
        revert_threshold = tempo_values.get(self.sudo_revert_tempo, 2)  # Default to REFLECTIVE
        current_value = tempo_values.get(current_tempo.name, 0)
        
        if current_value >= revert_threshold:
            logger.info(f"Sudo auto-reverted: Tempo is {current_tempo.name} (user away)")
            self.admin_override_active = False
            self.sudo_granted_at = None
            return True
        
        return False

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
                logger.error(f"Failed to warm/init new MCP server '{name}': {e}", exc_info=True)
    
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
                logger.error(f"Error terminating MCP server '{name}': {e}", exc_info=True)
                
        # 2. Update In-Memory State
        del self.mcp_servers[name]
        
        # 3. Persist to Sovereign Memory + Disk
        if hasattr(self, "config_manager"):
            await self.config_manager.save_mcp_config(self.mcp_servers)
            # Delete from DB
            await run_query(self, f"DELETE FROM mcp_server WHERE name = '{name}'")
        else:
             logger.error("ConfigManager not ready for MCP removal.")
            
        return True

    async def toggle_mcp_server(self, name: str, enabled: bool, persist: bool = True) -> bool:
        """
        Dynamically enable or disable an MCP server.
        Args:
            name: Server name
            enabled: New state
            persist: If True, updates Sovereign Memory (DB) + Disk. 
                     If False, only updates runtime state (good for temporary circuit-breaking).
        """
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
                    logger.info(f"Terminated process for disabled MCP server '{name}'")
                except Exception as e:
                    logger.error(f"Error terminating MCP server '{name}': {e}", exc_info=True)
            
            # Also clear from tool cache via Engine (but State doesn't have engine ref directly easily)
            # We will handle cache clearing in the Route handler.

        # 3. Persist to Sovereign Memory + Disk (ONLY if requested)
        if persist:
            if hasattr(self, "config_manager"):
                await self.config_manager.save_mcp_config(self.mcp_servers)
                
                # DB Update: Retrieve current config + update
                # Doing full upsert is safest
                cfg = self.mcp_servers[name]
                await self.config_manager.update_mcp_server(name, cfg)
            else:
                 logger.warning(f"ConfigManager not ready for MCP toggle '{name}'")
        else:
            logger.info(f"Runtime-only toggle for '{name}' (enabled={enabled}). DB not updated.")
            
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
                logger.error(f"Error cleaning up STDIO process '{name}': {e}", exc_info=True)
                # Fallback manual kill
                if name in self.stdio_processes:
                    del self.stdio_processes[name]
