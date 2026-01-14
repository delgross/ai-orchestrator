"""
Constants used across the agent_runner module.
"""

import os

# Single source of truth for all LLM roles in the system
MODEL_ROLES = [
    "agent_model", "router_model", "task_model", "summarization_model",
    "vision_model", "mcp_model", "finalizer_model", "fallback_model",
    "intent_model", "pruner_model", "healer_model", "critic_model",
    "embedding_model"
]

# Default Models (if not in config/db)
TASK_MODEL = os.getenv("TASK_MODEL", "ollama:llama3.3:70b")
AGENT_MODEL = os.getenv("AGENT_MODEL", "ollama:llama3.3:70b")

# Log sorter service sleep interval (seconds)
SLEEP_LOG_SORTER = 5.0

# Background task watchdog scanner sleep interval (seconds)
SLEEP_WATCHDOG = 60.0

# Retry and backoff constants
DEFAULT_RETRY_ATTEMPTS = 3
SLEEP_BRIEF_BACKOFF_BASE = 0.5  # Base delay in seconds for exponential backoff

# Core MCP Services - These are critical and must be protected
# Core services have higher circuit breaker thresholds and automatic recovery
CORE_MCP_SERVERS = {
    "system-control",  # Critical: Provides get_server_status and config tools
    "time",            # Critical: Prevents hallucinations about date/time
    "filesystem",      # Critical: Needed for basic operations
    "project-memory"   # Critical: Long-term memory and context
}

# Circuit breaker thresholds for core vs non-core services
CORE_SERVICE_CB_THRESHOLD = 10  # Core services: 10 failures before opening (vs 5 for non-core)
CORE_SERVICE_CB_TIMEOUT = 30.0  # Core services: 30s recovery timeout (vs 60s for non-core)
CORE_SERVICE_AUTO_RECOVERY_INTERVAL = 15.0  # Check core services every 15s for recovery

# Token Optimization Constants
# These can be overridden via config_state table in database
TOKEN_COMPRESSION_THRESHOLD_SHORT = 200  # Skip compression if content <= this (chars)
TOKEN_COMPRESSION_RECENT_MAX = 1000      # Recent messages (age < 5) max length (chars)
TOKEN_COMPRESSION_MID_MAX = 500          # Mid messages (age 5-10) max length (chars)
TOKEN_COMPRESSION_OLD_MAX = 200          # Old messages (age >= 10) max length (chars)

# Age thresholds for compression levels
TOKEN_COMPRESSION_AGE_RECENT = 5   # Messages with age < this are "recent"
TOKEN_COMPRESSION_AGE_MID = 10     # Messages with age < this are "mid"

# JSON structure buffers (space reserved for JSON structure overhead)
TOKEN_JSON_BUFFER_SMALL = 100  # For string truncation
TOKEN_JSON_BUFFER_LARGE = 200  # For list/dict truncation

# Field lists for optimization
TOKEN_REDUNDANT_FIELDS = [
    "root", "exists", "is_file", "truncated",
    "metadata", "author", "date", "tags"
]

TOKEN_IMPORTANT_FIELDS = [
    "ok", "error", "status", "title", "snippet",
    "url", "content", "path", "data", "summary", "message"
]

# Other thresholds
TOKEN_SMALL_FIELD_THRESHOLD = 200  # Keep non-important fields if < this (chars)
TOKEN_LIST_ITEM_SIZE_FLOOR = 50    # Minimum item size for list estimation (chars)

# Transport Constants
LOCK_ACQUISITION_TIMEOUT_SECONDS = 10.0
PROCESS_INITIALIZATION_TIMEOUT_SECONDS = 20.0
NON_CORE_PROCESS_TIMEOUT_SECONDS = 15.0
PROCESS_WAIT_TIMEOUT_SECONDS = 5.0
STDERR_READ_TIMEOUT_SECONDS = 0.1

# Error Messages
ERROR_STDERR_READ_FAILED = "Failed to read stderr: {error}"
ERROR_PROCESS_CREATION_FAILED = "Failed to create process: {error}"
ERROR_PROCESS_STREAM_CLOSE_FAILED = "Failed to close process streams: {error}"
