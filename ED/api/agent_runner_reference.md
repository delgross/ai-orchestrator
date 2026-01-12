# Agent Runner API Reference (Port 5460)

The Agent Runner is the "Brain" of the operation. It executes complex tasks, manages memory (SurrealDB), and orchestrates MCP tools. While the Router (5455) is the public face, the Runner (5460) exposes deep introspection endpoints.

**Base URL**: `http://127.0.0.1:5460`

---

## 🩺 Health & Diagnostics

### `GET /health`
Quick status check.
```json
{
  "status": "healthy",
  "ok": true,
  "internet": true,
  "uptime_s": 123.45
}
```

### `GET /admin/health/detailed`
Complete system topology report. Checks:
- **Memory Server**: Connection status & latency.
- **Gateway**: Connectivity to Router.
- **MCP Servers**: Individual health of every tool process.

### `GET /metrics`
Detailed observability metrics.
```json
{
  "requests": 150,
  "errors": 2,
  "avg_latency_ms": 450.2,
  "observability": { ... }
}
```

---

## 🧠 Memory & Ingestion

### `GET /admin/memory/status`
Checks connection to Sovereign Memory (SurrealDB).
**Response**:
```json
{
  "ok": true,
  "engine": "SurrealDB",
  "mode": "Transactional (HNSW Enabled)"
}
```

### `GET /admin/ingestion/status`
Checks the state of the background RAG ingestion pipeline.
- `paused`: Boolean.
- `reason`: String (e.g., "Manual Pause" or error message).
- `ingest_dir`: Path being watched.

### `POST /admin/ingestion/pause`
Manually halts document indexing (creates `.paused` lockfile).

### `POST /admin/ingestion/resume`
Resumes indexing (removes lockfile).

### `POST /admin/ingestion/clear-and-resume`
**Dangerous**: Deletes the specific file that caused a pipeline crash and instantly resumes indexing. Use when a corrupt PDF is blocking the queue.

---

## ⚙️ System Control

### `GET /admin/system-status`
Returns high-level operational state.
- **Idle Detection**: Current "Tempo" (Focused/Reflective/Deep).
- **Load**: Active request count.

### `GET /admin/background-tasks`
Lists all registered background tasks and their schedule status.

### `POST /admin/background-tasks/{task_name}/trigger`
Manually forces a background task to run immediately (e.g., `trigger_reindex`).

### `GET /admin/config`
Dumps the currently active configuration (Combined result of DB + Defaults).
*Note: Secrets are masked.*

---

## 🛠 Development & Debugging

### `GET /admin/dev/logs`
Tail the last N lines of the system logs via WebSocket or JSON.

### `POST /admin/dev/clear-cache`
Flushes internal Python artifacts (`__pycache__`, `.pyc`) and reloads modules where possible.
