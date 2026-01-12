"""
Utility functions for safe task management and error handling.
Prevents fire-and-forget tasks from failing silently and consuming resources.
"""

import asyncio
import logging
from typing import Coroutine, Any, Optional
from collections import defaultdict

logger = logging.getLogger("agent_runner.task_utils")

# Track task health for monitoring
_task_stats = defaultdict(lambda: {"created": 0, "completed": 0, "failed": 0})
_task_stats_lock = asyncio.Lock()


async def safe_task_wrapper(coro: Coroutine, task_name: str = "unknown", log_errors: bool = True) -> None:
    """
    Wrapper for fire-and-forget tasks that ensures exceptions are caught and logged.
    
    Args:
        coro: The coroutine to run
        task_name: Name of the task for logging/monitoring
        log_errors: Whether to log errors (default: True)
    """
    try:
        await coro
        async with _task_stats_lock:
            _task_stats[task_name]["completed"] += 1
    except asyncio.CancelledError:
        # Task was cancelled, this is normal
        async with _task_stats_lock:
            _task_stats[task_name]["completed"] += 1
        if log_errors:
            logger.debug(f"Task '{task_name}' was cancelled")
    except Exception as e:
        async with _task_stats_lock:
            _task_stats[task_name]["failed"] += 1
        if log_errors:
            logger.error(f"Fire-and-forget task '{task_name}' failed: {e}", exc_info=True)


def create_safe_task(coro: Coroutine, task_name: str = "unknown", log_errors: bool = True) -> asyncio.Task:
    """
    Create a fire-and-forget task with error handling.
    
    This is a drop-in replacement for asyncio.create_task() that ensures
    exceptions in background tasks are caught and logged.
    
    Args:
        coro: The coroutine to run
        task_name: Name of the task for logging/monitoring
        log_errors: Whether to log errors (default: True)
    
    Returns:
        The created task
    """
    # Increment created count in an async wrapper
    async def _wrapped_coro():
        # Increment created count
        try:
            async with _task_stats_lock:
                _task_stats[task_name]["created"] += 1
        except Exception:
            # If lock acquisition fails, continue anyway
            pass
        # Run the original coroutine
        await coro
    
    # Wrap with error handling
    wrapped = safe_task_wrapper(_wrapped_coro(), task_name, log_errors)
    return asyncio.create_task(wrapped)


async def get_task_stats() -> dict:
    """
    Get statistics about fire-and-forget task health.
    
    Returns:
        Dictionary mapping task names to their statistics
    """
    async with _task_stats_lock:
        return dict(_task_stats)


async def get_task_health_summary() -> dict:
    """
    Get a health summary of all tracked tasks.
    
    Returns:
        Dictionary with overall health metrics
    """
    async with _task_stats_lock:
        total_created = sum(s["created"] for s in _task_stats.values())
        total_completed = sum(s["completed"] for s in _task_stats.values())
        total_failed = sum(s["failed"] for s in _task_stats.values())
        
        return {
            "total_tasks": total_created,
            "completed": total_completed,
            "failed": total_failed,
            "pending": total_created - total_completed - total_failed,
            "failure_rate": total_failed / total_created if total_created > 0 else 0.0,
            "by_task": dict(_task_stats)
        }


