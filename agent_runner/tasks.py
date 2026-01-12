import logging
from agent_runner.state import AgentState

from common.unified_tracking import track_event, track_health_event, EventSeverity, EventCategory

logger = logging.getLogger("agent_runner")



# Robust Health Check from Monitor
from agent_runner.health_monitor import health_check_task as _robust_health_check

async def health_check_task() -> None:
    """Update system health status (Delegates to robust monitor)."""
    await _robust_health_check()

async def stdio_process_health_monitor(state: AgentState) -> None:
    """Monitor and cleanup dead stdio processes. Runs periodically to prevent resource leaks."""
    from agent_runner.transports.stdio import cleanup_stdio_process
    
    cleaned_count = 0
    for server, proc in list(state.stdio_processes.items()):
        if proc.returncode is not None:
            logger.info(f"Dead stdio process detected for '{server}' (returncode={proc.returncode}), cleaning up...")
            track_health_event(
                event="stdio_process_died",
                message=f"Stdio process for '{server}' died (exit code: {proc.returncode})",
                severity=EventSeverity.HIGH,
                component="stdio_monitor",
                metadata={"server": server, "returncode": proc.returncode}
            )
            try:
                await cleanup_stdio_process(state, server)
                cleaned_count += 1
            except Exception as e:
                logger.error(f"Failed to cleanup dead process '{server}': {e}", exc_info=True)
    
    if cleaned_count > 0:
        logger.info(f"Cleaned up {cleaned_count} dead stdio process(es)")

async def modal_heartbeat_task(state: AgentState) -> None:
    """Check if Cloud GPU (Modal) is actually warmed up and ready."""
    try:
        from agent_runner.modal_tasks import has_modal
        if not has_modal:
            state.cloud_gpu_ready = False
            return
            
        # We don't want to trigger a full build just for a heartbeat, 
        # so we check if the app name is 'initializing' or 'running' via the CLI or lookup
        # For now, we assume if it's not circuit broken, we 'hope' it's ready,
        # but a better check is hitting a no-op function.
        
        # Simple heuristic: If we have internet, we assume it's a candidate.
        # But we'll mark as False if a recent call failed.
        if not state.internet_available:
            state.cloud_gpu_ready = False
            return

        # Explicit lookup (mock check for now, can be improved with real modal app lookup)
        # If we were truly thorough, we'd call a .remote() no-op, but that might incur costs.
        # Instead, we rely on the Circuit Breaker which already tracks failures.
        # We'll sync cloud_gpu_ready to the breaker status of the unified model.
        
        unified_model = "Qwen2-VL-72B-Instruct"
        if hasattr(state, "mcp_circuit_breaker"):
            status = state.mcp_circuit_breaker.get_status().get(unified_model, {})
            # If open, it's definitely not ready
            if status.get("state") == "open":
                state.cloud_gpu_ready = False
                return
        
        state.cloud_gpu_ready = True
    except Exception as e:
        logger.error(f"Modal heartbeat check failed: {e}")
        state.cloud_gpu_ready = False

async def thinking_session_cleanup_task(state: AgentState) -> None:
    """Clean up old thinking sessions (older than 7 days). Runs daily."""
    try:
        if not hasattr(state, "memory") or not state.memory:
            return
        
        await state.memory.ensure_connected()
        
        # Delete sessions older than 7 days
        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(days=7)
        cutoff_timestamp = cutoff.timestamp()
        
        query = f"""
        DELETE thinking_session 
        WHERE timestamp < time::from_unix({cutoff_timestamp});
        """
        
        from agent_runner.db_utils import run_query
        result = await run_query(state, query)
        deleted_count = len(result) if result else 0
        
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old thinking session(s)")
            track_event(
                event="thinking_session_cleanup",
                message=f"Cleaned up {deleted_count} old thinking sessions",
                severity=EventSeverity.INFO,
                category=EventCategory.MAINTENANCE,
                metadata={"deleted_count": deleted_count}
            )
    except Exception as e:
        logger.error(f"Thinking session cleanup failed: {e}", exc_info=True)
