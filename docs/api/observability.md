# Observability System

## Overview

The observability system provides comprehensive monitoring, debugging, and performance analysis capabilities for the AI Orchestrator. It tracks every request through its complete lifecycle, records performance metrics at every stage, monitors component health, and provides tools for analyzing system behavior.

## Features

### Request Lifecycle Tracking

Every request is tracked through multiple stages:
- `RECEIVED` - Request received
- `AUTH_CHECKED` - Authentication verified
- `PARSED` - Request body parsed
- `ROUTING_DECIDED` - Routing decision made
- `UPSTREAM_CALL_START` - Upstream service call started
- `UPSTREAM_CALL_END` - Upstream service call completed
- `PROCESSING` - Request being processed
- `RESPONSE_SENT` - Response sent to client
- `COMPLETED` - Request fully completed
- `ERROR` - Error occurred
- `TIMEOUT` - Request timed out

Each stage transition is timestamped, allowing precise identification of where time is spent.

### Performance Metrics

Performance metrics are recorded for:
- Component operations (router, agent-runner, MCP servers, providers)
- Operation types (parse_body, upstream_call, etc.)
- Duration in milliseconds
- Associated metadata

Metrics are aggregated to provide:
- Min, max, average response times
- Percentiles (p50, p95, p99)
- Counts and rates

### Component Health Monitoring

All system components are monitored:
- Router
- Agent-runner
- MCP servers
- Providers
- Database
- Cache

Health status includes:
- Current status (healthy, degraded, unhealthy, unknown)
- Response times
- Error and success counts
- Last check timestamp
- Component-specific metadata

### Stuck Request Detection

The system automatically identifies requests that appear to be stuck:
- Age of request
- Time since last stage change
- Current stage
- Full request metadata

### Data Export

All observability data can be exported for analysis:
- Active requests
- Recent completed requests (last 1000)
- Performance metrics (last 5000)
- Component health
- Recent errors (last 1000)
- System metrics history (last 100 snapshots)

## API Endpoints

All endpoints require authentication via the router auth token.

### GET /admin/observability/metrics

Get current system metrics snapshot.

**Response:**
```json
{
  "ok": true,
  "metrics": {
    "timestamp": 1234567890.0,
    "active_requests": 5,
    "completed_requests_1min": 42,
    "error_rate_1min": 0.05,
    "avg_response_time_1min": 1250.5,
    "component_health": {...},
    "resource_usage": {...}
  }
}
```

### GET /admin/observability/active-requests

Get all currently active requests with full lifecycle information.

**Response:**
```json
{
  "ok": true,
  "active_requests": {
    "abc123": {
      "request_id": "abc123",
      "method": "POST",
      "path": "/v1/chat/completions",
      "stage": "PROCESSING",
      "stages": {...},
      "metadata": {...},
      "performance_metrics": [...],
      "started_at": 1234567890.0
    }
  },
  "count": 1
}
```

### GET /admin/observability/stuck-requests

Get requests that appear to be stuck (exceeded timeout).

**Query Parameters:**
- `timeout_seconds` (float, default: 30.0) - Timeout threshold

**Response:**
```json
{
  "ok": true,
  "stuck_requests": [
    {
      "request_id": "abc123",
      "age_seconds": 45.2,
      "time_since_last_stage_seconds": 30.1,
      "current_stage": "UPSTREAM_CALL_START",
      "path": "/v1/chat/completions",
      "method": "POST",
      "stages": {...},
      "metadata": {...}
    }
  ],
  "count": 1
}
```

### GET /admin/observability/performance

Get performance summary for analysis.

**Query Parameters:**
- `component` (optional) - Filter by component name
- `operation` (optional) - Filter by operation name

**Response:**
```json
{
  "ok": true,
  "summary": {
    "count": 1000,
    "min_ms": 10.5,
    "max_ms": 5000.0,
    "avg_ms": 250.3,
    "p50_ms": 200.0,
    "p95_ms": 800.0,
    "p99_ms": 2000.0
  }
}
```

### GET /admin/observability/component-health

Get health status of all components.

**Response:**
```json
{
  "ok": true,
  "component_health": {
    "agent_runner:agent_runner": {
      "component_type": "AGENT_RUNNER",
      "component_id": "agent_runner",
      "status": "healthy",
      "last_check": 1234567890.0,
      "response_time_ms": 15.2,
      "error_count": 0,
      "success_count": 100,
      "metadata": {...}
    }
  }
}
```

### POST /admin/observability/export

Export all observability data for analysis.

**Response:**
```json
{
  "ok": true,
  "export_path": "/path/to/export_1234567890.json",
  "message": "Data exported successfully"
}
```

## Usage Examples

### Check for Stuck Requests

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:5455/admin/observability/stuck-requests?timeout_seconds=30"
```

### Get Performance Summary for Agent-Runner

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:5455/admin/observability/performance?component=agent_runner"
```

### Export All Data for Analysis

```bash
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:5455/admin/observability/export"
```

## Integration

The observability system is automatically integrated into:
- Router middleware (tracks all requests)
- Router chat completions endpoint (detailed stage tracking)
- Agent-runner (to be integrated)

All data is stored in memory with configurable limits:
- Active requests: 1000 max
- Completed requests: 10000 max
- Performance metrics: 50000 max
- Recent errors: 1000 max
- System metrics history: 1000 max

## Analysis

Exported data can be analyzed using:
- Python scripts
- Jupyter notebooks
- Data analysis tools (pandas, etc.)
- Visualization tools

The exported JSON contains all request lifecycles, performance metrics, and component health data, allowing for comprehensive post-mortem analysis and performance optimization.






