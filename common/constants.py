"""
Centralized constants for the AI Orchestrator project.
"""

# Provider Types
PROVIDER_OPENAI_COMPAT = "openai_compat"
PROVIDER_OLLAMA = "ollama"

# Model Prefixes
PREFIX_AGENT = "agent"
PREFIX_OLLAMA = "ollama"
PREFIX_RAG = "rag"
PREFIX_OPENROUTER = "openrouter"
PREFIX_OPENAI = "openai"

# Message Roles
ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"
ROLE_SYSTEM = "system"
ROLE_TOOL = "tool"

# Object Types (OpenAI compatibility)
OBJ_CHAT_COMPLETION = "chat.completion"
OBJ_CHAT_COMPLETION_CHUNK = "chat.completion.chunk"
OBJ_MODEL = "model"
OBJ_LIST = "list"

# MCP Transport Schemes
MCP_SCHEME_HTTP = "http"
MCP_SCHEME_HTTPS = "https"
MCP_SCHEME_WS = "ws"
MCP_SCHEME_WSS = "wss"
MCP_SCHEME_UNIX = "unix"
MCP_SCHEME_STDIO = "stdio"
MCP_SCHEME_SSE = "sse"

# Common Event Names
EVENT_GATEWAY_ERROR = "gateway_error"
EVENT_TOOL_ERROR = "tool_error"
EVENT_MCP_ERROR = "mcp_error"
EVENT_OLLAMA_ERROR = "ollama_error"
EVENT_RAG_ERROR = "rag_error"

# Special Model Names
MODEL_AGENT_MCP = "agent:mcp"
MODEL_ROUTER = "router"
