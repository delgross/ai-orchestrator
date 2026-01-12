# Memory System (Sovereign Storage)

**Antigravity** relies on **SurrealDB** as its sovereign memory store. Unlike simple file-based memory, this provides structured, queryable, and graph-like relationships between entities.

**Source**: `ai/agent_runner/memory_server.py`

---

## 1. Architecture

The `MemoryServer` class manages the connection to SurrealDB.

- **Protocol**: HTTP/REST (Port 8000). RPC/Websocket is avoided for stability.
- **Connection**: Uses `httpx.AsyncClient` with connection pooling and keep-alive.
- **Robustness**:
    - **Startup Retry**: Attempts connection 5 times with exponential backoff.
    - **Circuit Breaker**: If DB fails during runtime, the system enters "Degraded Mode" (`state.memory_unstable = True`) rather than crashing.

---

## 2. Schema Definitions

The memory is structured into specific tables (defined via `DEFINE TABLE`):

### `fact` (Knowledge Graph)
Stores atomic units of knowledge.
- `entity`: Subject (e.g., "User").
- `relation`: Predicate (e.g., "prefers").
- `target`: Object (e.g., "Python").
- `embedding`: Vector representation (1024 dim) for semantic search.

### `episode` (Chat History)
Stores the raw conversation log.
- `session_id`: Conversation grouping.
- `role`: user/assistant/system.
- `content`: The text.
- `embedding`: Vector for "Recall" functionality.

### `mcp_server` (Tool Registry)
Stores the configuration of available tools.
- This is the source of truth for the Maître d' menu.

---

## 3. Transaction Safety

The `_execute_query` method handles the complexity of reliability:

1.  **Validation**: Blocks harmful SQL patterns.
2.  **Transactions**: Detects `BEGIN TRANSACTION` and attempts auto-rollback on failure.
3.  **Parsers**: Suppresses "already exists" errors to ensure idempotency during schema setup.

---

## 4. Vector Search

The system uses SurrealDB's native vector support (`MTREE` index).

```sql
SELECT * FROM fact 
WHERE embedding <|5|> $query_vector 
AND confidence > 0.7
```

This allows the agent to perform RAG (Retrieval Augmented Generation) directly against its sovereign memory without needing a separate Pinecone/Weaviate instance.
