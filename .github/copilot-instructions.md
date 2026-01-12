# AI Orchestrator - Copilot Instructions

## System Overview
**Antigravity** is an offline-first, resilient AI orchestration system that manages Model Context Protocol (MCP) servers, local LLMs (Ollama), and cloud providers. The system features automatic degraded-mode operation ("Gravity Mode") and extensive observability.

**Core Philosophy**: Never crash—always degrade gracefully. Log errors, add to `startup_issues`/`startup_warnings`, continue operation.

## Architecture Principles

### Nexus Gatekeeper Pattern
- **Nexus** ([agent_runner/nexus.py](agent_runner/nexus.py)) is the single entry/exit point for all chat I/O
- Nexus controls triggers, stream injection, and system messages but **delegates** all functionality
- Never implement business logic in Nexus—use it only for routing and control

### Component Boundaries
- **Router** (`:5455`): OpenAI-compatible gateway, provider management, embeddings
- **Agent Runner** (`:5460`): Tool execution, agent loops, MCP coordination
- **SurrealDB** (`:8000`): Sovereign memory—all configuration and state
- **RAG Server** (`:5555`): Optional knowledge base for semantic search

### Data Flow
```
User → Router → Agent Runner → MCP Tools → Agent Engine → Finalizer → User
                      ↓
                  SurrealDB (Memory/Config/State)
```

### Request Lifecycle
1. **Ingress**: Client → Router (`:5455`)
2. **Analysis**: Router identifies agentic vs raw model request
3. **Handoff**: Agentic requests forwarded to Agent Runner (`:5460`)
4. **Tool Selection**: Maître d' selects tools ([agent_runner/intent.py](agent_runner/intent.py))
5. **Loop**: AgentEngine runs tool-calling loop via [agent_runner/engine.py](agent_runner/engine.py)
6. **Finalization**: Finalizer synthesizes answer
7. **Egress**: Response streams back through Router to client
- All requests tracked with `X-Request-ID` header for end-to-end tracing

## Critical Developer Workflows

### Starting the System
```bash
./manage.sh start  # Starts all services via launchd/direct execution
./manage.sh status # Check what's running
./manage.sh logs   # Tail logs for debugging
```

### Boot Sequence (7 Steps)
The system follows a strict startup order ([agent_runner/main.py](agent_runner/main.py)):
0. **Startup Validation**: Checks dependencies, Python environment (validation errors don't stop boot)
1. **State Init**: Initializes AgentState, loads from SurrealDB, sets `state.system_start_time` for staggered health checks
2. **Memory Server**: Ensures schema, connects to SurrealDB
3. **MCP Discovery**: Loads servers from `config/mcp_manifests/*.json` and `config/config.yaml`
4. **Task Manager**: Starts background task scheduler (health checks, memory consolidation, internet monitor)
5. **RAG Services**: Optional knowledge base ingestion
6. **Final Checks**: Health validation, degraded mode detection

**Critical**: System continues in **degraded mode** if non-critical services fail. Check `state.degraded_reasons` for details. Each step logs `[BOOT_STEP] N/7` markers with timing.

### Configuration Hierarchy (Authority Chain)
1. **SurrealDB** (`config_state` table) — The master source of truth
2. **AgentState** (runtime) — Active in-memory cache
3. **Disk** (`config/*.yaml`) — Cold backup

**Always use** [agent_runner/config_manager.py](agent_runner/config_manager.py) to modify config—it syncs all three layers atomically. ConfigManager tracks file hashes (`meta:*_hash` keys) to detect disk changes and triggers parallel sync on boot via `check_and_sync_all()`.

**NOTE**: `.env` file is NOT directly loaded. Environment values are ingested into database via SystemIngestor, then loaded via `_load_runtime_config_from_db()`. If `.env` changes, use `ConfigManager.sync_env_from_disk()` to sync disk → DB.

### MCP Server Management
- **Discovery**: Servers auto-load from `config/mcp_manifests/*.json` and `config/config.yaml`
- **Tool Cache**: [agent_runner/engine.py](agent_runner/engine.py) maintains `mcp_tool_cache` with all available tools
- **Circuit Breaker**: Each server has per-tool circuit breaker tracking (`CLOSED`/`OPEN`/`HALF_OPEN`) via `CircuitBreakerRegistry`
- **Disabled Servers**: Check `state.disabled_servers` for servers excluded from tool selection.

**Adding a Server**:
Modify `config/config.yaml` or `config/mcp.yaml`. The system usually auto-detects changes via `ConfigManager` but a restart may be needed for profound changes.

## Project-Specific Conventions

### Error Handling & Degraded Mode
- **Never crash on startup**—log errors, add to `startup_issues`/`startup_warnings`, continue.
- Use [common/unified_tracking.py](common/unified_tracking.py) for all events:
```python
from common.unified_tracking import track_event, EventSeverity, EventCategory

track_event(
    event="mcp_server_failed",
    severity=EventSeverity.HIGH,
    category=EventCategory.MCP,
    message="Server timeout",
    metadata={"server": "memory", "timeout": 30},
    request_id=request_id  # For observability correlation
)
```

### Logging Standards
- Use **structured logging** with context via the standard `logging` library, but rely on `track_event` for system-wide visibility.
- **BOOT_STEP** markers track startup progress.
- **Request IDs** (`X-Request-ID`) flow through entire system for tracing.

### Maître d' Tool Selection Pattern
Instead of loading all tools (context bloat), the system uses an intent classification step:
1. **Tool Discovery**: `executor.discover_mcp_tools()` builds a menu.
2. **Intent Classification**: `intent.classify_search_intent()` (Maître d') inspects query + menu.
3. **Dynamic Loading**: Only relevant MCP servers are attached to the agent's context.

### Database Patterns
All SurrealDB queries use HTTP REST API ([agent_runner/memory_server.py](agent_runner/memory_server.py)):
- `fact`: Knowledge graph triples for long-term memory.
- `episode`: Chat history.
- `mcp_server`: Registered MCP servers (auto-synced).
- `chunk`: RAG document chunks with embeddings.
- `config_state`: The authoritative configuration store.

### Offline & Resilience
- **Internet Check**: `state.internet_available` flag controls access to cloud APIs.
- **Model Fallback**: Remote models redirect to `state.fallback_model` (Ollama) when offline.
- **Circuit Breakers**: `state.mcp_circuit_breaker` tracks server health. Do not bypass `state.mcp_circuit_breaker.get_breaker(server).state == "OPEN"`.

### Integration Points
- **Nexus**: The only I/O gate. Protocol: `dispatch(user_message, request_id)`.
- **Router**: Handles auth and proxying for `/v1/chat/completions`.
- **Dashboard**: `http://localhost:5455/dashboard/v2/index.html`.
