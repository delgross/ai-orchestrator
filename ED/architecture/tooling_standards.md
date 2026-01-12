# Tooling Standards (MCP Integration)

**Antigravity** uses the Model Context Protocol (MCP) as its primary interface for tools. The system acts as an MCP **Client**, aggregating tools from multiple MCP **Servers** into a unified menu.

**Source**: `ai/agent_runner/mcp_manager.py` (implied logic via `state.mcp_servers`)
**Config**: `ai/config/mcp.yaml`

---

## 1. Tool Registry Structure

Tools are defined in the Sovereign Database table `mcp_server`.

| Field | Type | Description |
| :--- | :--- | :--- |
| `name` | string | Unique identifier (e.g., `filesystem`, `tavily-search`). |
| `command` | string | Executable (e.g., `uv`, `node`, `python`). |
| `args` | list | Arguments (e.g., `["run", "mcp-server-filesystem"]`). |
| `env` | dict | Environment variables injected into the process. |
| `enabled` | bool | Master toggle. |

---

## 2. Server Categories

Tools are categorized by their lifecycle and criticality.

| Category | Servers | Behavior |
| :--- | :--- | :--- |
| **Core** | `system`, `time`, `location` | **Internal**. Always loaded. Cannot be disabled. |
| **System** | `filesystem`, `git` | **Managed**. Runs as subprocess. |
| **Network** | `tavily-search`, `fetch` | **Managed**. Requires internet. |
| **External** | `sonos`, `home-assistant` | **Remote**. Connects over SSE/HTTP (optional). |

---

## 3. The Constraint Protocol (Maître d')

To ensure the LLM selects the correct tool, every tool must map to a specific **Constraint ID** in `Maître d'`.

| Tool | Constraint ID | Trigger Keywords |
| :--- | :--- | :--- |
| `tavily-search` | 9, 10 | "news", "headlines", "real-time", "breaking", "politics" |
| `filesystem` | 4 | "read", "write", "list", "file" |
| `system` | 5, 5.5 | "config", "architecture", "restart", "health" |
| `memory` | 11 | "recall", "remember", "preferences", "discussed" |
| `advice` | 6 | (Dynamic based on topic list) |

---

## 4. Execution Flow

1.  **Selection**: Maître d' returns `target_servers: ["filesystem"]`.
2.  **Activation**: `AgentEngine` retrieves the `filesystem` tool schema from `state.mcp_servers`.
3.  **Injector**: The tool schema is injected into the LLM context.
4.  **Call**: LLM outputs tool call `{"name": "filesystem_read_file", ...}`.
5.  **Routing**: `AgentRunner` finds the [`filesystem`] MCP Server process.
6.  **RPC**: Request sent via JSON-RPC over Stdio/SSE.
7.  **Result**: Output captured, truncated (if > `MAX_READ_BYTES`), and returned to LLM.

---

## 5. Safety Limits

| Limit | Env Var | Default | Description |
| :--- | :--- | :--- | :--- |
| **Read Size** | `AGENT_MAX_READ_BYTES` | 50MB | Max output from any tool before truncation. |
| **List Size** | `AGENT_MAX_LIST_ENTRIES` | 5000 | Max items in `ls -R` or similar. |
| **Step Count** | `AGENT_MAX_TOOL_STEPS` | 20 | Max distinct tool calls per request. |
| **Total Tools** | `AGENT_MAX_TOOLS` | 120 | Max tools loaded in context (soft limit). |
