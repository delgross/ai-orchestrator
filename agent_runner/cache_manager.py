"""
Cache management tasks for agent-runner.

Provides:
- Cache cleanup (expired entries)
- Cache statistics
- Cache optimization
"""

from __future__ import annotations

import logging
import time
from typing import Dict, Any

logger = logging.getLogger("agent_runner.cache_manager")

# Import from agent_runner (will be available at runtime)
_tool_cache: Dict[str, Dict[str, Any]] = {}
TOOL_CACHE_ENABLED: bool = True


async def cleanup_expired_cache() -> None:
    """Remove expired cache entries."""
    if not TOOL_CACHE_ENABLED:
        return
    
    now = time.time()
    expired_count = 0
    initial_size = len(_tool_cache)
    
    expired_keys = [
        key
        for key, entry in _tool_cache.items()
        if now > entry.get("expires_at", 0.0)
    ]
    
    for key in expired_keys:
        _tool_cache.pop(key, None)
        expired_count += 1
    
    if expired_count > 0:
        logger.info(f"Cache cleanup: removed {expired_count} expired entries (from {initial_size} to {len(_tool_cache)})")


async def optimize_cache_size() -> None:
    """Optimize cache size by removing oldest entries if over limit."""
    if not TOOL_CACHE_ENABLED:
        return
    
    MAX_CACHE_SIZE = 100
    current_size = len(_tool_cache)
    
    if current_size <= MAX_CACHE_SIZE:
        return
    
    # Sort by timestamp and remove oldest entries
    sorted_entries = sorted(
        _tool_cache.items(),
        key=lambda x: x[1].get("timestamp", 0)
    )
    
    to_remove = current_size - MAX_CACHE_SIZE
    removed = 0
    
    for key, _ in sorted_entries[:to_remove]:
        _tool_cache.pop(key, None)
        removed += 1
    
    if removed > 0:
        logger.info(f"Cache optimization: removed {removed} oldest entries (from {current_size} to {len(_tool_cache)})")


async def cache_management_task() -> None:
    """Periodic cache management task."""
    logger.debug("Running cache management task")
    
    await cleanup_expired_cache()
    await optimize_cache_size()
    
    if TOOL_CACHE_ENABLED:
        logger.debug(f"Cache status: {len(_tool_cache)} entries")


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    if not TOOL_CACHE_ENABLED:
        return {"enabled": False, "entries": 0}
    
    now = time.time()
    expired = sum(
        1
        for entry in _tool_cache.values()
        if now > entry.get("expires_at", 0.0)
    )
    
    return {
        "enabled": True,
        "entries": len(_tool_cache),
        "expired": expired,
        "active": len(_tool_cache) - expired,
    }


def initialize_cache_manager(
    tool_cache: Dict[str, Dict[str, Any]],
    tool_cache_enabled: bool,
) -> None:
    """Initialize cache manager with runtime dependencies."""
    global _tool_cache, TOOL_CACHE_ENABLED
    _tool_cache = tool_cache
    TOOL_CACHE_ENABLED = tool_cache_enabled




















