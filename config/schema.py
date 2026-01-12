"""
Configuration schema documentation for AI Orchestrator.

This defines all configuration options and their types/defaults.
This will be used for validation when unified config is implemented.
"""

from typing import Dict, Optional
from dataclasses import dataclass, field


@dataclass
class RouterConfig:
    """Router service configuration."""
    # Core URLs
    ollama_base: str = "http://127.0.0.1:11434"
    agent_runner_url: str = "http://127.0.0.1:5460"
    
    # Development
    dev_mode: bool = False
    
    # Optional: RAG
    rag_base: Optional[str] = None
    rag_query_path: str = "/query"
    
    # Optional: Providers
    providers_yaml: str = "~/ai/providers.yaml"
    
    # Optional: Security
    router_auth_token: Optional[str] = None
    router_max_concurrency: int = 0  # 0 = unlimited
    
    # Optional: Performance
    models_cache_ttl_s: float = 600.0
    http_timeout_s: float = 120.0
    max_request_body_bytes: int = 5_000_000
    default_upstream_headers: Optional[str] = None


@dataclass
class AgentRunnerConfig:
    """Agent-runner service configuration."""
    # Core
    agent_model: str = "openai:gpt-4.1-mini"
    gateway_base: str = "http://127.0.0.1:5455"
    agent_fs_root: str = "~/ai/agent_fs_root"
    
    # Development
    dev_mode: bool = False
    
    # MCP Servers (comma-separated: name=url)
    mcp_servers: str = ""
    # MCP API Keys (env vars: MCP_TOKEN_<NAME>, FIRECRAWL_API_KEY, TAVILY_API_KEY, etc.)
    
    # Environment
    pythonioencoding: str = "utf-8"
    
    # Persistence
    agent_persistence_dir: str = "~/ai/agent_data"
    tool_cache_enabled: bool = True
    tool_cache_ttl: float = 300.0
    
    # Performance monitoring
    performance_alert_threshold_ms: float = 5000.0
    performance_degradation_factor: float = 2.0
    
    # Circuit breaker (optional)
    mcp_circuit_breaker_threshold: int = 5
    mcp_circuit_breaker_timeout: float = 60.0
    
    # Retry logic (optional)
    tool_retry_attempts: int = 2
    tool_retry_backoff_factor: float = 0.5
    
    # File operation limits (optional)
    agent_max_read_bytes: int = 200_000
    agent_max_list_entries: int = 500
    agent_max_tool_steps: int = 8
    
    # HTTP timeout (optional)
    agent_http_timeout_s: float = 120.0


@dataclass
class UnifiedConfig:
    """Future unified configuration structure."""
    router: RouterConfig = field(default_factory=RouterConfig)
    agent_runner: AgentRunnerConfig = field(default_factory=AgentRunnerConfig)
    # Future: Add other services here
    # dashboard: DashboardConfig = field(default_factory=DashboardConfig)


# Configuration key mappings (for backward compatibility)
CONFIG_KEY_MAPPINGS: Dict[str, str] = {
    # Router
    "OLLAMA_BASE": "ollama_base",
    "AGENT_RUNNER_URL": "agent_runner_url",
    "DEV_MODE": "dev_mode",
    "RAG_BASE": "rag_base",
    "RAG_QUERY_PATH": "rag_query_path",
    "PROVIDERS_YAML": "providers_yaml",
    "ROUTER_AUTH_TOKEN": "router_auth_token",
    "ROUTER_MAX_CONCURRENCY": "router_max_concurrency",
    "MODELS_CACHE_TTL_S": "models_cache_ttl_s",
    "HTTP_TIMEOUT_S": "http_timeout_s",
    "MAX_REQUEST_BODY_BYTES": "max_request_body_bytes",
    "DEFAULT_UPSTREAM_HEADERS": "default_upstream_headers",
    
    # Agent-runner
    "AGENT_MODEL": "agent_model",
    "GATEWAY_BASE": "gateway_base",
    "AGENT_FS_ROOT": "agent_fs_root",
    "MCP_SERVERS": "mcp_servers",
    "PYTHONIOENCODING": "pythonioencoding",
    "AGENT_PERSISTENCE_DIR": "agent_persistence_dir",
    "TOOL_CACHE_ENABLED": "tool_cache_enabled",
    "TOOL_CACHE_TTL": "tool_cache_ttl",
    "PERFORMANCE_ALERT_THRESHOLD_MS": "performance_alert_threshold_ms",
    "PERFORMANCE_DEGRADATION_FACTOR": "performance_degradation_factor",
    "MCP_CIRCUIT_BREAKER_THRESHOLD": "mcp_circuit_breaker_threshold",
    "MCP_CIRCUIT_BREAKER_TIMEOUT": "mcp_circuit_breaker_timeout",
    "TOOL_RETRY_ATTEMPTS": "tool_retry_attempts",
    "TOOL_RETRY_BACKOFF_FACTOR": "tool_retry_backoff_factor",
    "AGENT_MAX_READ_BYTES": "agent_max_read_bytes",
    "AGENT_MAX_LIST_ENTRIES": "agent_max_list_entries",
    "AGENT_MAX_TOOL_STEPS": "agent_max_tool_steps",
    "AGENT_HTTP_TIMEOUT_S": "agent_http_timeout_s",
}




















