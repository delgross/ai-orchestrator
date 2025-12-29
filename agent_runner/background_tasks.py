"""
Background task manager and scheduler for agent-runner.

Provides:
- Periodic tasks (run every N seconds)
- Scheduled tasks (cron-like scheduling)
- One-time tasks (run once after delay)
- Health monitoring
- Cache management
"""

from __future__ import annotations

import asyncio
import time
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional
from enum import Enum

logger = logging.getLogger("agent_runner.background_tasks")


class TaskType(Enum):
    """Task execution type."""
    PERIODIC = "periodic"  # Run every N seconds
    SCHEDULED = "scheduled"  # Cron-like scheduling
    ONCE = "once"  # Run once after delay


class TaskPriority(Enum):
    """Task priority levels."""
    CRITICAL = "critical"  # Must run, notify on failure
    HIGH = "high"  # Important, should run
    MEDIUM = "medium"  # Normal priority
    LOW = "low"  # Low priority, can skip if busy
    BACKGROUND = "background"  # Best effort, don't care if skipped


@dataclass
class Task:
    """Background task definition."""
    name: str
    task_type: TaskType
    func: Callable
    interval: Optional[float] = None  # For periodic tasks (seconds)
    schedule: Optional[str] = None  # For scheduled tasks (cron-like: "HH:MM" or "*/N minutes")
    delay: Optional[float] = None  # For one-time tasks (seconds)
    enabled: bool = True
    idle_only: bool = False
    priority: TaskPriority = TaskPriority.MEDIUM
    estimated_duration: Optional[float] = None  # Estimated duration in seconds
    dependencies: List[str] = field(default_factory=list)  # Task names that must complete first
    description: str = ""  # Human-readable description
    max_retries: int = 3  # Maximum retry attempts on failure
    retry_delay: float = 60.0  # Seconds to wait before retry
    consecutive_failures: int = 0  # Track consecutive failures
    last_run: Optional[float] = None
    next_run: Optional[float] = None
    run_count: int = 0
    error_count: int = 0
    last_error: Optional[str] = None
    last_duration: Optional[float] = None  # Actual duration of last run
    running: bool = False  # Whether task is currently executing


class BackgroundTaskManager:
    """Manages background tasks and scheduling."""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.running = False
        self._task_handles: Dict[str, asyncio.Task] = {}
        self._idle_checker: Optional[Callable[[], bool]] = None
        self._notification_subscribed = False
    
    def set_idle_checker(self, checker: Callable[[], bool]) -> None:
        """Set the function to check if system is idle."""
        self._idle_checker = checker
    
    def _subscribe_to_notifications(self) -> None:
        """Subscribe to health notifications to react automatically."""
        if self._notification_subscribed:
            return
        
        from common.notifications import get_notification_manager, NotificationLevel
        
        notifier = get_notification_manager()
        
        # Subscribe to critical health notifications
        async def handle_health_notification(notification):
            """React to health notifications by pausing dependent tasks."""
            if notification.category == "health" and notification.level in (NotificationLevel.CRITICAL, NotificationLevel.HIGH):
                # If gateway is down, pause tasks that depend on it
                if "gateway" in notification.title.lower() or "gateway" in notification.message.lower():
                    logger.warning("Gateway health issue detected, pausing gateway-dependent tasks")
                    # Could disable tasks that require gateway here
                    # For now, just log - can be extended based on task dependencies
                
                # If memory is down, pause memory-dependent tasks
                if "memory" in notification.title.lower() or "database" in notification.title.lower():
                    logger.warning("Memory database issue detected, pausing memory-dependent tasks")
                    # Could disable tasks that require memory here
        
        notifier.subscribe(
            handle_health_notification,
            category="health",
            level=NotificationLevel.HIGH
        )
        
        self._notification_subscribed = True
        logger.info("Background task manager subscribed to health notifications")

    def register(
        self,
        name: str,
        func: Callable,
        interval: Optional[float] = None,
        schedule: Optional[str] = None,
        delay: Optional[float] = None,
        enabled: bool = True,
        idle_only: bool = False,
        priority: TaskPriority = TaskPriority.MEDIUM,
        estimated_duration: Optional[float] = None,
        dependencies: Optional[List[str]] = None,
        description: str = "",
        max_retries: int = 3,
        retry_delay: float = 60.0,
    ) -> None:
        """
        Register a background task.
        
        Args:
            name: Unique task name
            func: Async function to execute
            interval: For periodic tasks, seconds between runs
            schedule: For scheduled tasks, cron-like string (e.g., "14:30" or "*/15 minutes")
            delay: For one-time tasks, seconds to wait before running
            enabled: Whether task is enabled
            idle_only: Whether to only run when system is idle
            priority: Task priority (critical, high, medium, low, background)
            estimated_duration: Estimated duration in seconds
            dependencies: List of task names that must complete first
            description: Human-readable description
            max_retries: Maximum retry attempts on failure (default: 3)
            retry_delay: Seconds to wait before retry (default: 60)
        """
        if name in self.tasks:
            logger.warning(f"Task '{name}' already registered, overwriting")
        
        # Determine task type
        if interval is not None:
            task_type = TaskType.PERIODIC
        elif schedule is not None:
            task_type = TaskType.SCHEDULED
        elif delay is not None:
            task_type = TaskType.ONCE
        else:
            raise ValueError("Must specify interval, schedule, or delay")
        
        task = Task(
            name=name,
            task_type=task_type,
            func=func,
            interval=interval,
            schedule=schedule,
            delay=delay,
            enabled=enabled,
            idle_only=idle_only,
            priority=priority,
            estimated_duration=estimated_duration,
            dependencies=dependencies or [],
            description=description,
            max_retries=max_retries,
            retry_delay=retry_delay,
        )
        
        self.tasks[name] = task
        logger.info(
            f"Registered background task: {name} "
            f"({task_type.value}, priority={priority.value}, idle_only={idle_only})"
        )
    
    def unregister(self, name: str) -> None:
        """Unregister a task."""
        if name in self.tasks:
            del self.tasks[name]
        if name in self._task_handles:
            self._task_handles[name].cancel()
            del self._task_handles[name]
    
    def enable(self, name: str) -> None:
        """Enable a task."""
        if name in self.tasks:
            self.tasks[name].enabled = True
    
    def disable(self, name: str) -> None:
        """Disable a task."""
        if name in self.tasks:
            self.tasks[name].enabled = False
    
    def _parse_schedule(self, schedule: str) -> Optional[float]:
        """
        Parse schedule string and return seconds until next run.
        
        Supports:
        - "HH:MM" - Run at specific time daily
        - "*/N minutes" - Run every N minutes
        - "*/N hours" - Run every N hours
        """
        schedule = schedule.strip()
        
        # Time format: "14:30"
        if ":" in schedule and len(schedule.split(":")) == 2:
            try:
                hour, minute = map(int, schedule.split(":"))
                now = datetime.now()
                target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if target <= now:
                    target += timedelta(days=1)
                return (target - now).total_seconds()
            except ValueError:
                logger.warning(f"Invalid time format: {schedule}")
                return None
        
        # Interval format: "*/N minutes" or "*/N hours"
        if schedule.startswith("*/"):
            try:
                parts = schedule[2:].split()
                if len(parts) == 2:
                    value = int(parts[0])
                    unit = parts[1].lower()
                    if unit in ("minute", "minutes", "min", "mins"):
                        return value * 60
                    elif unit in ("hour", "hours", "hr", "hrs"):
                        return value * 3600
            except (ValueError, IndexError):
                logger.warning(f"Invalid interval format: {schedule}")
                return None
        
        logger.warning(f"Unsupported schedule format: {schedule}")
        return None
    
    def _calculate_next_run(self, task: Task) -> float:
        """Calculate next run time for a task."""
        now = time.time()
        
        if task.task_type == TaskType.PERIODIC:
            if task.last_run is None:
                return now + (task.interval or 0)
            return task.last_run + (task.interval or 0)
        
        elif task.task_type == TaskType.SCHEDULED:
            if task.schedule:
                seconds = self._parse_schedule(task.schedule)
                if seconds is not None:
                    return now + seconds
            return now + 3600  # Default to 1 hour if parsing fails
        
        elif task.task_type == TaskType.ONCE:
            if task.delay:
                return now + task.delay
            return now
        
        return now
    
    async def _run_task(self, task: Task) -> None:
        """Execute a single task."""
        if not task.enabled:
            return
        
        # Check dependencies
        for dep_name in task.dependencies:
            if dep_name in self.tasks:
                dep_task = self.tasks[dep_name]
                # Wait for dependency to complete if it's running
                if dep_task.last_run is None or dep_task.error_count > 0:
                    logger.debug(f"Task '{task.name}' waiting for dependency '{dep_name}'")
                    # Simple check - in production, might want more sophisticated dependency resolution
                    if dep_task.error_count > 0:
                        logger.warning(f"Task '{task.name}' dependency '{dep_name}' has errors")
        
        # Check idleness if required
        if task.idle_only and self._idle_checker and not self._idle_checker():
            # For background priority, silently skip; for others, log
            if task.priority == TaskPriority.BACKGROUND:
                return
            logger.debug(f"Skipping idle-only task '{task.name}': System not idle")
            return
        
        start_time = time.time()
        try:
            # Execute the function
            if asyncio.iscoroutinefunction(task.func):
                await task.func()
            else:
                # It might be a regular function OR a lambda returning a coroutine
                result = task.func()
                if asyncio.iscoroutine(result):
                    await result
            
            # Success - reset consecutive failures
            task.run_count += 1
            task.last_run = time.time()
            task.last_error = None
            task.consecutive_failures = 0
            elapsed = time.time() - start_time
            task.last_duration = elapsed
            logger.debug(f"Task '{task.name}' completed in {elapsed:.2f}s")
        
        except Exception as e:
            task.error_count += 1
            task.consecutive_failures += 1
            task.last_error = str(e)
            task.last_duration = time.time() - start_time
            
            # Determine if we should retry
            should_retry = (
                task.consecutive_failures <= task.max_retries and
                task.enabled and
                task.priority != TaskPriority.BACKGROUND  # Background tasks don't retry
            )
            
            if should_retry:
                # Schedule retry
                retry_time = time.time() + task.retry_delay
                logger.warning(
                    f"Task '{task.name}' failed (attempt {task.consecutive_failures}/{task.max_retries}), "
                    f"retrying in {task.retry_delay}s"
                )
                # For periodic tasks, adjust next_run to retry time
                if task.task_type == TaskType.PERIODIC:
                    task.next_run = retry_time
                # For scheduled tasks, we'll retry at the retry time
                elif task.task_type == TaskType.SCHEDULED:
                    task.next_run = retry_time
            else:
                # Max retries exceeded or background task - disable if too many failures
                if task.consecutive_failures > task.max_retries and task.priority != TaskPriority.CRITICAL:
                    logger.error(
                        f"Task '{task.name}' exceeded max retries ({task.max_retries}), "
                        f"disabling task"
                    )
                    task.enabled = False
                    # Send notification about disabling
                    from common.notifications import notify_high
                    
                    if notify_high:
                        try:
                            notify_high(
                                title=f"Task Disabled: {task.name}",
                                message=f"Task disabled after {task.consecutive_failures} consecutive failures",
                                source=task.name,
                                metadata={"error_count": task.error_count, "last_error": str(e), "category": "task"}
                            )
                        except Exception:
                            pass
            
            # Send notification based on priority
            from common.notifications import notify_critical, notify_high
            
            if notify_critical and notify_high:
                try:
                    if task.priority == TaskPriority.CRITICAL:
                        notify_critical(
                            title=f"Critical Task Failed: {task.name}",
                            message=f"{str(e)} (attempt {task.consecutive_failures}/{task.max_retries})",
                            source=task.name,
                            metadata={
                                "error_count": task.error_count,
                                "run_count": task.run_count,
                                "consecutive_failures": task.consecutive_failures,
                                "will_retry": should_retry,
                                "category": "task"
                            }
                        )
                    elif task.priority == TaskPriority.HIGH:
                        notify_high(
                            title=f"High Priority Task Failed: {task.name}",
                            message=f"{str(e)} (attempt {task.consecutive_failures}/{task.max_retries})",
                            source=task.name,
                            metadata={
                                "consecutive_failures": task.consecutive_failures,
                                "will_retry": should_retry,
                                "category": "task"
                            }
                        )
                except Exception:
                    pass  # Don't let notification errors break task execution
            
            logger.error(f"Task '{task.name}' failed: {e}", exc_info=True)
        finally:
            task.running = False
    
    async def _run_periodic_task(self, task: Task) -> None:
        """Run a periodic task in a loop."""
        # Wait for initial interval before first run (prevents immediate execution on startup)
        if task.interval:
            await asyncio.sleep(task.interval)
        
        while self.running and task.enabled:
            try:
                await self._run_task(task)
                await asyncio.sleep(task.interval or 60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Periodic task '{task.name}' loop error: {e}")
                await asyncio.sleep(task.interval or 60)
    
    async def _run_scheduled_task(self, task: Task) -> None:
        """Run a scheduled task."""
        while self.running and task.enabled:
            try:
                now = time.time()
                if task.next_run is None:
                    task.next_run = self._calculate_next_run(task)
                
                wait_time = task.next_run - now
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                
                if not self.running or not task.enabled:
                    break
                
                await self._run_task(task)
                task.next_run = self._calculate_next_run(task)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Scheduled task '{task.name}' loop error: {e}")
                task.next_run = time.time() + 3600  # Retry in 1 hour
    
    async def _run_once_task(self, task: Task) -> None:
        """Run a one-time task."""
        if task.delay:
            await asyncio.sleep(task.delay)
        
        if self.running and task.enabled:
            await self._run_task(task)
            # One-time tasks are automatically disabled after running
            task.enabled = False
    
    async def start(self) -> None:
        """Start all registered tasks."""
        if self.running:
            logger.warning("Background task manager already running")
            return
        
        self.running = True
        logger.info(f"Starting background task manager with {len(self.tasks)} tasks")
        
        # Subscribe to notifications for reactive behavior
        self._subscribe_to_notifications()
        
        for name, task in self.tasks.items():
            if not task.enabled:
                continue
            
            if task.task_type == TaskType.PERIODIC:
                handle = asyncio.create_task(self._run_periodic_task(task))
            elif task.task_type == TaskType.SCHEDULED:
                handle = asyncio.create_task(self._run_scheduled_task(task))
            elif task.task_type == TaskType.ONCE:
                handle = asyncio.create_task(self._run_once_task(task))
            else:
                continue
            
            self._task_handles[name] = handle
            logger.info(f"Started task: {name}")
    
    async def stop(self) -> None:
        """Stop all tasks."""
        if not self.running:
            return
        
        self.running = False
        logger.info("Stopping background task manager")
        
        for name, handle in self._task_handles.items():
            handle.cancel()
            try:
                await handle
            except asyncio.CancelledError:
                pass
        
        self._task_handles.clear()
    
    async def trigger_task(self, name: str) -> Dict[str, Any]:
        """Manually trigger a task to run immediately."""
        if name not in self.tasks:
            return {"ok": False, "error": f"Task '{name}' not found"}
        
        task = self.tasks[name]
        if task.running:
            return {"ok": False, "error": f"Task '{name}' is already running"}
        
        # Run task in background (don't wait for completion)
        asyncio.create_task(self._run_task(task))
        return {"ok": True, "message": f"Task '{name}' triggered"}
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all tasks."""
        now = time.time()
        return {
            "running": self.running,
            "tasks": {
                name: {
                    "type": task.task_type.value,
                    "priority": task.priority.value,
                    "enabled": task.enabled,
                    "running": task.running,  # Current execution status
                    "idle_only": task.idle_only,
                    "description": task.description,
                    "estimated_duration": task.estimated_duration,
                    "dependencies": task.dependencies,
                    "max_retries": task.max_retries,
                    "consecutive_failures": task.consecutive_failures,
                    "run_count": task.run_count,
                    "error_count": task.error_count,
                    "last_run": task.last_run,
                    "last_duration": task.last_duration,
                    "next_run": task.next_run,
                    "seconds_until_next": max(0, (task.next_run or 0) - now) if task.next_run else None,
                    "last_error": task.last_error,
                }
                for name, task in self.tasks.items()
            }
        }
    
    def get_upcoming_tasks(self, time_window: float) -> List[Dict[str, Any]]:
        """Get tasks scheduled to run within the given time window (seconds)."""
        now = time.time()
        upcoming = []
        
        for name, task in self.tasks.items():
            if not task.enabled:
                continue
            
            if task.next_run is None:
                task.next_run = self._calculate_next_run(task)
            
            seconds_until = task.next_run - now
            if 0 <= seconds_until <= time_window:
                upcoming.append({
                    "name": name,
                    "priority": task.priority.value,
                    "description": task.description,
                    "next_run": task.next_run,
                    "seconds_until": seconds_until,
                    "estimated_duration": task.estimated_duration,
                    "type": task.task_type.value,
                })
        
        # Sort by priority (critical first) then by time
        priority_order = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3,
            TaskPriority.BACKGROUND: 4,
        }
        upcoming.sort(key=lambda t: (priority_order.get(TaskPriority(t["priority"]), 99), t["seconds_until"]))
        
        return upcoming


# Global task manager instance
_task_manager: Optional[BackgroundTaskManager] = None


def get_task_manager() -> BackgroundTaskManager:
    """Get the global task manager instance."""
    global _task_manager
    if _task_manager is None:
        _task_manager = BackgroundTaskManager()
    return _task_manager


