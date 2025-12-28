# Unified Notification System

The notification system is now **fully unified and available to all system components**.

## Access Methods

### 1. Global Singleton (Recommended)
```python
from agent_runner.notifications import get_notification_manager

notifier = get_notification_manager()
notifier.notify(
    level=NotificationLevel.CRITICAL,
    title="Error Title",
    message="Error message",
    category="health",
    source="component_name"
)
```

### 2. Convenience Functions (Easiest)
```python
from agent_runner.notifications import (
    notify_critical,
    notify_high,
    notify_health,
    notify_error,
    notify_info
)

# Critical issues
notify_critical("Database Down", "SurrealDB connection lost", source="memory")

# Health issues
notify_health("Gateway Timeout", "Router not responding", source="health_check")

# High priority
notify_high("Task Failed", "Backup task failed", source="backup_task")

# Errors
notify_error("MCP Error", "Server connection failed", source="mcp_client")

# Info
notify_info("Task Complete", "Backup completed successfully", source="backup_task")
```

## Integration Points

### ✅ Background Tasks (`background_tasks.py`)
- Task failures send notifications based on priority
- Critical tasks notify on every failure
- High-priority tasks notify on failures
- Auto-disable notifications when tasks exceed retry limits

### ✅ Health Monitoring (`health_monitor.py`)
- Gateway health check failures
- MCP server health issues (multiple or critical servers)
- Circuit breaker recovery status

### ✅ Main Agent Runner (`agent_runner.py`)
- Gateway timeout/errors in health checks
- Memory database health check failures
- Memory database query failures
- Critical MCP server timeouts/errors
- SurrealDB backup failures

### ✅ All Components Can Use It
Any component can import and use:
```python
# In any module
try:
    from agent_runner.notifications import notify_high
except ImportError:
    from notifications import notify_high  # Fallback for direct execution

# Use it anywhere
notify_high("My Component Error", "Something went wrong", source="my_component")
```

## Notification Levels

- **CRITICAL**: Must notify immediately (database down, critical backups failed)
- **HIGH**: Important issues (gateway down, high-priority task failures)
- **MEDIUM**: Normal errors (task failures, connection issues)
- **LOW**: Low priority (can batch)
- **INFO**: Informational only

## Categories

- `system`: General system notifications
- `task`: Background task related
- `health`: Health check related
- `error`: Error conditions
- `info`: Informational messages

## Channels

- **LOG**: Written to log files (automatic)
- **DASHBOARD**: Available via `/admin/notifications` API (automatic)
- **CONSOLE**: Console output (optional)
- **WEBHOOK**: HTTP webhook (configure via `set_webhook()`)

## API Endpoints

- `GET /admin/notifications` - Get notifications (with filters)
- `POST /admin/notifications/{id}/acknowledge` - Acknowledge a notification

## Usage Examples

### In Health Checks
```python
from agent_runner.notifications import notify_health

if not gateway_healthy:
    notify_health("Gateway Down", "Router not responding", source="health_monitor")
```

### In Task Failures
```python
from agent_runner.notifications import notify_critical

try:
    backup_database()
except Exception as e:
    notify_critical("Backup Failed", str(e), source="backup_task")
```

### In Error Handlers
```python
from agent_runner.notifications import notify_error

try:
    process_data()
except Exception as e:
    notify_error("Processing Error", str(e), source="data_processor")
```

## Benefits

1. **Unified**: Single system for all notifications
2. **Accessible**: Easy imports from any component
3. **Flexible**: Multiple priority levels and categories
4. **Persistent**: Notification history maintained
5. **Filterable**: Can filter by level, category, source
6. **Acknowledgment**: Notifications can be acknowledged
7. **Multi-channel**: Logs, dashboard, webhooks, console

## Future Enhancements

- Webhook implementation for external integrations
- Email notifications
- SMS notifications
- Notification rules and routing
- Notification aggregation and batching






