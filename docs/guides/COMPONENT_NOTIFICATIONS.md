# Component-to-Component Notifications

The notification system now supports **component-to-component notifications**, allowing components to subscribe to and react to events from other components.

## Why This Is Useful

### 1. **Event-Driven Architecture**
Components can react to events without tight coupling:
- Gateway goes down → Scheduler pauses gateway-dependent tasks
- Memory database fails → Backup system triggers immediate backup
- Health check fails → Components take automatic recovery actions

### 2. **Automatic Reactions**
Components can automatically respond to issues:
- Critical task fails → Other components can take corrective action
- Health degradation → Components can reduce load or switch to backup modes
- Resource exhaustion → Components can pause non-critical operations

### 3. **Decoupling**
Components don't need to know about each other directly:
- Health monitor doesn't need to import scheduler
- Tasks don't need to know about health checks
- All communication goes through the notification system

## How It Works

### Subscription System

Components can subscribe to notifications with filters:

```python
from agent_runner.notifications import get_notification_manager, NotificationLevel

notifier = get_notification_manager()

# Subscribe to all health notifications
async def handle_health_issue(notification):
    if "gateway" in notification.title.lower():
        # React to gateway issues
        pause_gateway_dependent_tasks()

notifier.subscribe(
    handle_health_issue,
    category="health",
    level=NotificationLevel.HIGH  # Only high/critical
)
```

### Subscription Filters

1. **By Category**: `category="health"`, `category="task"`, etc.
2. **By Level**: `level=NotificationLevel.CRITICAL` (receives that level and higher)
3. **By Source**: `source="health_monitor"`, `source="backup_task"`, etc.
4. **All Notifications**: `all_notifications=True`

### Callback Types

Both sync and async callbacks are supported:

```python
# Async callback (recommended)
async def handle_notification(notification):
    await react_to_notification(notification)

notifier.subscribe(handle_notification, category="health")

# Sync callback
def handle_notification(notification):
    react_to_notification(notification)

notifier.subscribe(handle_notification, category="health")
```

## Real-World Examples

### Example 1: Scheduler Reacts to Health Issues

```python
# In background_tasks.py
async def handle_health_notification(notification):
    """Pause tasks when critical components are down."""
    if notification.category == "health":
        if "gateway" in notification.title.lower():
            # Disable tasks that require gateway
            disable_tasks_requiring_gateway()
        elif "memory" in notification.title.lower():
            # Disable tasks that require memory
            disable_tasks_requiring_memory()

notifier.subscribe(handle_health_notification, category="health", level=NotificationLevel.HIGH)
```

### Example 2: Backup System Reacts to Memory Issues

```python
# In backup component
async def handle_memory_issue(notification):
    """Trigger immediate backup when memory issues detected."""
    if "memory" in notification.title.lower() or "database" in notification.title.lower():
        logger.warning("Memory issue detected, triggering emergency backup")
        await trigger_emergency_backup()

notifier.subscribe(handle_memory_issue, category="health", level=NotificationLevel.CRITICAL)
```

### Example 3: Component Monitors All Critical Issues

```python
# Monitor all critical issues
async def handle_critical_issue(notification):
    """Log and escalate all critical issues."""
    logger.critical(f"CRITICAL: {notification.title} - {notification.message}")
    await escalate_to_admin(notification)

notifier.subscribe(handle_critical_issue, level=NotificationLevel.CRITICAL)
```

### Example 4: Task-Specific Reactions

```python
# React to specific task failures
async def handle_backup_failure(notification):
    """When backup fails, notify and retry."""
    if notification.source == "surreal_backup":
        logger.error("Backup failed, scheduling retry")
        await schedule_backup_retry()

notifier.subscribe(handle_backup_failure, category="task", source="surreal_backup")
```

## Current Integrations

### ✅ Background Task Manager
- Subscribes to health notifications
- Can pause tasks when dependencies fail
- Reacts to gateway and memory issues

### 🔄 Extensible
Any component can subscribe:
- Health monitor can subscribe to task failures
- Memory system can subscribe to health checks
- Scheduler can subscribe to resource issues
- Custom components can subscribe to any events

## Benefits

1. **Reactive**: Components automatically respond to issues
2. **Decoupled**: Components don't need direct dependencies
3. **Flexible**: Filter by category, level, or source
4. **Scalable**: Easy to add new subscribers
5. **Reliable**: Callbacks are fire-and-forget with error handling

## API

```python
# Subscribe
notifier.subscribe(
    callback: Callable[[Notification], None],
    category: Optional[str] = None,
    level: Optional[NotificationLevel] = None,
    source: Optional[str] = None,
    all_notifications: bool = False,
)

# Unsubscribe
notifier.unsubscribe(callback)
```

## Best Practices

1. **Use async callbacks** for I/O operations
2. **Filter appropriately** to avoid unnecessary callbacks
3. **Handle errors** in callbacks (they're already wrapped, but be defensive)
4. **Unsubscribe** when components shut down
5. **Document** what your component subscribes to and why

## Future Enhancements

- Priority-based callback execution
- Callback retry logic
- Callback timeout handling
- Subscription statistics
- Callback chains and pipelines






