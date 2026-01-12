# Router API Reference (Port 5455)

The Router is the primary ingress gateway for the system. It handles authentication, rate limiting, and request routing. All client applications (Chat UI, IDE Extensions, etc.) should talk to this port.

**Base URL**: `http://127.0.0.1:5455`

## 🔐 Authentication
Most endpoints require the `Authorization` header.
```bash
Authorization: Bearer <ROUTER_AUTH_TOKEN>
```
The token is defined in `.env` or `config/router.env`.

---

## 🚀 Chat & Completions

### `POST /v1/chat/completions`
OpenAI-compatible chat completion endpoint.

**Headers**:
- `X-Quality-Tier`: `speed` | `balanced` | `high` (Optional)
- `X-Request-ID`: `uuid` (Optional, for tracing)

**Body**:
```json
{
  "model": "agent:mcp", // or "ollama:llama3", "claude-3-opus"
  "messages": [
    {"role": "user", "content": "Hello"}
  ],
  "stream": true,
  "temperature": 0.7
}
```

**Model Prefixes**:
- `agent:` -> Forwards to **Agent Runner** (Tools, Memory).
- `ollama:` -> Forwards to local **Ollama** instance.
- `rag:` -> Uses RAG server for context.
- `openai:` / `anthropic:` -> External proxies.
- (None) -> Defaults to `agent:mcp`.

---

## 🛠 Management & Admin

### `GET /`
Service root.
- **Accept: application/json**: Returns `{"ok": True, "version": "..."}`.
- **Accept: text/html**: Redirects to Dashboard.

### `GET /health`
Basic health check. Returns 200 OK if the process is running.

### `GET /v1/models`
Lists all available models aggregated from:
1. Local Ollama instance.
2. Agent Runner capabilities.
3. External providers config.

**Response**:
```json
{
  "object": "list",
  "data": [
    {"id": "agent:mcp", "object": "model"},
    {"id": "ollama:llama3", "object": "model"}
  ]
}
```

### `GET /dashboard`
Redirects to the Dashboard UI (`/v2/index.html`).

### `GET /metrics`
Prometheus-style metrics or JSON metrics for the router.
- Active connections
- Request throughput
- Circuit breaker states

---

## 🔌 Admin / Configuration
*Endpoints usually prefixed with `/admin` or internal tools.*

### `POST /admin/reload`
Reloads the `providers.yaml` configuration from disk without restarting the server.

### `POST /admin/cache/clear`
Clears internal LRU caches (routing tables, model lists).

### `GET /admin/mcp-toggle`
**Response**: `{"enabled": true}`
Check if MCP tools are globally enabled.

### `POST /admin/mcp-toggle`
**Body**: `{"enabled": false}`
Emergency switch to disable all tool execution through the router.

---

## 🎨 UI Tools

### `GET /prompt-inspector`
Serves an interactive HTML tool for:
1. Inspecting the active system prompt.
2. Testing query classification logic.
3. Evaluating response quality.
