"""
Health monitoring tasks for agent-runner.

Monitors:
- MCP server health
- Circuit breaker recovery
- Dependency health (gateway, etc.)
"""

from __future__ import annotations

import logging
import time
from typing import Dict, Any, Optional
import asyncio
import httpx

logger = logging.getLogger("agent_runner.health_monitor")

# Notification system
from common.notifications import notify_health

# Import from agent_runner (will be available at runtime)
MCP_SERVERS: Dict[str, Any] = {}
_mcp_circuit_breaker: Any = None
GATEWAY_BASE: str = "http://127.0.0.1:5455"
_http_client: Optional[httpx.AsyncClient] = None
_state: Optional[Any] = None # Will store AgentState


async def check_mcp_server_health(server: str, timeout: float = 15.0, retries: int = 2) -> Dict[str, Any]:
    """Actually test server health with lightweight call."""
    cfg = MCP_SERVERS.get(server)
    if not cfg:
        return {"ok": False, "error": "Server not configured", "last_check": time.time()}
    
    # For stdio servers, check if process is alive first (lightweight)
    if cfg.get("type") == "stdio" and _state and server in _state.stdio_processes:
        proc = _state.stdio_processes[server]
        if proc.returncode is not None:  # Note: asyncio.subprocess.Process uses returncode, not poll()
            return {"ok": False, "error": "Process died", "last_check": time.time()}
    
    # Actually test server with tools/list (lightweight call)
    for attempt in range(retries + 1):
        try:
            from agent_runner.tools.mcp import tool_mcp_proxy
            
            res = await asyncio.wait_for(
                tool_mcp_proxy(_state, server, "tools/list", {}, bypass_circuit_breaker=True),
                timeout=timeout
            )
            
            if res.get("ok"):
                # Also check that server actually has tools (not just responds)
                tools = res.get("result", {}).get("tools", [])
                if len(tools) == 0:
                    return {"ok": False, "error": "Server responds but provides no tools", "last_check": time.time()}
                return {"ok": True, "last_check": time.time()}
            
            # If not last attempt, retry
            if attempt < retries:
                await asyncio.sleep(1.0)
                continue
                
            return {"ok": False, "error": res.get("error"), "last_check": time.time()}
            
        except asyncio.TimeoutError:
            if attempt < retries:
                await asyncio.sleep(1.0)
                continue
            return {"ok": False, "error": f"Health check timeout ({timeout}s)", "last_check": time.time()}
        except Exception as e:
            if attempt < retries:
                await asyncio.sleep(1.0)
                continue
            return {"ok": False, "error": str(e), "last_check": time.time()}


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

    if recovered:
        logger.info(f"Circuit breaker recovery: {len(recovered)} server(s) entered half-open state: {recovered}")
    if failed_recovery:
        logger.info(f"Circuit breaker recovery: {len(failed_recovery)} server(s) still failing: {failed_recovery}")


async def check_critical_services() -> None:  # Type hint already present
    """Monitor core services (Router) and trigger self-healing if needed."""
    try:
        # Check Router Health
        async with httpx.AsyncClient(timeout=3.0) as client:
            try:
                r = await client.get(f"{GATEWAY_BASE}/health")
                if r.status_code != 200:
                    logger.warning(f"Router health check returned {r.status_code}. Potential issue.")
            except (httpx.ConnectError, httpx.ReadTimeout):
                logger.error("CRITICAL: Router is unreachable! Triggering self-healing restart...")
                
                # Trigger Restart via manage.sh
                try:
                    # We run this detached or blocking? Blocking is safer to avoid loops.
                    # We use the absolute path to manage.sh
                    from agent_runner.config import PROJECT_ROOT
                    cmd_path = f"{PROJECT_ROOT}/bin/manage.sh"
                    
                    # Log the attempt
                    logger.info(f"Executing self-healing restart: {cmd_path} restart router")
                    
                    # NON-BLOCKING EXECUTION
                    proc = await asyncio.create_subprocess_exec(
                        cmd_path, "restart", "router",
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    
                    stdout, stderr = await proc.communicate()
                    
                    if proc.returncode == 0:
                         logger.info("Router restart triggered successfully.")
                    else:
                         logger.error(f"Router restart failed (code {proc.returncode}): {stderr.decode()}")

                except Exception as restart_err:
                    logger.error(f"Self-healing execution failed: {restart_err}")


    except Exception as e:
        logger.error(f"Critical service check failed: {e}")


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
    """Check if the system has internet access using multiple reliable targets."""
    # ISOLATION FIX: Use a dedicated, fresh client for connectivity checks.
    # Do NOT reuse the shared app client (_http_client) to avoid pool exhaustion or deadlocks.
    async def check_target(client: httpx.AsyncClient, url: str) -> bool:
        try:
            r = await client.head(url, timeout=5.0)
            if r.status_code < 400: return True
        except Exception as e:
            logger.debug(f"Health check failed for {url}: {e}")
        return False

    try:
        # 1. Try Python/HTTPX first
        async with httpx.AsyncClient(timeout=5.0) as private_client:
            targets = [
                "https://www.google.com",
                "https://www.cloudflare.com",
                "https://www.microsoft.com",
                "https://1.1.1.1"
            ]
            
            tasks = [check_target(private_client, t) for t in targets]
            for f in asyncio.as_completed(tasks):
                if await f:
                    return True
            
            logger.warning("Internet check failed for ALL targets.")
            return False

    except Exception as e:
        logger.error(f"Critical error during internet check: {e}")
        return False


async def health_check_task() -> None:
    """Periodic health check task."""
    logger.debug("Running health check task")
    
    # Update internet availability state
    if _state:
        # Use config for interval, default to 5s if not set
        check_interval = _state.config.get("system", {}).get("internet_check_interval", 5)
        if time.time() - _state.last_internet_check > check_interval:
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

    # Check critical services (Router) - Self Healing
    await check_critical_services()

    # Check gateway health (Reporting only)
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
    
    # Staggered MCP server health checks
    from agent_runner.constants import CORE_MCP_SERVERS
    
    time_since_start = time.time() - _state.system_start_time if _state else 0.0
    
    # Startup window: Staggered checks at 5s, 15s, 60s
    if time_since_start < 60.0:
        # Determine which startup check we're at
        if time_since_start < 5.0:
            return  # Too early, skip
        elif 5.0 <= time_since_start < 15.0:
            # First check window (5-15s)
            check_time = 5.0
            last_check_key = "_startup_check_5s"
        elif 15.0 <= time_since_start < 60.0:
            # Second check window (15-60s)
            check_time = 15.0
            last_check_key = "_startup_check_15s"
        else:
            # Third check window (60s)
            check_time = 60.0
            last_check_key = "_startup_check_60s"
        
        # Check if we've already done this check
        last_check = getattr(_state, last_check_key, 0.0)
        if last_check > 0:
            return  # Already checked at this interval
        
        # Mark as checked
        setattr(_state, last_check_key, time.time())
        
        logger.info(f"🔄 Startup health check at {check_time}s ({time_since_start:.0f}s since start)")
        
        # Shorter timeout during startup (faster feedback)
        timeout = 10.0
        
        # Check all servers in parallel
        health_tasks = [
            check_mcp_server_health(server, timeout=timeout)
            for server in MCP_SERVERS.keys()
        ]
        
        results = await asyncio.gather(*health_tasks, return_exceptions=True)
        
        # Update health status
        for server, result in zip(MCP_SERVERS.keys(), results):
            if isinstance(result, Exception):
                _state.mcp_server_health[server] = {
                    "healthy": False,
                    "error": str(result),
                    "last_check": time.time()
                }
            else:
                _state.mcp_server_health[server] = {
                    "healthy": result.get("ok", False),
                    "error": result.get("error") if not result.get("ok") else None,
                    "last_check": result.get("last_check", time.time()),
                    "last_success": time.time() if result.get("ok") else _state.mcp_server_health.get(server, {}).get("last_success"),
                    "last_failure": time.time() if not result.get("ok") else _state.mcp_server_health.get(server, {}).get("last_failure")
                }
        
        # Log summary
        healthy_count = sum(1 for s in _state.mcp_server_health.values() if s.get("healthy"))
        logger.info(f"Startup health check ({check_time}s): {healthy_count}/{len(MCP_SERVERS)} servers healthy")
        
        # Set variables for compatibility with existing code
        healthy_servers = healthy_count
        disabled_servers = [s for s, h in _state.mcp_server_health.items() if not h.get("healthy")]
        core_disabled_servers = [s for s in disabled_servers if s in CORE_MCP_SERVERS]
    
    # Normal operation: Every 60 seconds
    else:
        # Check every 60 seconds
        check_interval = 60.0
        last_check_key = "_last_normal_health_check"
        last_check = getattr(_state, last_check_key, 0.0)
        
        if time.time() - last_check < check_interval:
            return  # Skip if checked recently
        
        setattr(_state, last_check_key, time.time())
        
        logger.debug("Running normal health check (every 60s)")
        
        # Normal timeout (15-20s)
        from agent_runner.constants import CORE_MCP_SERVERS
        health_tasks = []
        for server in MCP_SERVERS.keys():
            timeout = 20.0 if server in CORE_MCP_SERVERS else 15.0
            health_tasks.append(check_mcp_server_health(server, timeout=timeout))
        
        results = await asyncio.gather(*health_tasks, return_exceptions=True)
        
        # Update health status
        for server, result in zip(MCP_SERVERS.keys(), results):
            if isinstance(result, Exception):
                _state.mcp_server_health[server] = {
                    "healthy": False,
                    "error": str(result),
                    "last_check": time.time()
                }
            else:
                _state.mcp_server_health[server] = {
                    "healthy": result.get("ok", False),
                    "error": result.get("error") if not result.get("ok") else None,
                    "last_check": result.get("last_check", time.time()),
                    "last_success": time.time() if result.get("ok") else _state.mcp_server_health.get(server, {}).get("last_success"),
                    "last_failure": time.time() if not result.get("ok") else _state.mcp_server_health.get(server, {}).get("last_failure")
                }
        
        healthy_count = sum(1 for s in _state.mcp_server_health.values() if s.get("healthy"))
        logger.info(f"Normal health check: {healthy_count}/{len(MCP_SERVERS)} servers healthy")
        
        # Set variables for compatibility with existing code
        healthy_servers = healthy_count
        disabled_servers = [s for s, h in _state.mcp_server_health.items() if not h.get("healthy")]
        from agent_runner.constants import CORE_MCP_SERVERS
        core_disabled_servers = [s for s in disabled_servers if s in CORE_MCP_SERVERS]
    
    # [CORE SERVICE PROTECTION] Automatic recovery for core services
    if core_disabled_servers and _mcp_circuit_breaker and _state:
        # Check if enough time has passed since last recovery attempt
        last_recovery_key = "_core_service_last_recovery"
        last_recovery = getattr(_state, last_recovery_key, 0.0)
        now = time.time()
        
        if now - last_recovery >= CORE_SERVICE_AUTO_RECOVERY_INTERVAL:
            logger.info(f"🔄 Attempting automatic recovery for core services: {', '.join(core_disabled_servers)}")
            setattr(_state, last_recovery_key, now)
            
            for server in core_disabled_servers:
                try:
                    # Reset circuit breaker to allow retry
                    _mcp_circuit_breaker.reset(server)
                    logger.info(f"✅ Reset circuit breaker for core service '{server}' - attempting recovery")
                    
                    # Test the server with a lightweight call
                    from agent_runner.tools.mcp import tool_mcp_proxy
                    test_result = await tool_mcp_proxy(
                        _state,
                        server=server,
                        tool="tools/list",
                        arguments={},
                        bypass_circuit_breaker=False  # Use circuit breaker to track recovery
                    )
                    
                    if test_result.get("ok"):
                        logger.info(f"✅ Core service '{server}' recovered successfully!")
                        try:
                            from common.unified_tracking import track_health_event, EventSeverity
                            track_health_event(
                                event="core_service_recovered",
                                message=f"Core service '{server}' automatically recovered",
                                severity=EventSeverity.INFO,
                                component="health_monitor",
                                metadata={"server": server}
                            )
                        except Exception:
                            pass
                    else:
                        logger.warning(f"⚠️ Core service '{server}' recovery test failed: {test_result.get('error', 'Unknown')}")
                except Exception as e:
                    logger.error(f"Failed to recover core service '{server}': {e}", exc_info=True)
    
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
        # Core service failures are CRITICAL, non-core are HIGH
        from agent_runner.constants import CORE_MCP_SERVERS
        has_core_failures = any(s in CORE_MCP_SERVERS for s in disabled_servers)
        
        # Only notify if there are multiple disabled servers or critical ones
        if len(disabled_servers) > 1 or has_core_failures:
            # Use unified tracking if available
            try:
                from common.unified_tracking import track_health_event, EventSeverity, EventCategory
                severity = EventSeverity.CRITICAL if has_core_failures else EventSeverity.HIGH
                message = f"{len(disabled_servers)} MCP server(s) disabled"
                if has_core_failures:
                    core_list = [s for s in disabled_servers if s in CORE_MCP_SERVERS]
                    message += f" - CRITICAL: Core services down: {', '.join(core_list)}"
                
                track_health_event(
                    event="mcp_server_health_issues",
                    message=message,
                    severity=severity,
                    component="health_monitor",
                    metadata={
                        "disabled_servers": disabled_servers,
                        "core_disabled": core_disabled_servers,
                        "healthy_count": healthy_servers,
                        "has_core_failures": has_core_failures
                    }
                )
            except ImportError:
                # Fallback to old system
                notify_health(
                    title="MCP Server Health Issues",
                    message=f"{len(disabled_servers)} MCP server(s) disabled: {', '.join(disabled_servers)}",
                    source="health_monitor",
                    metadata={"disabled_servers": disabled_servers, "healthy_count": healthy_servers}
                )


    # Check for Zombie Processes (stuck CLI commands)
    await check_zombie_processes()


async def check_zombie_processes() -> None:
    """Scan for and terminate stuck MCP management processes (like curl/npx) running > 5 mins."""
    try:
        # Check for curl commands hitting the Agent Runner that are old
        # ps format: pid, elapsed time (fmt: [[dd-]hh:]mm:ss), command
        cmd = "ps -eo pid,etime,command | grep 'curl' | grep 'admin/mcp' | grep -v grep"
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        
        lines = stdout.decode().splitlines()
        for line in lines:
            parts = line.split(maxsplit=2)
            if len(parts) < 3: continue
            
            pid, etime, command = parts
            
            # Parse elapsed time to minutes
            minutes = 0
            try:
                if "-" in etime: # Days
                    days, rest = etime.split("-")
                    minutes += int(days) * 1440
                    etime = rest
                
                time_parts = [int(x) for x in etime.split(":")]
                if len(time_parts) == 3: # hh:mm:ss
                    minutes += time_parts[0]*60 + time_parts[1]
                elif len(time_parts) == 2: # mm:ss
                    minutes += time_parts[0]
            except:
                continue
                
            # THRESHOLD: 5 Minutes
            if minutes > 5:
                # Kill it
                logger.warning(f"ZOMBIE DETECTED: PID {pid} running for {etime} mins. Terminating.")
                kill_proc = await asyncio.create_subprocess_exec("kill", "-9", pid)
                await kill_proc.wait()
                
                # Notify
                try:
                    from common.unified_tracking import track_health_event, EventSeverity
                    track_health_event(
                        event="zombie_process_killed",
                        message=f"Terminated stuck process (PID {pid}, running {etime})",
                        severity=EventSeverity.HIGH,
                        component="health_monitor",
                        metadata={"command": command, "elapsed": etime}
                    )
                except Exception as e:
                    logger.debug(f"Error recording command execution: {e}")

    except Exception as e:
        logger.debug(f"Zombie check error: {e}")


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


async def get_detailed_health_report() -> Dict[str, Any]:
    """
    Generate a comprehensive, structured health report for system introspection.
    Returns topology, dependency status, and circuit breaker states.
    """
    gateway_url = GATEWAY_BASE
    if _state and _state.gateway_base:
        gateway_url = _state.gateway_base
        
    report = {
        "timestamp": time.time(),
        "status": "healthy", # optimistically
        "topology": {
            "name": "Agent Runner",
            "type": "Orchestrator",
            "dependencies": {
                "router": {"type": "service", "url": gateway_url, "critical": True},
                "database": {"type": "service", "url": "surrealdb:8000", "critical": True},
                "internet": {"type": "resource", "critical": False}
            },
            "components": {}
        }
    }
    
    # 1. Check MCP Servers & Gather Tools
    mcp_status = {}
    total_mcp = 0
    healthy_mcp = 0
    
    # [NEW] Access Engine for Tool Registry
    # Use Registry to avoid cycle
    try:
        from agent_runner.agent_runner import get_shared_engine
        engine = get_shared_engine()
        # Ensure executor is initialized
        mcp_tool_cache = getattr(engine.executor, "mcp_tool_cache", {})
        native_defs = getattr(engine.executor, "tool_definitions", [])
    except Exception:
        mcp_tool_cache = {}
        native_defs = []
        
    # Add Native Tools to topology first
    native_tool_names = [t.get("function", {}).get("name") for t in native_defs]
    report["topology"]["components"]["agent_runner"] = {
        "type": "native",
        "status": "online",
        "tools": native_tool_names
    }
    
    if _mcp_circuit_breaker:
        cb_stats = _mcp_circuit_breaker.get_status()
    else:
        cb_stats = {}
    
    for name, config in MCP_SERVERS.items():
        total_mcp += 1
        # Check breaker status
        breaker_info = cb_stats.get(name, {})
        is_open = breaker_info.get("state") == "open"
        
        status = "healthy"
        if is_open:
            status = "unhealthy"
            # [FIX] If internet is okay, force a probe/reset for critical LLM services
            if internet_ok and name == "xai":
                 # Aggressively reset the breaker state if it seems stuck
                 status = "recovering"
                 if _mcp_circuit_breaker:
                     _mcp_circuit_breaker.reset(name)
        
        if status == "healthy": healthy_mcp += 1
        
        # [NEW] Get discovered tools for this server
        server_tools_raw = mcp_tool_cache.get(name, [])
        tool_names = [t.get("function", {}).get("name") for t in server_tools_raw]
        
        mcp_status[name] = {
            "type": "mcp_server",
            "status": status,
            "config": config,
            "circuit_breaker": {
                 "state": breaker_info.get("state", "closed"),
                 "failures": breaker_info.get("failures", 0),
                 "last_failure": breaker_info.get("last_failure_time"),
                 "consecutive_failures": breaker_info.get("consecutive_failures", 0)
            },
            "tools": tool_names  # [NEW] Expose available functions
        }
        
    report["topology"]["components"]["mcp_servers"] = mcp_status
    report["metrics"] = {
        "mcp_total": total_mcp,
        "mcp_healthy": healthy_mcp
    }
    
    # 2. Check Dependencies
    # Internet
    internet_ok = False
    if _state:
        internet_ok = _state.internet_available
    report["topology"]["dependencies"]["internet"]["status"] = "online" if internet_ok else "offline"
    
    # Router
    router_health = await check_gateway_health()
    report["topology"]["dependencies"]["router"]["status"] = "online" if router_health.get("ok") else "offline"
    if not router_health.get("ok"):
        report["status"] = "degraded"
        
    # Database (Surreal) details if possible
    # We can infer from project-memory status
    if "project-memory" in MCP_SERVERS:
        pm_status = mcp_status.get("project-memory", {}).get("status")
        report["topology"]["dependencies"]["database"]["status"] = "online" if pm_status == "healthy" else "unknown"
        
    # Overall Status Calculation
    if healthy_mcp < total_mcp:
        report["status"] = "degraded" 
        # If critical ones are down, maybe unhealthy?
    if not router_health.get("ok"):
        report["status"] = "unhealthy"

    # 3. Scheduler & Task Awareness [NEW]
    try:
        from agent_runner.background_tasks import get_task_manager
        tm = get_task_manager()
        task_status = tm.get_status()
        
        # Simplify for the report
        tasks_list = []
        for t_name, t_info in task_status.get("tasks", {}).items():
             # Calculate human friendly next run
             next_run_s = t_info.get("seconds_until_next")
             next_run_str = f"{int(next_run_s)}s" if next_run_s is not None else "N/A"
             
             # Format Schedule String
             if t_info.get("type") == "periodic":
                 sched = f"Every {t_info.get('interval')}s"
             elif t_info.get("type") == "scheduled":
                 sched = f"Cron: {t_info.get('schedule')}"
             else:
                 sched = "Active"

             tasks_list.append({
                 "name": t_name,
                 "type": t_info.get("type"),
                 "schedule": sched,
                 "next_run": next_run_str,
                 "status": "running" if t_info.get("running") else "idle"
             })
             
        report["scheduler"] = {
            "status": "online" if task_status.get("running") else "stopped",
            "active_tasks": len(tasks_list),
            "tasks": tasks_list
        }
    except Exception as e:
        report["scheduler"] = {"status": "unknown", "error": str(e)}
        
    return report

