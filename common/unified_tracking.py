"""
Unified Event Tracking System

Provides a single entry point for all tracking systems:
- Observability system (request lifecycle, performance metrics)
- Notification system (alerts and notifications)
- JSON event logging (structured log events)
- System blog (human-readable event logs)
- Dashboard tracker (dashboard-specific errors)

This unifies the previously siloed tracking systems.
"""

from __future__ import annotations

import logging
import time
from enum import Enum
from typing import Any, Dict, Optional

logger = logging.getLogger("unified_tracking")


class EventSeverity(Enum):
    """Event severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"
    DEBUG = "debug"


class EventCategory(Enum):
    """Event categories for routing."""
    ERROR = "error"
    HEALTH = "health"
    PERFORMANCE = "performance"
    SECURITY = "security"
    CONFIG = "config"
    TASK = "task"
    MCP = "mcp"
    DASHBOARD = "dashboard"
    SYSTEM = "system"
    ANOMALY = "anomaly"


class UnifiedTracker:
    """
    Unified tracking system that routes events to all appropriate subsystems.
    
    Usage:
        from common.unified_tracking import track_event
        
        track_event(
            event="mcp_server_failed",
            severity=EventSeverity.HIGH,
            category=EventCategory.MCP,
            message="MCP server 'memory' failed to respond",
            metadata={"server": "memory", "error": "timeout"},
            request_id="abc123"
        )
    """
    
    def __init__(self):
        self._observability = None
        self._notification_manager = None
        self._dashboard_tracker = None
        self._system_blog = None
        self._json_logger = None
        
        # Lazy initialization to avoid circular imports
        self._initialized = False
    
    def _ensure_initialized(self):
        """Lazy initialization of subsystems."""
        if self._initialized:
            return
        
        try:
            # Observability system
            try:
                from common.observability import get_observability
                self._observability = get_observability()
            except (ImportError, Exception) as e:
                logger.debug(f"Observability system not available: {e}")
            
            # Notification system
            try:
                from common.notifications import get_notification_manager, NotificationLevel
                self._notification_manager = get_notification_manager()
                # Map our severity to notification levels
                self._severity_to_notification = {
                    EventSeverity.CRITICAL: NotificationLevel.CRITICAL,
                    EventSeverity.HIGH: NotificationLevel.HIGH,
                    EventSeverity.MEDIUM: NotificationLevel.MEDIUM,
                    EventSeverity.LOW: NotificationLevel.LOW,
                    EventSeverity.INFO: NotificationLevel.INFO,
                }
            except (ImportError, Exception) as e:
                logger.debug(f"Notification system not available: {e}")
            
            # Dashboard tracker
            try:
                from agent_runner.dashboard_tracker import get_dashboard_tracker, DashboardErrorType
                self._dashboard_tracker = get_dashboard_tracker()
                # Map categories to dashboard error types
                self._category_to_dashboard_type = {
                    EventCategory.ERROR: DashboardErrorType.JAVASCRIPT_ERROR,
                    EventCategory.HEALTH: DashboardErrorType.API_ERROR,
                    EventCategory.MCP: DashboardErrorType.API_ERROR,
                    EventCategory.DASHBOARD: DashboardErrorType.RENDERING_ERROR,
                }
            except (ImportError, Exception) as e:
                logger.debug(f"Dashboard tracker not available: {e}")
            
            # System blog
            try:
                from common.system_blog import get_blog, BlogCategory, BlogSeverity
                self._system_blog = get_blog()
                self._blog_category_map = {
                    EventCategory.ANOMALY: BlogCategory.ANOMALY,
                    EventCategory.SYSTEM: BlogCategory.SYSTEM_EVENT,
                    EventCategory.CONFIG: BlogCategory.CONFIG_CHANGE,
                    EventCategory.ERROR: BlogCategory.SYSTEM_EVENT,
                }
                self._blog_severity_map = {
                    EventSeverity.CRITICAL: BlogSeverity.CRITICAL,
                    EventSeverity.HIGH: BlogSeverity.WARNING,
                    EventSeverity.MEDIUM: BlogSeverity.INFO,
                    EventSeverity.LOW: BlogSeverity.INFO,
                    EventSeverity.INFO: BlogSeverity.INFO,
                }
            except (ImportError, Exception) as e:
                logger.debug(f"System blog not available: {e}")
            
            # JSON event logger
            try:
                from common.logging_utils import log_json_event
                self._json_logger = log_json_event
            except (ImportError, Exception) as e:
                logger.debug(f"JSON logger not available: {e}")
            
            self._initialized = True
        except Exception as e:
            logger.warning(f"Failed to initialize unified tracker subsystems: {e}")
            self._initialized = True  # Mark as initialized to avoid retry loops
    
    def verify_channels(self) -> Dict[str, Any]:
        """Verify the health of all tracking subsystems."""
        self._ensure_initialized()
        status = {
            "observability": False,
            "notifications": False,
            "dashboard": False,
            "blog": False,
            "json_logger": False
        }
        
        if self._observability:
            status["observability"] = True # Basic existence check
            
        if self._notification_manager:
             status["notifications"] = True
             
        if self._dashboard_tracker:
             status["dashboard"] = True
             
        if self._system_blog:
             status["blog"] = True
        
        if self._json_logger:
             status["json_logger"] = True
             
        # Aggregate
        status["healthy"] = all(status.values())
        return status

    
    def track_event(
        self,
        event: str,
        severity: EventSeverity = EventSeverity.INFO,
        category: EventCategory = EventCategory.SYSTEM,
        message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        component: Optional[str] = None,
        error: Optional[Exception] = None,
        write_to_blog: bool = False,
        notify: Optional[bool] = None,  # None = auto-determine based on severity
    ) -> None:
        """
        Track an event across all appropriate subsystems.
        
        Args:
            event: Event name/type (e.g., "mcp_server_failed")
            severity: Event severity level
            category: Event category for routing
            message: Human-readable message
            metadata: Additional context data
            request_id: Request ID for correlation
            component: Component name (e.g., "mcp", "dashboard", "health_monitor")
            error: Exception object if this is an error event
            write_to_blog: Force write to system blog (default: only for CRITICAL/HIGH)
            notify: Force notification (default: auto for CRITICAL/HIGH)
        """
        self._ensure_initialized()
        
        metadata = metadata or {}
        if error:
            metadata["error_type"] = type(error).__name__
            metadata["error_message"] = str(error)
            if hasattr(error, "__traceback__"):
                import traceback
                metadata["error_traceback"] = traceback.format_exc()
        
        # Auto-determine notification based on severity
        if notify is None:
            notify = severity in (EventSeverity.CRITICAL, EventSeverity.HIGH)
        
        # Auto-determine blog write based on severity
        if not write_to_blog:
            write_to_blog = severity in (EventSeverity.CRITICAL, EventSeverity.HIGH)
        
        # 1. JSON Event Logging (always, for log parsing)
        if self._json_logger:
            try:
                json_payload = {
                    "event": event,
                    "severity": severity.value,
                    "category": category.value,
                    **(metadata or {})
                }
                if message:
                    json_payload["message"] = message
                if component:
                    json_payload["component"] = component
                self._json_logger(event, request_id=request_id, **json_payload)
            except Exception as e:
                logger.debug(f"Failed to log JSON event: {e}")
        
        # 2. Observability System (for performance/request tracking)
        if self._observability:
            try:
                import asyncio
                from common.observability import ComponentType
                
                # Record component health for HEALTH/MCP/ERROR events
                if category in (EventCategory.HEALTH, EventCategory.MCP, EventCategory.ERROR):
                    # Map component to ComponentType
                    component_type_map = {
                        "mcp": ComponentType.MCP_SERVER,
                        "health_monitor": ComponentType.AGENT_RUNNER,
                        "dashboard": ComponentType.AGENT_RUNNER,
                        "circuit_breaker": ComponentType.MCP_SERVER,
                    }
                    comp_type = component_type_map.get(component or "", ComponentType.AGENT_RUNNER)
                    # For MCP events, use server name from metadata if available
                    if category == EventCategory.MCP and metadata and "server" in metadata:
                        comp_id = metadata["server"]
                    else:
                        comp_id = component or "unknown"
                    
                    # Determine health status from severity
                    if severity in (EventSeverity.CRITICAL, EventSeverity.HIGH):
                        status = "unhealthy"
                    elif severity == EventSeverity.MEDIUM:
                        status = "degraded"
                    else:
                        status = "healthy"
                    
                    # Call async function using asyncio.create_task (fire-and-forget)
                    # This matches the pattern used in observability_middleware.py
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            # Event loop is running, use create_task
                            asyncio.create_task(
                                self._observability.record_component_health(
                                    comp_type,
                                    comp_id,
                                    status,
                                    metadata={
                                        "event": event,
                                        "severity": severity.value,
                                        "message": message,
                                        **metadata
                                    }
                                )
                            )
                        else:
                            # No event loop, run in new one
                            asyncio.run(
                                self._observability.record_component_health(
                                    comp_type,
                                    comp_id,
                                    status,
                                    metadata={
                                        "event": event,
                                        "severity": severity.value,
                                        "message": message,
                                        **metadata
                                    }
                                )
                            )
                    except RuntimeError:
                        # No event loop available, skip observability
                        logger.debug(f"No event loop available for observability recording: {event}")
                
                # Record error in observability if it's an error event
                if category == EventCategory.ERROR and request_id:
                    # Try to add error to existing request lifecycle
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            asyncio.create_task(self._record_error_in_observability(request_id, error, metadata))
                    except RuntimeError:
                        logger.debug(f"No event loop available for error recording: {event}")
            except Exception as e:
                logger.debug(f"Failed to record in observability: {e}")

        # 3. Notification System (for alerts)
        if notify and self._notification_manager:
            try:
                notification_level = self._severity_to_notification.get(severity)
                if not notification_level:
                    from common.notifications import NotificationLevel
                    notification_level = NotificationLevel.INFO
                if notification_level:
                    title = message or event.replace("_", " ").title()
                    self._notification_manager.notify(
                        level=notification_level,
                        title=title,
                        message=message or f"Event: {event}",
                        category=category.value,
                        source=component or "unified_tracker",
                        metadata=metadata
                    )
            except Exception as e:
                logger.debug(f"Failed to send notification: {e}")
        
        # 4. Dashboard Tracker (for dashboard-specific errors)
        if category == EventCategory.DASHBOARD and self._dashboard_tracker:
            try:
                dashboard_type = self._category_to_dashboard_type.get(category)
                if not dashboard_type:
                    from agent_runner.dashboard_tracker import DashboardErrorType
                    dashboard_type = DashboardErrorType.UNKNOWN
                if dashboard_type:
                    self._dashboard_tracker.record_error(
                        error_type=dashboard_type,
                        error_message=message or str(error) if error else event,
                        error_stack=metadata.get("error_traceback") if metadata else None,
                        component=component,
                        context=metadata,
                        request_id=request_id
                    )
            except Exception as e:
                logger.debug(f"Failed to record in dashboard tracker: {e}")
        
        # 5. System Blog (for important events)
        if write_to_blog and self._system_blog:
            try:
                from common.system_blog import BlogCategory, BlogSeverity
                blog_category = self._blog_category_map.get(category, BlogCategory.SYSTEM_EVENT)
                blog_severity = self._blog_severity_map.get(severity, BlogSeverity.INFO)
                
                # Create blog entry
                from common.system_blog import BlogEntry
                blog_entry = BlogEntry(
                    timestamp=time.time(),
                    category=blog_category,
                    severity=blog_severity,
                    title=message or event.replace("_", " ").title(),
                    source=component or "unified_tracker",
                    content=f"Event: {event}\n\n{message or ''}\n\nMetadata: {metadata}",
                    metadata=metadata
                )
                self._system_blog.write_entry(blog_entry)
            except Exception as e:
                logger.debug(f"Failed to write to system blog: {e}")

    async def _record_error_in_observability(self, request_id: str, error: Optional[Exception], metadata: Dict[str, Any]):
        """Helper to record error in observability system."""
        try:
            lifecycle = await self._observability.get_request(request_id)
            if lifecycle and error:
                lifecycle.add_error(error, metadata)
        except Exception as e:
            logger.debug(f"Failed to record error in observability: {e}")


# Global singleton instance
_tracker: Optional[UnifiedTracker] = None


def get_unified_tracker() -> UnifiedTracker:
    """Get the global unified tracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = UnifiedTracker()
    return _tracker


def track_event(
    event: str,
    severity: EventSeverity = EventSeverity.INFO,
    category: EventCategory = EventCategory.SYSTEM,
    message: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
    component: Optional[str] = None,
    error: Optional[Exception] = None,
    write_to_blog: bool = False,
    notify: Optional[bool] = None,
) -> None:
    """
    Convenience function to track an event.
    
    Example:
        track_event(
            "mcp_server_failed",
            severity=EventSeverity.HIGH,
            category=EventCategory.MCP,
            message="Memory server failed",
            metadata={"server": "memory"},
            component="mcp_client"
        )
    """
    tracker = get_unified_tracker()
    tracker.track_event(
        event=event,
        severity=severity,
        category=category,
        message=message,
        metadata=metadata,
        request_id=request_id,
        component=component,
        error=error,
        write_to_blog=write_to_blog,
        notify=notify,
    )


# Convenience functions for common patterns
def track_error(
    event: str,
    message: str,
    error: Optional[Exception] = None,
    severity: EventSeverity = EventSeverity.HIGH,
    component: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
) -> None:
    """Track an error event."""
    track_event(
        event=event,
        severity=severity,
        category=EventCategory.ERROR,
        message=message,
        error=error,
        component=component,
        metadata=metadata,
        request_id=request_id,
        notify=True,  # Errors should notify
    )


def track_health_event(
    event: str,
    message: str,
    severity: EventSeverity = EventSeverity.MEDIUM,
    component: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """Track a health-related event."""
    track_event(
        event=event,
        severity=severity,
        category=EventCategory.HEALTH,
        message=message,
        component=component,
        metadata=metadata,
        notify=severity in (EventSeverity.CRITICAL, EventSeverity.HIGH),
    )


def track_mcp_event(
    event: str,
    message: str,
    server: str,
    severity: EventSeverity = EventSeverity.MEDIUM,
    error: Optional[Exception] = None,
    metadata: Optional[Dict[str, Any]] = None,
    component: Optional[str] = None,
) -> None:
    """Track an MCP server event."""
    metadata = metadata or {}
    metadata["server"] = server
    track_event(
        event=event,
        severity=severity,
        category=EventCategory.MCP,
        message=message,
        error=error,
        component=component or "mcp_client",
        metadata=metadata,
        notify=severity in (EventSeverity.CRITICAL, EventSeverity.HIGH),
    )


def track_dashboard_event(
    event: str,
    message: str,
    severity: EventSeverity = EventSeverity.MEDIUM,
    error: Optional[Exception] = None,
    component: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
) -> None:
    """Track a dashboard event."""
    track_event(
        event=event,
        severity=severity,
        category=EventCategory.DASHBOARD,
        message=message,
        error=error,
        component=component,
        metadata=metadata,
        request_id=request_id,
        notify=severity in (EventSeverity.CRITICAL, EventSeverity.HIGH),
    )

