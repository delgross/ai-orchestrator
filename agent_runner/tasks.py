import asyncio
import time
import logging
from typing import Dict, Any
from datetime import datetime
from agent_runner.state import AgentState
from common.notifications import notify_high, notify_info

from common.unified_tracking import track_event, track_health_event, EventSeverity, EventCategory

logger = logging.getLogger("agent_runner")

async def internet_check_task(state: AgentState) -> None:
    """Check internet availability."""
    client = await state.get_http_client()
    try:
        resp = await client.get("https://www.google.com", timeout=2.0)
        is_avail = resp.status_code < 400
        if is_avail != state.internet_available:
            if is_avail:
                track_event(
                    event="internet_restored",
                    message="Internet connection restored",
                    severity=EventSeverity.INFO,
                    category=EventCategory.SYSTEM,
                    component="internet_check"
                )
            else:
                track_event(
                    event="internet_lost",
                    message="Internet connection lost",
                    severity=EventSeverity.HIGH,
                    category=EventCategory.SYSTEM,
                    component="internet_check"
                )
        state.internet_available = is_avail
    except Exception as e:
        if state.internet_available:
            track_event(
                event="internet_lost_exception",
                message=f"Internet connection lost: {e}",
                severity=EventSeverity.HIGH,
                category=EventCategory.SYSTEM,
                component="internet_check",
                error=e
            )
        state.internet_available = False

async def health_check_task(state: AgentState) -> None:
    """Update system health status."""
    # Logic for comprehensive health check...
    pass

async def stdio_process_health_monitor(state: AgentState) -> None:
    """Monitor and restart dead stdio processes."""
    from agent_runner.transports.stdio import cleanup_stdio_process
    
    for server, proc in list(state.stdio_processes.items()):
        if proc.returncode is not None:
            track_health_event(
                event="stdio_process_died",
                message=f"Stdio process for '{server}' died (exit code: {proc.returncode})",
                severity=EventSeverity.HIGH,
                component="stdio_monitor",
                metadata={"server": server, "returncode": proc.returncode}
            )
            await cleanup_stdio_process(state, server)
