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
    MONITOR = "monitor"  # Health monitoring tasks


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
    func: Callable[..., Any]
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
    last_duration: Optional[float] = None  # Actual duration of last run
    running: bool = False  # Whether task is currently executing
    min_tempo: Optional[Any] = None # Minimum Tempo required to run (e.g. Tempo.REFLECTIVE)
    time_of_day: Optional[str] = None  # Time-of-day requirement: "NIGHT" or None


class BackgroundTaskManager:
    """Manages background tasks and scheduling."""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.running = False
        self._task_handles: Dict[str, asyncio.Task] = {}
        self._idle_checker: Optional[Callable[[], bool]] = None
        self._idle_checker: Optional[Callable[[], bool]] = None
        self._notification_subscribed = False
        
        # GLOBAL CIRCUIT BREAKER
        # If we have too many total failures across ALL tasks in a short window, pause everything.
        self._global_error_history: List[float] = [] # Timestamps of errors
        self._global_cb_tripped = False
        self._global_cb_reset_time = 0.0
    
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
        min_tempo: Optional[Any] = None,
        time_of_day: Optional[str] = None,
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
            idle_only: Whether to only run when system is idle (Deprecated: use min_tempo)
            priority: Task priority (critical, high, medium, low, background)
            min_tempo: Minimum Tempo required (default: None)
            time_of_day: Time-of-day requirement: "NIGHT" or None (default: None)
            estimated_duration: Estimated duration in seconds
            dependencies: List of task names that must complete first
            description: Human-readable description
            max_retries: Maximum retry attempts on failure (default: 3)
            retry_delay: Seconds to wait before retry (default: 60)
        """
        if name in self.tasks:
            # Benign overwrite in development/restart
            logger.debug(f"Task '{name}' already registered, overwriting")
        
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
            min_tempo=min_tempo,
            time_of_day=time_of_day,
        )
        # Apply extra kwargs if we didn't add to init yet (safe approach) or update object
        # Actually better to just update the object after init since we don't want to break signature of register unless we fully updated it
        # But we can update signature of register above, let's just do it cleanly.
        
        self.tasks[name] = task
        tt_val = task_type.value if hasattr(task_type, "value") else str(task_type)
        p_val = priority.value if hasattr(priority, "value") else str(priority)
        logger.info(
            f"Registered background task: {name} "
            f"({tt_val}, priority={p_val}, idle_only={idle_only})"
        )
        
        # If manager is already running, start the task immediately
        if self.running and task.enabled:
            self._start_task_wrapper(name, task)
            logger.info(f"Started task immediately: {name}")

    def _start_task_wrapper(self, name: str, task: Task) -> None:
        """Helper to start the appropriate loop for a task type."""
        if name in self._task_handles:
             # Already running (or at least handle exists)
             return

        if task.task_type == TaskType.PERIODIC:
            handle = asyncio.create_task(self._run_periodic_task(task))
        elif task.task_type == TaskType.SCHEDULED:
            handle = asyncio.create_task(self._run_scheduled_task(task))
        elif task.task_type == TaskType.ONCE:
            handle = asyncio.create_task(self._run_once_task(task))
        else:
            return
        
        self._task_handles[name] = handle
    
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
        
        # Raw seconds format: "300"
        if isinstance(schedule, int):
            return schedule
        if isinstance(schedule, str) and schedule.isdigit():
            return int(schedule)
        
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

        # GLOBAL CIRCUIT BREAKER CHECK
        if self._global_cb_tripped:
            if time.time() > self._global_cb_reset_time:
                logger.info("Global Circuit Breaker RESET. Resuming tasks.")
                self._global_cb_tripped = False
                self._global_error_history.clear()
            else:
                return # Silently skip execution while system is cooling down
        
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
        
        # Check idleness if required (Legacy)
        if task.idle_only and self._idle_checker and not self._idle_checker():
            if task.priority == TaskPriority.BACKGROUND:
                return
            logger.debug(f"Skipping idle-only task '{task.name}': System not idle")
            return

        # Check Tempo (Idle-based requirement)
        if task.min_tempo:
            from agent_runner.agent_runner import get_shared_state
            state = get_shared_state()
            current_tempo = await state.get_current_tempo()
            
            tempo_values = {
                "FOCUSED": 0,
                "ALERT": 1,
                "REFLECTIVE": 2,
                "DEEP": 3
            }
            
            # Handle if min_tempo is string or enum
            req_val = -1
            if hasattr(task.min_tempo, "name"):
                req_val = tempo_values.get(task.min_tempo.name, 99)
            elif isinstance(task.min_tempo, str):
                req_val = tempo_values.get(task.min_tempo, 99)
            
            cur_val = tempo_values.get(current_tempo.name, 0)
            
            if cur_val < req_val:
                # System is too busy for this task
                if task.priority != TaskPriority.BACKGROUND:
                     logger.debug(f"Skipping task '{task.name}': Current Tempo {current_tempo.name} < Min Tempo {task.min_tempo}")
                return
        
        # Check time of day (e.g., NIGHT)
        if task.time_of_day:
            from agent_runner.agent_runner import get_shared_state
            state = get_shared_state()
            
            if task.time_of_day == "NIGHT":
                if not state.is_nighttime():
                    if task.priority != TaskPriority.BACKGROUND:
                        logger.debug(f"Skipping task '{task.name}': Not nighttime")
                    return
            # Can add more time_of_day options here (e.g., "DAY", "MORNING", etc.)
        
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
                # Schedule retry with deterministic jitter (based on task name and attempt)
                import random
                # We use a seed based on name to be somewhat stable but still jittered
                random.seed(f"{task.name}_{task.consecutive_failures}")
                jitter = random.uniform(0.8, 1.2)
                actual_delay = task.retry_delay * jitter
                
                retry_time = time.time() + actual_delay
                logger.warning(
                    f"Task '{task.name}' failed (attempt {task.consecutive_failures}/{task.max_retries}), "
                    f"retrying in {actual_delay:.1f}s (jittered from {task.retry_delay}s)"
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
                    
                    if notify_high is not None:
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
            
            if notify_critical is not None and notify_high is not None:
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
                except Exception as notify_err:
                    logger.warning(f"Failed to send task failure notification: {notify_err}", exc_info=True)
                    # Don't let notification errors break task execution, but log them
            
            logger.error(f"Task '{task.name}' failed: {e}", exc_info=True)
            
            # Update Global Circuit Breaker
            now = time.time()
            self._global_error_history.append(now)
            # clean old errors (> 5 mins ago)
            self._global_error_history = [t for t in self._global_error_history if now - t < 300]
            
            # Trip if > 10 errors in 5 minutes
            if len(self._global_error_history) > 10 and not self._global_cb_tripped:
                self._global_cb_tripped = True
                self._global_cb_reset_time = now + 600 # 10 minute cooldown
                logger.critical("GLOBAL CIRCUIT BREAKER TRIPPED: >10 Task Failures in 5 mins. Pausing Scheduler.")
                
                from common.notifications import notify_critical
                notify_critical(
                    title="SYSTEM PAUSED (Circuit Breaker)",
                    message="The Task Scheduler has paused for 10 minutes due to excessive task failures (>10 in 5m).",
                    source="BackgroundTaskManager"
                )
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

    async def scan_task_definitions(self) -> None:
        """
        Periodically scan the 'agent_runner/tasks/definitions' directory for new or updated tasks.
        This provides dynamic task discovery without restarts.
        """
        from pathlib import Path
        try:
            import yaml
        except ImportError:
            return

        defs_dir = Path(__file__).parent / "tasks" / "definitions"
        if not defs_dir.exists():
            return

        from agent_runner.task_loader import load_tasks_from_config, register_tasks_from_config
        
        while self.running:
            try:
                # 1. Discover all current task files
                current_files = set(defs_dir.glob("*.yaml"))
                current_files.update(defs_dir.glob("*.yml"))
                
                # 2. Load each file as a potential task
                for file_path in current_files:
                    try:
                        # Use async file I/O
                        import aiofiles
                        async with aiofiles.open(file_path, "r") as f:
                            content = await f.read()
                            task_config = yaml.safe_load(content)
                            
                        if not task_config:
                            continue
                            
                        # If name not in body, infer from filename
                        if "name" not in task_config:
                            task_config["name"] = file_path.stem

                        task_name = task_config["name"]
                        
                        # Check if we need to register/update
                        # We use a simple wrapper to pass this single task config to the loader
                        # The loader expects {"agent_runner": {"periodic_tasks": {name: config}}}
                        # We simulate this structure to reuse the robust loading logic
                        wrapper_config = {
                            "agent_runner": {
                                "periodic_tasks": {
                                    task_name: task_config
                                }
                            }
                        }
                        
                        # This registers or updates the task in self.tasks
                        # The loader handles checking if it exists/needs update
                        await register_tasks_from_config(self, wrapper_config)
                        
                    except Exception as e:
                        logger.error(f"Failed to load task definition {file_path.name}: {e}")

                # 3. [Optional] Remove tasks whose files were deleted?
                # For now, we assume "disable in file" is the preferred method vs deleting file.
                # Deleting logic is risky if task is running. 
                
            except Exception as e:
                logger.error(f"Task scanner loop error: {e}")
            
            # Scan every 60 seconds
            from agent_runner.constants import SLEEP_WATCHDOG
            await asyncio.sleep(SLEEP_WATCHDOG)

    async def start(self) -> None:
        """Start all registered tasks."""
        if self.running:
            logger.warning("Background task manager already running")
            return
        
        self.running = True
        logger.info(f"Starting background task manager with {len(self.tasks)} tasks")
        
        # Subscribe to notifications for reactive behavior
        self._subscribe_to_notifications()

        # Start Dynamic Task Scanner
        self._task_handles["_scanner"] = asyncio.create_task(self.scan_task_definitions())
        
        for name, task in self.tasks.items():
            if not task.enabled:
                continue
            
            self._start_task_wrapper(name, task)
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
                    "interval": task.interval, # [NEW]
                    "schedule": task.schedule, # [NEW]
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


from agent_runner.service_registry import ServiceRegistry

def get_task_manager() -> BackgroundTaskManager:
    """Get the global task manager instance."""
    global _task_manager
    if _task_manager is None:
        try:
            _task_manager = ServiceRegistry.get_task_manager()
        except RuntimeError:
            _task_manager = BackgroundTaskManager()
            ServiceRegistry.register_task_manager(_task_manager)
    return _task_manager


# MEMORY HEALTH MONITORING TASK
async def memory_health_monitor():
    """
    Background task to monitor memory server health and stability.
    Attempts recovery if instability is detected.
    """
    try:
        from agent_runner.agent_runner import get_shared_state
        from agent_runner.service_registry import ServiceRegistry

        state = get_shared_state()
        if not state or not hasattr(state, 'memory') or not state.memory:
            logger.debug("Memory health monitor: No memory server to monitor")
            return

        memory = state.memory
        was_unstable = getattr(state, 'memory_unstable', False)

        # Quick connectivity test
        try:
            test_result = await memory._execute_query("INFO FOR DB;")
            connection_healthy = test_result is not None

            if connection_healthy and was_unstable:
                # Memory has recovered from instability
                logger.info("Memory health monitor: Connection restored, clearing instability flag")
                state.memory_unstable = False
                # Could trigger MCP reload here if needed
            elif not connection_healthy and not was_unstable:
                # Memory has become unstable
                logger.warning("Memory health monitor: Connection lost, marking as unstable")
                state.memory_unstable = True
                # Could trigger fallback mode here

        except Exception as e:
            if not was_unstable:
                logger.warning(f"Memory health monitor: Connection test failed: {e}")
                state.memory_unstable = True

    except Exception as e:
        logger.error(f"Memory health monitor task failed: {e}")


# Register memory health monitoring task
_memory_monitor_task = Task(
    name="memory_health_monitor",
    task_type=TaskType.MONITOR,
    func=memory_health_monitor,
    interval=30.0,  # Check every 30 seconds
    enabled=True,
    priority=TaskPriority.HIGH
)


# SYSTEM HEALTH MONITOR (5s Heartbeat)
async def system_health_monitor():
    """
    Monitor system health every 5 seconds.
    Updates in-memory cache and persists to DB on change.
    """
    try:
        from agent_runner.agent_runner import get_shared_state, get_shared_engine
        import httpx, time, asyncio
        
        state = get_shared_state()
        if not state: return

        # 1. Parallel Checks
        async def check_rag():
            try:
                async with httpx.AsyncClient(timeout=0.2) as client:
                    resp = await client.get(f"http://localhost:5555/health")
                    return resp.status_code == 200
            except: return False

        async def check_facts():
            if not (hasattr(state, "memory") and state.memory and state.memory.initialized): return "N/A"
            try:
                from agent_runner.db_utils import run_query
                res = await run_query(state, "SELECT count() FROM fact GROUP ALL")
                if res and isinstance(res, list) and len(res) > 0:
                    return f"{res[0].get('count', 0):,} Facts"
            except: pass
            return "N/A"

        async def check_latency():
            try:
                t0 = time.time()
                url = "http://localhost:11434"
                if state.config.get("llm_providers", {}).get("ollama", {}).get("base_url"):
                    url = state.config["llm_providers"]["ollama"]["base_url"]
                async with httpx.AsyncClient(timeout=0.2) as client:
                    await client.get(url)
                return f"{int((time.time()-t0)*1000)}ms"
            except: return "Timeout"

        rag_online, fact_count, latency = await asyncio.gather(
            check_rag(), check_facts(), check_latency()
        )

        # 2. Gather Local State
        memory_online = hasattr(state, "memory") and state.memory and state.memory.initialized
        
        engine = get_shared_engine()
        mcp_count = len(state.mcp_servers)
        mcp_tools = sum(len(tools) for tools in engine.executor.mcp_tool_cache.values()) if engine else 0
        
        internet = getattr(state, "internet_available", True) # Default true if unknown
        
        open_breakers = []
        if hasattr(state, "mcp_circuit_breaker"):
             for name, breaker in state.mcp_circuit_breaker.breakers.items():
                 if breaker.state.value == "open":
                     open_breakers.append(name)

        # 3. Construct Snapshot
        snapshot = {
            "rag_online": rag_online,
            "memory_online": memory_online,
            "fact_count": fact_count,
            "mcp_count": mcp_count,
            "mcp_tools": mcp_tools,
            "internet_online": internet,
            "latency": latency,
            "open_breakers": open_breakers,
            "timestamp": time.time() 
        }

        # 4. Compare & Update
        current_cache = getattr(state, "system_dashboard_data", {})
        
        # Compare critical fields (ignore timestamp/latency small jitters)
        # We only persist to DB if structural change or significant metric shift?
        # User said "updated every 5 seconds if any had changed". checking equality strictly.
        # But latency changes every ms. We should ignore latency for "DB Write" trigger?
        # Let's say we write if latency bucket changes? or just write. 
        # Actually user said "if any had changed". 
        # Let's clean the snapshot for comparison (remove timestamp)
        
        snap_cmp = snapshot.copy()
        del snap_cmp["timestamp"]
        # Allow latency jitter (e.g. only update if status "Timeout" vs "10ms")
        # For strict matching, we keep latency. It will update DB almost every 5s. That is acceptable (~17k writes/day). Surreal handles it.
        
        old_cmp = current_cache.copy()
        if "timestamp" in old_cmp: del old_cmp["timestamp"]
        
        # Update Cache (Always, for live dashboard)
        state.system_dashboard_data = snapshot
        
        if snap_cmp != old_cmp:
            # Change detected
            if hasattr(state, "memory") and state.memory:
                 from agent_runner.db_utils import run_query
                 # Persist to system_state
                 # We use a dedicated item 'dashboard_monitor'
                 import json
                 # Create/Update
                 q = f"""
                 LET $data = {json.dumps(snapshot)};
                 UPDATE system_state SET details = $data WHERE item = 'dashboard_monitor';
                 IF count(SELECT * FROM system_state WHERE item = 'dashboard_monitor') == 0 THEN 
                    CREATE system_state SET item = 'dashboard_monitor', details = $data 
                 END;
                 """
                 await run_query(state, q)
                 # logger.debug("Persisted new system dashboard snapshot to DB")
                 
    except Exception as e:
        logger.warning(f"System Health Monitor failed: {e}")
