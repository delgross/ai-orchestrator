# Unified Tracking System - Migration Guide

## Overview

The unified tracking system (`common/unified_tracking.py`) provides a **single entry point** for all tracking needs, routing events to:
- Observability system (performance/request tracking)
- Notification system (alerts)
- JSON event logging (structured logs)
- System blog (human-readable logs)
- Dashboard tracker (dashboard errors)

## Why This Matters

**Before**: Each subsystem used different tracking mechanisms:
- MCP failures → JSON events + notifications (but not observability)
- Dashboard errors → Dashboard tracker only (not notifications)
- Health issues → Notifications only (not observability)
- Circuit breakers → JSON events + notifications (but not observability)

**After**: One call routes to all appropriate systems automatically.

## Usage Examples

### Basic Event Tracking

```python
from common.unified_tracking import track_event, EventSeverity, EventCategory

# Track an MCP server failure
track_event(
    event="mcp_server_failed",
    severity=EventSeverity.HIGH,
    category=EventCategory.MCP,
    message="Memory server failed to respond",
    metadata={"server": "memory", "error": "timeout"},
    component="mcp_client"
)
# This automatically:
# - Logs JSON event
# - Sends notification (HIGH severity)
# - Records in observability (if applicable)
```

### Convenience Functions

```python
from common.unified_tracking import (
    track_error,
    track_health_event,
    track_mcp_event,
    track_dashboard_event
)

# Track an error
track_error(
    event="database_connection_failed",
    message="SurrealDB connection lost",
    error=exception,
    component="memory_server",
    severity=EventSeverity.CRITICAL
)

# Track MCP event
track_mcp_event(
    event="mcp_server_recovered",
    message="Memory server recovered",
    server="memory",
    severity=EventSeverity.INFO
)

# Track dashboard error
track_dashboard_event(
    event="refresh_failed",
    message="Failed to refresh model services",
    error=exception,
    component="model-services",
    request_id="abc123"
)
```

## Migration Strategy

### Phase 1: Add Unified Tracking (Non-Breaking)

1. **Keep existing code unchanged** - all existing tracking still works
2. **Add unified tracking alongside** - new code uses unified tracking
3. **Gradually migrate** - convert old code when convenient

### Phase 2: Migrate High-Value Components

Priority order:
1. **MCP Circuit Breakers** - High visibility, many events
2. **Dashboard Tracker** - Already identified as siloed
3. **Health Monitor** - Important for system health
4. **Background Tasks** - Task failures need tracking

### Phase 3: Complete Migration

- All new code uses unified tracking
- Old tracking calls deprecated but still work
- Eventually remove old direct calls

## Migration Examples

### Before (MCP Circuit Breaker)

```python
# Old way - multiple systems
_log_json_event("mcp_server_disabled", server=server, failures=cb["failures"])
notify_high(
    title=f"MCP Server Disabled: {server}",
    message=f"Server disabled after {cb['failures']} failures",
    source="circuit_breaker"
)
```

### After (Unified)

```python
# New way - one call routes to all
from common.unified_tracking import track_mcp_event

track_mcp_event(
    event="mcp_server_disabled",
    message=f"MCP server '{server}' disabled after {cb['failures']} failures",
    server=server,
    severity=EventSeverity.HIGH,
    metadata={"failures": cb["failures"], "disabled_until": cb["disabled_until"]}
)
# Automatically:
# - Logs JSON event
# - Sends notification
# - Could record in observability (future enhancement)
```

### Before (Dashboard Error)

```python
# Old way - only dashboard tracker
tracker.record_error(
    error_type=DashboardErrorType.JAVASCRIPT_ERROR,
    error_message=error.message,
    component="model-services"
)
```

### After (Unified)

```python
# New way - routes to all systems
from common.unified_tracking import track_dashboard_event

track_dashboard_event(
    event="refresh_failed",
    message="Failed to refresh model services",
    error=error,
    component="model-services",
    severity=EventSeverity.MEDIUM
)
# Automatically:
# - Logs JSON event
# - Records in dashboard tracker
# - Sends notification if severity is HIGH/CRITICAL
```

## Benefits

1. **Single Source of Truth**: One call, all systems updated
2. **Consistency**: All events tracked the same way
3. **Visibility**: Events appear in all relevant systems
4. **Maintainability**: Change routing logic in one place
5. **Backward Compatible**: Old code still works

## Future Enhancements

1. **Async Support**: Make observability recording async
2. **Event Filtering**: Configurable routing rules
3. **Performance**: Batch events for high-volume scenarios
4. **Analytics**: Unified event analytics across all systems


