"""
Memory Recovery Module

Handles background recovery of memory connections when they fail during startup.
This module provides resilient recovery mechanisms for database connectivity issues.
"""

import asyncio
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agent_runner.state import AgentState
    from agent_runner.memory_server import MemoryServer

logger = logging.getLogger("agent_runner.memory_recovery")

# Recovery configuration constants
RECOVERY_RETRY_DELAY = 10  # Base delay between recovery attempts (seconds)
MAX_RECOVERY_ATTEMPTS = 5  # Maximum number of recovery attempts
RECOVERY_BACKOFF_MULTIPLIER = 1.0  # Multiplier for exponential backoff


async def background_memory_recovery(state: "AgentState") -> None:
    """
    Background task to recover memory connection if it becomes available.

    This function runs in the background after startup if memory initialization fails.
    It periodically attempts to reconnect to the database and restore full functionality.

    Args:
        state: The agent state object
    """
    await asyncio.sleep(RECOVERY_RETRY_DELAY)  # Wait before first retry

    for recovery_attempt in range(MAX_RECOVERY_ATTEMPTS):
        try:
            logger.info(f"Attempting memory server recovery (attempt {recovery_attempt + 1}/{MAX_RECOVERY_ATTEMPTS})...")

            # Create new memory server if needed
            if state.memory is None:
                from agent_runner.memory_server import MemoryServer
                state.memory = MemoryServer(state)

            # Attempt to initialize
            await state.memory.initialize()

            if state.memory.initialized:
                logger.info("✅ Memory server recovery successful!")

                # Remove from degraded features
                if "memory" in getattr(state, 'degraded_features', []):
                    state.degraded_features.remove("memory")

                # Re-register with service registry
                try:
                    from agent_runner.service_registry import ServiceRegistry
                    ServiceRegistry.register_memory_server(state.memory)
                except Exception as reg_err:
                    logger.warning(f"ServiceRegistry registration failed during recovery: {reg_err}")

                # Reload MCP servers now that memory is available
                try:
                    from agent_runner.config import load_mcp_servers
                    await load_mcp_servers(state)
                    logger.info("MCP servers reloaded after memory recovery")
                except Exception as reload_err:
                    logger.warning(f"Failed to reload MCP servers after memory recovery: {reload_err}")

                # Recovery successful - exit the loop
                break

        except Exception as recovery_err:
            logger.debug(f"Memory recovery attempt {recovery_attempt + 1} failed: {recovery_err}")

            if recovery_attempt < MAX_RECOVERY_ATTEMPTS - 1:
                # Exponential backoff: 10s, 20s, 30s, 40s
                delay = RECOVERY_RETRY_DELAY * (recovery_attempt + 1)
                logger.debug(f"Waiting {delay}s before next recovery attempt...")
                await asyncio.sleep(delay)

    if not getattr(state.memory, 'initialized', False):
        logger.warning(f"Memory server recovery failed after {MAX_RECOVERY_ATTEMPTS} attempts. System will continue in degraded mode.")


async def start_memory_recovery_if_needed(state: "AgentState") -> None:
    """
    Start background memory recovery if memory is not available.

    This should be called during startup after memory initialization fails.

    Args:
        state: The agent state object
    """
    if not getattr(state.memory, 'initialized', False):
        logger.info("Starting background memory recovery task...")
        asyncio.create_task(background_memory_recovery(state))
    else:
        logger.debug("Memory server is healthy - no recovery needed")

