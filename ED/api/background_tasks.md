# Background Tasks Catalog

Antigravity relies on a suite of autonomous background tasks to maintain system health, optimize memory, and gather intelligence. These tasks run independently of user requests.

**Source**: `ai/agent_runner/tasks.py`, `ai/agent_runner/background_tasks.py`

---

## 1. System Maintenance

| Task Name | Schedule | Description |
| :--- | :--- | :--- |
| `health_check` | 60s | Pings critical services (SurrealDB, Router) and updates `current_health.json`. |
| `internet_check` | 5m | Verifies external connectivity to `1.1.1.1` or `8.8.8.8`. Toggles `offline_mode`. |
| `log_cleanup` | 24h | Rotates and compresses logs in `logs/` to prevent disk saturation. |
| `surreal_backup` | 24h | Dumps the Sovereign Knowledge Graph to `agent_data/backups/`. |

---

## 2. Intelligence & Research

| Task Name | Schedule | Tempo Requirement | Description |
| :--- | :--- | :--- | :--- |
| `research_cycle` | 4h | **Reflective** | Spawns a sub-agent to browse configured RSS feeds (e.g., Ohio News) and ingest relevant articles. |
| `intel_consolidation` | 6h | **Deep** | Analyzes the `fact` table for duplicates and consolidates related nodes using the `SUMMARIZATION_MODEL`. |
| `mcp_intel` | 12h | **Any** | Queries all connected MCP servers for their capabilities description and updates the Tool Registry. |

---

## 3. RAG & Memory

| Task Name | Schedule | Description |
| :--- | :--- | :--- |
| `vector_reindex` | On-Demand | Rebuilds the HNSW vector index in SurrealDB. Triggered after bulk ingestion. |
| `memory_fact_stats` | 1h | Calculates statistics (Total Facts, Avg Confidence, Knowledge Distribution) for the dashboard. |

---

## 4. Control Logic

### Tempo Awareness
Certain tasks (like `intel_consolidation`) are computationally expensive. They are configured with `idle_only=True` via the Sovereign DB.
- If the agent is **FOCUSED** (User chatting), these tasks are skipped.
- They only activate when the system enters **DEEP** idle (> 30m inactivity).

### Manual Triggers
Any task can be force-started via the Admin API:
```bash
POST /admin/background-tasks/research_cycle/trigger
```
