"""
Health monitoring tasks for agent-runner.

Monitors:
- MCP server health
- Circuit breaker recovery
- Dependency health (gateway, etc.)
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger("agent_runner.health_monitor")

# Notification system
from common.notifications import notify_health, notify_high, notify_critical

# Import from agent_runner (will be available at runtime)
MCP_SERVERS: Dict[str, Any] = {}
_mcp_circuit_breaker: Dict[str, Dict[str, Any]] = {}
GATEWAY_BASE: str = "http://127.0.0.1:5455"
_http_client: Optional[httpx.AsyncClient] = None
_state: Optional[Any] = None # Will store AgentState


async def check_mcp_server_health(server: str) -> Dict[str, Any]:
    """Check health of a single MCP server."""
    cfg = MCP_SERVERS.get(server)
    if not cfg:
        return {"ok": False, "error": "Server not configured"}
    
    scheme = cfg.get("scheme", "http")
    
    # Check circuit breaker status via registry
    if not _mcp_circuit_breaker.is_allowed(server):
        status = _mcp_circuit_breaker.get_breaker(server).to_dict()
        return {
            "ok": False,
            "error": "Circuit breaker active",
            "state": status["state"],
            "disabled_until": status["disabled_until"],
        }
    
    return {"ok": True, "scheme": scheme}


async def test_circuit_breaker_recovery() -> None:
    """Test disabled MCP servers using actual tool_mcp_proxy() code path."""
    now = time.time()
    recovered = []
    failed_recovery = []
    
    # Get status from registry
    cb_status = _mcp_circuit_breaker.get_status()
    
    for server, status in cb_status.items():
        state = status.get("state")
        
        # If server is open (disabled), test it
        if state == "open":
            logger.info(f"Testing circuit breaker recovery for '{server}'")
            
            if server not in MCP_SERVERS:
                continue
            
            # Use actual tool_mcp_proxy() with bypass flag to test recovery
            try:
                from agent_runner.tools.mcp import tool_mcp_proxy
                
                # Try a lightweight health check tool
                test_res = await tool_mcp_proxy(
                    _state,
                    server=server,
                    tool="list_models" if server == "ollama" else "check_health",
                    arguments={},
                    bypass_circuit_breaker=True
                )
                
                test_success = False
                if test_res.get("ok"):
                    test_success = True
                elif "not found" in str(test_res.get("error", "")).lower():
                    # Tool doesn't exist but server responded - that's a partial success
                    test_success = True
                
                if test_success:
                    logger.info(f"MCP server '{server}' recovery test passed, recording success in breaker")
                    _mcp_circuit_breaker.record_success(server)
                    recovered.append(server)
                else:
                    logger.info(f"MCP server '{server}' recovery test failed")
                    _mcp_circuit_breaker.record_failure(server)
                    failed_recovery.append(server)

            except Exception as e:
                logger.debug(f"Error during recovery test for '{server}': {e}")
                failed_recovery.append(server)
    
    if recovered:
        logger.info(f"Circuit breaker recovery: {len(recovered)} server(s) entered half-open state: {recovered}")
    if failed_recovery:
        logger.info(f"Circuit breaker recovery: {len(failed_recovery)} server(s) still failing: {failed_recovery}")


async def check_gateway_health() -> Dict[str, Any]:
    """Check health of the gateway (router)."""
    global _http_client
    
    if not _http_client:
        return {"ok": False, "error": "HTTP client not initialized"}
    
    try:
        start = time.time()
        response = await _http_client.get(f"{GATEWAY_BASE}/health", timeout=10.0)
        elapsed = (time.time() - start) * 1000
        
        if response.status_code == 200:
            data = response.json()
            return {
                "ok": True,
                "status_code": response.status_code,
                "response_time_ms": round(elapsed, 2),
                "data": data,
            }
        else:
            return {
                "ok": False,
                "status_code": response.status_code,
                "error": f"HTTP {response.status_code}",
            }
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def check_dashboard_health() -> Dict[str, Any]:
    """Verify that the dashboard is being served correctly."""
    global _http_client
    if not _http_client:
        return {"ok": False, "error": "HTTP client not initialized"}
    
    try:
        # Check v2 dashboard
        url = f"{GATEWAY_BASE}/v2/index.html"
        start = time.time()
        response = await _http_client.get(url, timeout=5.0)
        elapsed = (time.time() - start) * 1000
        
        if response.status_code == 200:
            return {
                "ok": True,
                "response_time_ms": round(elapsed, 2),
                "content_length": len(response.text)
            }
        else:
            return {"ok": False, "status_code": response.status_code}
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def check_internet_connectivity() -> bool:
    """Check if the system has internet access."""
    global _http_client
    if not _http_client:
        return True # Assume online if we can't check
    
    try:
        # Try a reliable public DNS service or major site
        response = await _http_client.head("https://www.google.com", timeout=5.0)
        return response.status_code < 400
    except Exception:
        return False


async def health_check_task() -> None:
    """Periodic health check task."""
    logger.debug("Running health check task")
    
    # Update internet availability state
    if _state:
        # Only check every 60 seconds to avoid noise
        if time.time() - _state.last_internet_check > 60:
            original_state = _state.internet_available
            _state.internet_available = await check_internet_connectivity()
            _state.last_internet_check = time.time()
            
            if original_state != _state.internet_available:
                status = "RESTORED" if _state.internet_available else "LOST"
                logger.info(f"Internet connectivity {status}")
                try:
                    from common.unified_tracking import track_health_event, EventSeverity
                    track_health_event(
                        event="internet_connectivity_change",
                        message=f"Internet connectivity {status}",
                        severity=EventSeverity.MEDIUM if _state.internet_available else EventSeverity.HIGH,
                        component="health_monitor",
                        metadata={"internet_available": _state.internet_available}
                    )
                except Exception:
                    pass

    # Check gateway health
    gateway_health = await check_gateway_health()
    if not gateway_health.get("ok"):
        error_msg = gateway_health.get('error', 'Unknown error')
        logger.warning(f"Gateway health check failed: {error_msg}")
        # Use unified tracking if available
        try:
            from common.unified_tracking import track_health_event, EventSeverity, EventCategory
            track_health_event(
                event="gateway_health_check_failed",
                message=f"Gateway is unhealthy: {error_msg}",
                severity=EventSeverity.HIGH,
                component="health_monitor",
                metadata={"gateway_base": GATEWAY_BASE, "health_result": gateway_health}
            )
        except ImportError:
            # Fallback to old system
            notify_health(
                title="Gateway Health Check Failed",
                message=f"Gateway is unhealthy: {error_msg}",
                source="health_monitor",
                metadata={"gateway_base": GATEWAY_BASE, "health_result": gateway_health}
            )
    
    # Check Dashboard health if gateway is up
    if gateway_health.get("ok"):
        dash_health = await check_dashboard_health()
        if not dash_health.get("ok"):
            logger.error(f"DASHBOARD DOWN: {dash_health.get('error', 'HTTP ' + str(dash_health.get('status_code')))}")
            try:
                from common.unified_tracking import track_health_event, EventSeverity
                track_health_event(
                    event="dashboard_down",
                    message="Dashboard UI is unreachable",
                    severity=EventSeverity.HIGH,
                    component="health_monitor",
                    metadata={"result": dash_health}
                )
            except Exception:
                pass
    
    # Test circuit breaker recovery (run more frequently for faster recovery)
    await test_circuit_breaker_recovery()
    
    # Check MCP server health (summary)
    healthy_servers = 0
    disabled_servers = []
    for server in MCP_SERVERS.keys():
        health = await check_mcp_server_health(server)
        if health.get("ok"):
            healthy_servers += 1
        else:
            disabled_servers.append(server)
    
    # Check memory growth
    try:
        from agent_runner.tools.mcp import tool_mcp_proxy
        mem_stats = await tool_mcp_proxy(
            _state,
            server="project-memory",
            tool="get_memory_stats",
            arguments={},
            bypass_circuit_breaker=True
        )
        if mem_stats.get("ok"):
            res = mem_stats.get("result", {})
            ep_count = res.get("episode_count", 0)
            # Threshold: Warn if more than 1000 episodes (can be adjusted)
            if ep_count > 1000:
                logger.warning(f"Memory growth warning: {ep_count} episodes in database. Consider manual review or pruning.")
                try:
                    from common.unified_tracking import track_health_event, EventSeverity
                    track_health_event(
                        event="memory_growth_warning",
                        message=f"Large number of episodes in memory: {ep_count}",
                        severity=EventSeverity.MEDIUM,
                        component="health_monitor",
                        metadata={"episode_count": ep_count}
                    )
                except Exception:
                    pass
    except Exception as e:
        logger.debug(f"Failed to check memory stats in health monitor: {e}")

    if disabled_servers:
        logger.info(f"MCP server health: {healthy_servers} healthy, {len(disabled_servers)} disabled")
        # Only notify if there are multiple disabled servers or critical ones
        if len(disabled_servers) > 1 or "project-memory" in disabled_servers:
            # Use unified tracking if available
            try:
                from common.unified_tracking import track_health_event, EventSeverity, EventCategory
                is_critical = "project-memory" in disabled_servers
                track_health_event(
                    event="mcp_server_health_issues",
                    message=f"{len(disabled_servers)} MCP server(s) disabled: {', '.join(disabled_servers)}",
                    severity=EventSeverity.CRITICAL if is_critical else EventSeverity.HIGH,
                    component="health_monitor",
                    metadata={"disabled_servers": disabled_servers, "healthy_count": healthy_servers}
                )
            except ImportError:
                # Fallback to old system
                notify_health(
                    title="MCP Server Health Issues",
                    message=f"{len(disabled_servers)} MCP server(s) disabled: {', '.join(disabled_servers)}",
                    source="health_monitor",
                    metadata={"disabled_servers": disabled_servers, "healthy_count": healthy_servers}
                )


def initialize_health_monitor(
    mcp_servers: Dict[str, Any],
    mcp_circuit_breaker: Any,
    gateway_base: str,
    http_client: Optional[httpx.AsyncClient],
    state: Any = None
) -> None:
    """Initialize health monitor with runtime dependencies."""
    global MCP_SERVERS, _mcp_circuit_breaker, GATEWAY_BASE, _http_client, _state
    MCP_SERVERS = mcp_servers
    _mcp_circuit_breaker = mcp_circuit_breaker
    GATEWAY_BASE = gateway_base
    _http_client = http_client
    _state = state

