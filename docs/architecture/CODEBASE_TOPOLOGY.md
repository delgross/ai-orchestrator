# Codebase Topology & System Pathways

This document maps the physical code structure to the logical architecture and traces the critical "Pathways" that data and requests follow through the system.

## 🗺 Directory Map

| Directory | Role | Key Files |
| :--- | :--- | :--- |
| `agent_runner/` | **Execution Core** | `engine.py` (Logic), `main.py` (API), `feedback.py` (Learning) |
| `router/` | **Gateway / Proxy** | `main.py` (FastAPI), `providers.py` (Ollama/OpenAI logic) |
| `common/` | **Shared Services** | `unified_tracking.py`, `anomaly_detector.py`, `observability.py` |
| `dashboard/` | **Frontend** | `index.html`, `app.js` (System status & Chat) |
| `config/` | **Configuration** | `config.yaml` (Static defaults), `system_config.json` (Dashboard overrides) |
| `bin/` | **Executables** | Shell scripts for service management and diagnostics. |

---

## 🏎 System Pathways

### 1. The Request Lifecycle (Client ➜ Response)
This is the North-South pathway for user interaction.

1.  **Ingress**: A client (LibreChat or Dashboard) sends an OpenAI-compatible request to the **Router** (`:5455`).
2.  **Analysis**: `router/main.py` identifies if the request is for a raw model or an agentic loop.
3.  **Handoff**: Agentic requests are forwarded to the **Agent Runner** (`:5460`).
4.  **Loop**: The `AgentEngine` in `agent_runner/engine.py` runs the tool-calling loop.
5.  **Finalization**: Once tools are done, the `Finalizer` role synthesizes the final answer.
6.  **Egress**: The response streams back through the Router to the Client.

### 2. The Tool Pathway (Discovery ➜ Execution)
This traces how the system gains and uses capabilities.

1.  **Discovery**: On startup, `agent_runner/mcp_parser.py` reads server configs.
2.  **Selection (Maître d')**: When a query arrives, `engine.py` calls the Maître d' to select relevant servers based on the menu and history (`feedback.py`).
3.  **Connection**: The runner establishes Stdio/SSE transports to the selected MCP servers via `agent_runner/transports/`.
4.  **Execution**: The agent sends JSON-RPC calls to the servers and receives tool outputs.

### 3. The Resilience Pathway (Gravity Mode)
This is the safety pathway that ensures 100% uptime.

1.  **Detection**: `common/observability.py` or the Router's heartbeat detects a network failure.
2.  **Interception**: `agent_runner/state.py` flips the `internet_available` flag.
3.  **Re-routing**: The Router automatically redirects any `openai:*` or `anthropic:*` requests to the local `FALLBACK_MODEL` (Ollama).
4.  **Notification**: The Unified Tracking layer broadcasts the "Gravity Mode Active" event to the dashboard and notifications.

---

## 🛠 Common Operations
- **Adding a Tool**: Add an MCP server to `config/mcp_servers.json`. The Maître d' will automatically discover it on restart.
- **Changing Models**: Edit `system_config.json` via the dashboard. `agent_runner/state.py` ensures these takes precedence over the YAML files.
- **Debugging a Request**: Use the `X-Request-ID` from the logs to trace the event through `agent_runner.log` and the Unified Tracker.
