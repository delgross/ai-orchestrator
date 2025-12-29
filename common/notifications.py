"""
Notification system for agent-runner.

Provides:
- Priority-based notifications
- Multiple notification channels (log, webhook, etc.)
- Notification history and filtering
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("agent_runner.notifications")


class NotificationLevel(Enum):
    """Notification priority levels."""
    CRITICAL = "critical"  # Must notify immediately
    HIGH = "high"  # Important, notify soon
    MEDIUM = "medium"  # Normal priority
    LOW = "low"  # Low priority, can batch
    INFO = "info"  # Informational only


class NotificationChannel(Enum):
    """Available notification channels."""
    LOG = "log"  # Log file
    CONSOLE = "console"  # Console output
    WEBHOOK = "webhook"  # HTTP webhook
    DASHBOARD = "dashboard"  # Dashboard UI
    COMPONENT = "component"  # Internal component callbacks


@dataclass
class Notification:
    """A notification message."""
    level: NotificationLevel
    title: str
    message: str
    category: str = "system"  # system, task, health, etc.
    source: Optional[str] = None  # Task name, component name, etc.
    timestamp: float = field(default_factory=time.time)
    channels: List[NotificationChannel] = field(default_factory=lambda: [NotificationChannel.LOG, NotificationChannel.DASHBOARD])
    metadata: Dict[str, Any] = field(default_factory=dict)
    acknowledged: bool = False
    acknowledged_at: Optional[float] = None


class NotificationManager:
    """Manages notifications and routing."""
    
    def __init__(self, max_history: int = 1000):
        self.notifications: List[Notification] = []
        self.max_history = max_history
        self.webhook_url: Optional[str] = None
        self.enabled_channels: List[NotificationChannel] = [
            NotificationChannel.LOG,
            NotificationChannel.DASHBOARD,
            NotificationChannel.COMPONENT,  # Enable component notifications by default
        ]
        # Component subscriptions: {category: [callbacks], level: [callbacks], source: [callbacks]}
        self._component_subscriptions: Dict[str, List[Callable[[Notification], None]]] = {}
        # All-component subscriptions (receive all notifications)
        self._all_component_subscriptions: List[Callable[[Notification], None]] = []
    
    def set_webhook(self, url: str) -> None:
        """Set webhook URL for notifications."""
        self.webhook_url = url
        if NotificationChannel.WEBHOOK not in self.enabled_channels:
            self.enabled_channels.append(NotificationChannel.WEBHOOK)
    
    def subscribe(
        self,
        callback: Callable[[Notification], None],
        category: Optional[str] = None,
        level: Optional[NotificationLevel] = None,
        source: Optional[str] = None,
        all_notifications: bool = False,
    ) -> None:
        """
        Subscribe a component to receive notifications.
        
        Args:
            callback: Async or sync function that receives Notification
            category: Only receive notifications of this category (e.g., "health", "task")
            level: Only receive notifications of this level or higher
            source: Only receive notifications from this source
            all_notifications: If True, receive all notifications regardless of filters
        """
        if all_notifications:
            self._all_component_subscriptions.append(callback)
        else:
            # Create subscription key
            filters = []
            if category:
                filters.append(f"category:{category}")
            if level:
                filters.append(f"level:{level.value}")
            if source:
                filters.append(f"source:{source}")
            
            key = "|".join(filters) if filters else "all"
            if key not in self._component_subscriptions:
                self._component_subscriptions[key] = []
            self._component_subscriptions[key].append(callback)
        
        logger.debug(f"Component subscribed to notifications: {key if not all_notifications else 'all'}")
    
    def unsubscribe(self, callback: Callable[[Notification], None]) -> None:
        """Unsubscribe a component from notifications."""
        # Remove from all subscriptions
        if callback in self._all_component_subscriptions:
            self._all_component_subscriptions.remove(callback)
        
        # Remove from filtered subscriptions
        for key, callbacks in list(self._component_subscriptions.items()):
            if callback in callbacks:
                callbacks.remove(callback)
                if not callbacks:
                    del self._component_subscriptions[key]
        
        logger.debug("Component unsubscribed from notifications")
    
    def _notify_components(self, notification: Notification) -> None:
        """Notify all subscribed components."""
        # Notify all-component subscribers
        for callback in self._all_component_subscriptions:
            try:
                if asyncio.iscoroutinefunction(callback):
                    # Schedule async callback (fire and forget)
                    asyncio.create_task(callback(notification))
                else:
                    # Call sync callback
                    callback(notification)
            except Exception as e:
                logger.error(f"Error in component notification callback: {e}", exc_info=True)
        
        # Notify filtered subscribers
        for key, callbacks in self._component_subscriptions.items():
            # Check if notification matches filter
            matches = True
            if "category:" in key:
                expected_category = key.split("category:")[1].split("|")[0]
                if notification.category != expected_category:
                    matches = False
            if matches and "level:" in key:
                expected_level_str = key.split("level:")[1].split("|")[0]
                try:
                    expected_level = NotificationLevel(expected_level_str)
                    # Only match if notification level is >= expected level
                    level_priority = {
                        NotificationLevel.CRITICAL: 0,
                        NotificationLevel.HIGH: 1,
                        NotificationLevel.MEDIUM: 2,
                        NotificationLevel.LOW: 3,
                        NotificationLevel.INFO: 4,
                    }
                    if level_priority.get(notification.level, 99) > level_priority.get(expected_level, 0):
                        matches = False
                except ValueError:
                    matches = False
            if matches and "source:" in key:
                expected_source = key.split("source:")[1].split("|")[0]
                if notification.source != expected_source:
                    matches = False
            
            if matches:
                for callback in callbacks:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            asyncio.create_task(callback(notification))
                        else:
                            callback(notification)
                    except Exception as e:
                        logger.error(f"Error in component notification callback: {e}", exc_info=True)
    
    def notify(
        self,
        level: NotificationLevel,
        title: str,
        message: str,
        category: str = "system",
        source: Optional[str] = None,
        channels: Optional[List[NotificationChannel]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Notification:
        """Create and send a notification."""
        notification = Notification(
            level=level,
            title=title,
            message=message,
            category=category,
            source=source,
            channels=channels or self.enabled_channels.copy(),
            metadata=metadata or {},
        )
        
        # Send to enabled channels
        for channel in notification.channels:
            if channel in self.enabled_channels:
                self._send_to_channel(notification, channel)
        
        # Notify subscribed components (always, regardless of channels)
        if NotificationChannel.COMPONENT in self.enabled_channels:
            self._notify_components(notification)
        
        # Store in history
        self.notifications.append(notification)
        
        # Trim history if needed
        if len(self.notifications) > self.max_history:
            self.notifications = self.notifications[-self.max_history:]
        
        return notification
    
    def _send_to_channel(self, notification: Notification, channel: NotificationChannel) -> None:
        """Send notification to a specific channel."""
        if channel == NotificationChannel.LOG:
            log_level = {
                NotificationLevel.CRITICAL: logging.CRITICAL,
                NotificationLevel.HIGH: logging.ERROR,
                NotificationLevel.MEDIUM: logging.WARNING,
                NotificationLevel.LOW: logging.INFO,
                NotificationLevel.INFO: logging.INFO,
            }.get(notification.level, logging.INFO)
            
            logger.log(
                log_level,
                f"[{notification.category}] {notification.title}: {notification.message}",
                extra={"source": notification.source, "metadata": notification.metadata}
            )
        
        elif channel == NotificationChannel.CONSOLE:
            print(f"[{notification.level.value.upper()}] {notification.title}: {notification.message}")
        
        elif channel == NotificationChannel.WEBHOOK and self.webhook_url:
            # TODO: Implement webhook sending (future enhancement)
            # Would send HTTP POST to self.webhook_url with notification payload
            pass
        
        elif channel == NotificationChannel.DASHBOARD:
            # Dashboard notifications are stored and retrieved via API
            pass
        
        elif channel == NotificationChannel.COMPONENT:
            # Component notifications are handled by _notify_components
            pass
    
    def get_notifications(
        self,
        level: Optional[NotificationLevel] = None,
        category: Optional[str] = None,
        unacknowledged_only: bool = False,
        limit: int = 100,
    ) -> List[Notification]:
        """Get notifications with filters."""
        filtered = self.notifications
        
        if level:
            filtered = [n for n in filtered if n.level == level]
        
        if category:
            filtered = [n for n in filtered if n.category == category]
        
        if unacknowledged_only:
            filtered = [n for n in filtered if not n.acknowledged]
        
        # Sort by timestamp (newest first)
        filtered.sort(key=lambda n: n.timestamp, reverse=True)
        
        return filtered[:limit]
    
    def acknowledge(self, notification_id: Optional[int] = None, source: Optional[str] = None) -> bool:
        """Acknowledge a notification."""
        if notification_id is not None and 0 <= notification_id < len(self.notifications):
            self.notifications[notification_id].acknowledged = True
            self.notifications[notification_id].acknowledged_at = time.time()
            return True
        
        if source:
            for notification in self.notifications:
                if notification.source == source and not notification.acknowledged:
                    notification.acknowledged = True
                    notification.acknowledged_at = time.time()
                    return True
        
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get notification statistics."""
        total = len(self.notifications)
        unacknowledged = sum(1 for n in self.notifications if not n.acknowledged)
        
        by_level: Dict[str, int] = {}
        for level in NotificationLevel:
            by_level[level.value] = sum(1 for n in self.notifications if n.level == level)
        
        by_category: Dict[str, int] = {}
        for notification in self.notifications:
            cat = notification.category
            by_category[cat] = by_category.get(cat, 0) + 1
        
        return {
            "total": total,
            "unacknowledged": unacknowledged,
            "by_level": by_level,
            "by_category": by_category,
        }


# Global notification manager instance
_notification_manager: Optional[NotificationManager] = None


def get_notification_manager() -> NotificationManager:
    """Get the global notification manager instance."""
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = NotificationManager()
    return _notification_manager


# Convenience functions for common notification patterns
def notify_critical(title: str, message: str, source: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Notification:
    """Send a critical notification."""
    return get_notification_manager().notify(
        level=NotificationLevel.CRITICAL,
        title=title,
        message=message,
        category="system",
        source=source,
        metadata=metadata or {}
    )


def notify_high(title: str, message: str, source: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Notification:
    """Send a high-priority notification."""
    return get_notification_manager().notify(
        level=NotificationLevel.HIGH,
        title=title,
        message=message,
        category="system",
        source=source,
        metadata=metadata or {}
    )


def notify_health(title: str, message: str, source: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Notification:
    """Send a health-related notification."""
    return get_notification_manager().notify(
        level=NotificationLevel.HIGH,
        title=title,
        message=message,
        category="health",
        source=source,
        metadata=metadata or {}
    )


def notify_error(title: str, message: str, source: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Notification:
    """Send an error notification (medium priority)."""
    return get_notification_manager().notify(
        level=NotificationLevel.MEDIUM,
        title=title,
        message=message,
        category="error",
        source=source,
        metadata=metadata or {}
    )


def notify_info(title: str, message: str, source: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Notification:
    """Send an informational notification."""
    return get_notification_manager().notify(
        level=NotificationLevel.INFO,
        title=title,
        message=message,
        category="info",
        source=source,
        metadata=metadata or {}
    )

