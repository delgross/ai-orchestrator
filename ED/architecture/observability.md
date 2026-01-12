# Observability & Unified Tracking

**Antigravity** employs a unified event tracking system that serves as the central nervous system for all observability, logging, and notifications. It tracks every request through a defined lifecycle state machine, aggregates performance metrics, and exposes deep inspection APIs.

**Source**: `ai/common/unified_tracking.py`
**Reference**: `ai/docs/api/observability.md` (Legacy Golden Master)

---

## 1. Request Lifecycle State Machine

Every request is tracked through a strict sequence of stages. Timestamps are recorded at each transition for bottleneck analysis.

| Stage ID | Description |
| :--- | :--- |
| **RECEIVED** | Request entered the system boundary. |
| **AUTH_CHECKED** | Authentication token verified (or failed). |
| **PARSED** | Request body successfully parsed into Pydantic model. |
| **ROUTING_DECIDED** | Router logic has selected the upstream target or internal handler. |
| **UPSTREAM_CALL_START** | Outbound call to LLM Provider or Agent Runner initiated. |
| **UPSTREAM_CALL_END** | Response received from upstream service. |
| **PROCESSING** | Internal logic execution / Tool use loops. |
| **RESPONSE_SENT** | HTTP response flushed to the client. |
| **COMPLETED** | Lifecycle fully closed, resources released. |
| **ERROR** | Exception or strict failure occurred. |
| **TIMEOUT** | Hard time limit exceeded. |

---

## 2. Observability API Registry (Port 5455/5460)

These endpoints provide real-time introspection into the engine state. All require Admin Auth.

| Endpoint | Method | Response Structure (Condensed) | Purpose |
| :--- | :--- | :--- | :--- |
| `/admin/observability/metrics` | `GET` | `{"active_requests": 5, "error_rate_1min": 0.05, "component_health": Map<ID, Health>}` | High-level dashboard feed. |
| `/admin/observability/active-requests` | `GET` | `{"active_requests": Map<ReqID, RequestData>}` | Spy on currently executing agents. |
| `/admin/observability/stuck-requests` | `GET` | `{"stuck_requests": List<RequestData>}` | Requests exceeding `timeout_seconds`. |
| `/admin/observability/performance` | `GET` | `{"p50_ms": 200, "p95_ms": 800, "count": 1000}` | Latency analysis (min/max/avg/percentiles). |
| `/admin/observability/component-health` | `GET` | `{"component_health": Map<ID, HealthStatus>}` | Strict health check of all subsystems. |
| `/admin/observability/export` | `POST` | `{"export_path": "/path/to/dump.json"}` | Full state dump for offline analysis. |

---

## 3. Component Health Model

Health status creates a unified view of system availability.

**Health Status Enum**:
- `HEALTHY`: Functional.
- `DEGRADED`: Functional but impaired (latency/errors).
- `UNHEALTHY`: Non-functional / Crash loop.
- `UNKNOWN`: No data.

**Health Object Schema**:
```json
{
  "component_type": "AGENT_RUNNER | MCP_SERVER | DATABASE",
  "component_id": "string (unique)",
  "status": "HEALTHY",
  "last_check": 1715000000.0,
  "response_time_ms": 15.2,
  "error_count": 0,
  "success_count": 100,
  "metadata": {}
}
```

---

## 4. Event Routing Matrix

The `track_event()` function routes signals based on **Category** and **Severity**.

| Destination | Condition | Description |
| :--- | :--- | :--- |
| **JSON Logger** | **Always** | Logs to `logs/events.jsonl` for machine parsing. |
| **Observability** | `Health`, `MCP`, `Error` | Updates `ComponentHealth` state (Green/Yellow/Red). |
| **Notifications** | `High`, `Critical` | Desktop/Mobile alerts (via `notify-send` equivalent). |
| **System Blog** | `System`, `Anomaly`, `Config` | Human-readable narrative log (`system_blog.md`). |
| **Dashboard** | `Dashboard` | Frontend-specific error/interaction tracking. |

---

## 5. Event Category Registry

| Category | Value | Usage Scenario |
| :--- | :--- | :--- |
| **ERROR** | `error` | Exceptions, crashes, stack traces. |
| **HEALTH** | `health` | Heartbeat failures, probing results. |
| **PERFORMANCE** | `performance` | Latency spikes, memory pressure. |
| **SECURITY** | `security` | Authentication failures, permission denials. |
| **CONFIG** | `config` | Dynamic config changes, database syncs. |
| **TASK** | `task` | Cron job executions (e.g., backups). |
| **MCP** | `mcp` | Tool execution, server lifecycle events. |
| **DASHBOARD** | `dashboard` | UI rendering errors. |
| **SYSTEM** | `system` | Startup/Shutdown, Update events. |
| **ANOMALY** | `anomaly` | Statistical outliers (Budget, Traffic). |

---

## 6. Implementation Details

- **Stuck Request Logic**: A request is "stuck" if `Age > Timeout` OR `TimeSinceLastStage > StageTimeout`.
- **Data Retention**:
    - Active Requests: Max 1000
    - Completed Requests: Max 10,000
    - Metrics: Max 50,000
- **fire-and-forget**: Tracking is async; it must never block the request loop.

