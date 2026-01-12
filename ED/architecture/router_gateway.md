# Router Gateway (API Entry Point)

The **Router** is the unified API Gateway for the Antigravity system. It provides an OpenAI-compatible interface on **Port 5455** that multiplexes requests to local models (Ollama), the Agent Runner, RAG systems, and external providers.

**Source**: `ai/router/main.py`
**Routes**: `ai/router/routes/chat.py`

---

## 1. Route Table

| Method | Path | Target | Description |
| :--- | :--- | :--- | :--- |
| **POST** | `/v1/chat/completions` | Dispatcher | Main OpenAI-compatible chat endpoint. |
| **GET** | `/health` | Self | Router health check (checks dependencies). |
| **GET** | `/v1/models` | Aggregator | Lists all available models from all providers. |
| **POST** | `/v1/embeddings` | `ollama` | Proxies embedding requests to local model. |

---

## 2. Dispatch Logic (Prefix Routing)

The router determines the destination based on the `model` string prefix or alias.

| Prefix / Model | Destination | Handler Type | Timeout |
| :--- | :--- | :--- | :--- |
| `agent:` | **Agent Runner** | HTTP Proxy | 120s |
| `ollama:` | **Local Ollama** | streaming/direct | - |
| `rag:` | **RAG Server** | RPC/HTTP | 30s |
| `openai:` | `api.openai.com` | External Proxy | 120s |
| `anthropic:` | `api.anthropic.com` | External Proxy | 120s |
| `perplexity:` | `api.perplexity.ai` | External Proxy | 60s |
| (no prefix) | **Agent Agent** | Default Fallback | 120s |

**Aliases**:
- `Questionable Insight` -> `agent:mcp`
- `router:default` -> `ollama:llama3.1` (or configured router model)

---

## 3. Headers & Control

The router accepts specific headers to control behavior.

| Header | Value type | Effect |
| :--- | :--- | :--- |
| `Authorization` | `Bearer <token>` | Validates against `ROUTER_AUTH_TOKEN`. |
| `X-Request-ID` | UUID | Propagated to all downstream services for tracing. |
| `X-Quality-Tier` | `speed` \| `balanced` \| `high` | Sets execution tier for Agent Runner. |

---

## 4. Async Mode (Fire & Forget)

If `state.router_mode = "async"`, the router changes behavior to support long-running tasks without holding the connection.

**Behavior**:
1.  Client sends `POST`.
2.  Router spawns background `asyncio.Task`.
3.  Router immediately returns **202 Accepted**.
4.  Response Payload:
    ```json
    {
      "id": "chatcmpl-123456",
      "object": "chat.completion.async",
      "status": "accepted",
      "message": "Request accepted for background processing."
    }
    ```

**Note**: Streaming requests (`stream=True`) override this and force **Synchronous** mode to maintain the SSE connection.

---

## 5. Circuit Breakers

The Router maintains its own `CircuitBreakerRegistry` (`ai/common/circuit_breaker.py`) distinct from the Agent's.

- **Threshold**: 5 failures in 60 seconds.
- **Action**: Returns **503 Service Unavailable** instantly for that provider.
- **Deadlock Protection**: The "Watchdog" task checks if *both* Ollama and Agent Runner are down. If so, it force-resets the breakers to prevent a "deadlock" where the router waits for the agent which waits for the router.
