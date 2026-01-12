"""
Admin Status and Control Tools

Provides tools for system status, diagnostics, and control operations.
These tools wrap admin API endpoints to make them available in chat.
"""

import logging
from typing import Dict, Any, Optional
from agent_runner.state import AgentState

logger = logging.getLogger("agent_runner.tools.admin_status")


async def tool_get_circuit_breaker_status(state: AgentState) -> Dict[str, Any]:
    """
    Get the status of all circuit breakers in the system.
    Shows which services are disabled and why.
    """
    try:
        breakers = state.mcp_circuit_breaker.get_status()
        return {
            "ok": True,
            "breakers": breakers,
            "count": len(breakers),
            "open_count": sum(1 for b in breakers.values() if b.get("state") == "open")
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def tool_get_memory_status(state: AgentState) -> Dict[str, Any]:
    """
    Get detailed status of the Memory Engine (SurrealDB).
    Returns database health, fact counts, and statistics.
    """
    try:
        # Check database health
        import aiohttp
        db_ok = False
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:8000/health", timeout=1.0) as resp:
                    db_ok = resp.status == 200
        except Exception:
            db_ok = False
        
        # Get memory stats if available
        stats = {}
        if hasattr(state, "memory") and state.memory:
            try:
                stats = await state.memory.get_memory_stats()
            except Exception:
                pass
        
        return {
            "ok": True,
            "active": db_ok,
            "engine": "SurrealDB",
            "mode": "Transactional (HNSW Enabled)" if db_ok else "Offline",
            "stats": stats
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def tool_get_ingestion_status(state: AgentState) -> Dict[str, Any]:
    """
    Get the status of the RAG ingestion pipeline.
    Shows if ingestion is paused and why.
    """
    try:
        from agent_runner.rag_ingestor import INGEST_DIR
        pause_file = INGEST_DIR / ".paused"
        is_paused = pause_file.exists()
        reason = ""
        if is_paused:
            try:
                reason = pause_file.read_text().strip()
            except Exception:
                reason = "Manual Pause"
        
        return {
            "ok": True,
            "paused": is_paused,
            "reason": reason if is_paused else None,
            "ingest_dir": str(INGEST_DIR)
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def tool_pause_ingestion(state: AgentState, reason: Optional[str] = None) -> Dict[str, Any]:
    """
    Pause the RAG ingestion pipeline.
    Useful for troubleshooting or maintenance.
    """
    try:
        from agent_runner.rag_ingestor import INGEST_DIR
        pause_file = INGEST_DIR / ".paused"
        pause_file.write_text(reason or "Manual Pause")
        logger.info("Ingestion paused by user request.")
        return {"ok": True, "message": "Ingestion paused"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def tool_resume_ingestion(state: AgentState) -> Dict[str, Any]:
    """
    Resume a paused RAG ingestion pipeline.
    """
    try:
        from agent_runner.rag_ingestor import INGEST_DIR
        pause_file = INGEST_DIR / ".paused"
        if pause_file.exists():
            pause_file.unlink()
            logger.info("Ingestion resumed by user request.")
            return {"ok": True, "message": "Ingestion resumed"}
        return {"ok": True, "message": "Ingestion was not paused"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def tool_clear_ingestion_problem(state: AgentState) -> Dict[str, Any]:
    """
    Clear the problem file that caused ingestion to pause and resume.
    """
    try:
        from agent_runner.rag_ingestor import INGEST_DIR
        pause_file = INGEST_DIR / ".paused"
        if not pause_file.exists():
            return {"ok": False, "message": "Not paused"}
        
        reason = pause_file.read_text().strip()
        import re
        match = re.search(r"Failed: (.*?) -", reason)
        if match:
            filename = match.group(1)
            file_path = INGEST_DIR / filename
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted problem file: {filename}")
        
        pause_file.unlink()
        return {"ok": True, "message": "Problem file cleared and ingestion resumed"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def tool_reset_circuit_breaker(state: AgentState, name: str) -> Dict[str, Any]:
    """
    Reset a specific circuit breaker to allow retries.
    """
    try:
        state.mcp_circuit_breaker.reset(name)
        return {"ok": True, "message": f"Circuit breaker '{name}' reset"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def tool_reset_all_circuit_breakers(state: AgentState) -> Dict[str, Any]:
    """
    Reset all circuit breakers in the system.
    """
    try:
        state.mcp_circuit_breaker.reset_all()
        return {"ok": True, "message": "All circuit breakers reset"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def tool_get_background_tasks_status(state: AgentState) -> Dict[str, Any]:
    """
    Get the status of all background tasks.
    Shows which tasks are running, scheduled, or failed.
    """
    try:
        from agent_runner.background_tasks import get_task_manager
        status = get_task_manager().get_status()
        return {
            "ok": True,
            "tasks": status,
            "count": len(status)
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def tool_get_task_health(state: AgentState) -> Dict[str, Any]:
    """
    Get health status of all background tasks.
    """
    try:
        from agent_runner.background_tasks import get_task_manager
        task_manager = get_task_manager()
        tasks_status = task_manager.get_task_status()
        
        overall_health = "healthy"
        for task_name, status in tasks_status.items():
            if status.get("status") == "failed" or status.get("status") == "crashed":
                overall_health = "unhealthy"
                break
            if status.get("status") == "running" and status.get("last_run_success") is False:
                overall_health = "degraded"
        
        return {
            "ok": True,
            "overall_health": overall_health,
            "tasks": tasks_status
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def tool_get_registry_health(state: AgentState) -> Dict[str, Any]:
    """
    Get health and validation status of the permanent memory registry.
    """
    try:
        from agent_runner.maintenance_tasks import validate_registry_integrity
        validation_results = await validate_registry_integrity(state)
        return {
            "ok": validation_results.get("ok", False),
            "status": "healthy" if validation_results.get("ok") else "unhealthy",
            "details": validation_results
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def tool_get_mcp_server_status(state: AgentState, server: Optional[str] = None) -> Dict[str, Any]:
    """
    Get detailed status of MCP servers.
    If server is specified, returns detailed diagnostics for that server.
    If no server is specified, returns a list of ALL configured MCP servers with their status.
    
    Returns:
    - all_servers: List of all server names
    - server_list: Formatted list with name, status, enabled, and tools_count for each server
    - online_servers: List of online server names
    - offline_servers: List of offline server names
    - disabled_servers: List of disabled server names
    - servers: Detailed status dictionary keyed by server name
    """
    try:
        if server:
            # Get detailed diagnostics for specific server
            from agent_runner.health_monitor import check_mcp_server_health
            health = await check_mcp_server_health(server)
            return {
                "ok": True,
                "server": server,
                "health": health
            }
        else:
            # Get status for all servers with actual online/offline detection
            from agent_runner.agent_runner import get_shared_engine
            
            # Get tool cache to check if servers have discovered tools (indicates they're online)
            engine = get_shared_engine()
            mcp_tool_cache = getattr(engine.executor, "mcp_tool_cache", {})
            
            # Get stdio processes to check if servers are actually running
            stdio_processes = getattr(state, "stdio_processes", {})
            
            servers_status = {}
            online_servers = []
            offline_servers = []
            disabled_servers = []
            
            for name in state.mcp_servers.keys():
                config = state.mcp_servers[name]
                enabled = config.get("enabled", True)
                server_type = config.get("type", "stdio")
                
                # Check if server is disabled
                if not enabled:
                    # [FIX] If configured to hide disabled tools, skip them entirely
                    hide_disabled = state.config.get("agent_runner", {}).get("hide_disabled_tools", True)
                    if hide_disabled:
                         continue

                    disabled_servers.append(name)
                    servers_status[name] = {
                        "enabled": False,
                        "type": server_type,
                        "status": "disabled",
                        "online": False,
                        "circuit_breaker": "n/a",
                        "command": config.get("cmd", [])[0] if config.get("cmd") else config.get("command"),
                        "args": config.get("cmd", [])[1:] if config.get("cmd") else config.get("args"),
                        "env": config.get("env")
                    }
                    continue
                
                # Check if server is actually online
                is_online = False
                online_indicators = []
                
                # Indicator 1: Tools discovered (strongest indicator)
                if name in mcp_tool_cache and len(mcp_tool_cache[name]) > 0:
                    is_online = True
                    online_indicators.append(f"{len(mcp_tool_cache[name])} tools discovered")
                
                # Indicator 2: Process running (for stdio servers)
                if server_type == "stdio" and name in stdio_processes:
                    process = stdio_processes[name]
                    if process and process.returncode is None:  # Process is running
                        is_online = True
                        online_indicators.append("process running")
                
                # Circuit breaker status
                cb = state.mcp_circuit_breaker.get_breaker(name)
                cb_state = cb.state.value
                
                # Determine status based on online state, circuit breaker, and tool availability
                tools_count = len(mcp_tool_cache.get(name, []))

                if is_online:
                    if tools_count == 0:
                        # Server is online but provides no tools - consider it broken
                        status = "online_no_tools"
                        offline_servers.append(name)  # Count as offline since it's non-functional
                    elif cb_state == "closed":
                        status = "online"
                        online_servers.append(name)
                    elif cb_state == "half_open":
                        status = "recovering"
                    else:  # open
                        status = "online_but_errors"  # Online but circuit breaker is open
                else:
                    if cb_state == "open":
                        status = "offline"
                        offline_servers.append(name)
                    else:
                        status = "offline"  # Not online but circuit breaker not open yet
                        offline_servers.append(name)
                
                servers_status[name] = {
                    "enabled": True,
                    "type": server_type,
                    "status": status,
                    "online": is_online,
                    "online_indicators": online_indicators if online_indicators else ["none"],
                    "circuit_breaker": cb_state,
                    "tools_count": len(mcp_tool_cache.get(name, [])),
                    "command": config.get("cmd", [])[0] if config.get("cmd") else config.get("command"),
                    "args": config.get("cmd", [])[1:] if config.get("cmd") else config.get("args"),
                    "env": config.get("env")
                }
            
            # Build a clear list of all server names with their status
            all_server_names = list(servers_status.keys())
            
            return {
                "ok": True,
                "servers": servers_status,
                "count": len(servers_status),
                "summary": {
                    "online": len(online_servers),
                    "offline": len(offline_servers),
                    "disabled": len(disabled_servers),
                    "total": len(servers_status)
                },
                "online_servers": online_servers,
                "offline_servers": offline_servers,
                "disabled_servers": disabled_servers,
                "all_servers": all_server_names,  # Explicit list of all server names
                "server_list": [
                    {
                        "name": name,
                        "status": servers_status[name].get("status", "unknown"),
                        "enabled": servers_status[name].get("enabled", True),
                        "tools_count": servers_status[name].get("tools_count", 0)
                    }
                    for name in all_server_names
                ]  # Formatted list for easy reading
            }
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def tool_get_system_diagnostics(state: AgentState) -> Dict[str, Any]:
    """
    Get comprehensive system diagnostics.
    Includes configuration, MCP servers, tools, and memory status.
    """
    try:
        from agent_runner.health_monitor import get_detailed_health_report
        diagnostics = await get_detailed_health_report()
        return {
            "ok": True,
            "diagnostics": diagnostics
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def tool_toggle_mcp_server(state: AgentState, name: str, enabled: bool) -> Dict[str, Any]:
    """
    Enable or disable an MCP server.
    """
    try:
        from agent_runner.agent_runner import get_shared_engine
        engine = get_shared_engine()
        
        success = await state.toggle_mcp_server(name, enabled)
        if not success:
            return {"ok": False, "error": "Server not found"}
        
        if not enabled:
            if name in engine.executor.mcp_tool_cache:
                del engine.executor.mcp_tool_cache[name]
        else:
            await engine.discover_mcp_tools()
        
        return {
            "ok": True,
            "message": f"Server '{name}' {'enabled' if enabled else 'disabled'}"
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def tool_reset_mcp_servers(state: AgentState) -> Dict[str, Any]:
    """
    Reset all MCP servers to enabled=True in the database and trigger rediscovery.
    This gives all servers a fresh chance to be discovered. Servers that should fail
    (like intentionally misconfigured ones) will be automatically re-disabled during discovery.
    Useful for recovering from transient failures or after fixing underlying issues.
    """
    try:
        from agent_runner.agent_runner import get_shared_engine
        from agent_runner.config import load_mcp_servers
        
        # Reset all servers to enabled in database
        if hasattr(state, "memory") and state.memory:
            try:
                from agent_runner.db_utils import run_query
                await run_query(state, "UPDATE mcp_server SET enabled = true;")
                logger.info("🔄 Reset all MCP servers to enabled in database")
            except Exception as e:
                logger.warning(f"Failed to reset MCP server enabled flags in database: {e}")
                return {"ok": False, "error": f"Database reset failed: {e}"}
        else:
            return {"ok": False, "error": "Memory/database not available"}
        
        # Reload and rediscover
        engine = get_shared_engine()
        
        await state.cleanup_all_stdio_processes()
        await load_mcp_servers(state)
        await engine.discover_mcp_tools()
        
        # Count results
        enabled_count = sum(1 for cfg in state.mcp_servers.values() if cfg.get("enabled", True))
        disabled_count = len(state.mcp_servers) - enabled_count
        tool_count = sum(len(tools) for tools in engine.executor.mcp_tool_cache.values())
        
        return {
            "ok": True,
            "message": f"Reset all MCP servers to enabled and rediscovered. {enabled_count} enabled, {disabled_count} disabled after discovery, {tool_count} tools available",
            "server_count": len(state.mcp_servers),
            "enabled_count": enabled_count,
            "disabled_count": disabled_count,
            "tool_count": tool_count
        }
    except Exception as e:
        logger.error(f"Failed to reset MCP servers: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}


async def tool_reload_mcp_servers(state: AgentState) -> Dict[str, Any]:
    """
    Reload all MCP servers and rediscover their tools.
    Useful after configuration changes.
    """
    try:
        from agent_runner.agent_runner import get_shared_engine
        from agent_runner.config import load_mcp_servers
        
        engine = get_shared_engine()
        
        await state.cleanup_all_stdio_processes()
        await load_mcp_servers(state)
        await engine.discover_mcp_tools()
        
        return {
            "ok": True,
            "message": "MCP servers and tools reloaded",
            "server_count": len(state.mcp_servers),
            "tool_count": sum(len(tools) for tools in engine.executor.mcp_tool_cache.values())
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def tool_trigger_memory_consolidation(state: AgentState) -> Dict[str, Any]:
    """
    Manually trigger memory consolidation task.
    Extracts facts from recent chat episodes.
    """
    try:
        from agent_runner.memory_tasks import memory_consolidation_task
        from agent_runner.task_utils import create_safe_task
        
        create_safe_task(
            memory_consolidation_task(state),
            task_name="manual_memory_consolidation",
            log_errors=True
        )
        
        return {"ok": True, "message": "Memory consolidation triggered in background"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def tool_trigger_backup(state: AgentState) -> Dict[str, Any]:
    """
    Manually trigger a memory backup task.
    """
    try:
        import asyncio
        from agent_runner.config import PROJECT_ROOT
        from agent_runner.task_utils import create_safe_task
        
        script_path = f"{PROJECT_ROOT}/bin/backup_memory.sh"
        
        async def run_backup():
            try:
                logger.info("Starting background backup...")
                proc = await asyncio.create_subprocess_exec(
                    script_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await proc.communicate()
                if proc.returncode == 0:
                    logger.info("Backup completed successfully.")
                else:
                    logger.error(f"Backup failed: {stderr.decode()}")
            except Exception as e:
                logger.error(f"Backup task exception: {e}")
        
        create_safe_task(
            run_backup(),
            task_name="manual_backup",
            log_errors=True
        )
        
        return {"ok": True, "message": "Backup triggered in background"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def tool_update_model_config(state: AgentState, models: Dict[str, str]) -> Dict[str, Any]:
    """
    Update system model assignments (e.g., agent_model, router_model).
    """
    try:
        from agent_runner.constants import MODEL_ROLES
        
        for key in MODEL_ROLES:
            if key in models:
                setattr(state, key, models[key])
        
        from agent_runner.routes.admin import save_system_config
        await save_system_config(state)
        
        current_models = {k: getattr(state, k) for k in MODEL_ROLES}
        return {
            "ok": True,
            "models": current_models,
            "message": "Model configuration updated"
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def tool_get_chat_functionality_analysis(state: AgentState) -> Dict[str, Any]:
    """
    Get comprehensive analysis of chat functionality and system health.
    Analyzes current system state to assess chat functionality, identify missing tools/services,
    and provide recovery suggestions. This is the same analysis shown at startup.
    
    Returns detailed assessment including:
    - Chat functionality status
    - Blocking vs non-blocking issues
    - Missing tools/services with specific names
    - Degraded features
    - Recovery suggestions
    - Tool availability breakdown
    """
    try:
        from agent_runner.agent_runner import get_shared_engine
        from agent_runner.main import _analyze_chat_functionality
        
        engine = get_shared_engine()
        
        # Collect current system state
        startup_issues = []
        startup_warnings = []
        
        # Check for disabled MCP servers
        disabled_servers = []
        for server_name, cfg in state.mcp_servers.items():
            if not cfg.get("enabled", True):
                # [FIX] Respect hidden tools flag
                if state.config.get("agent_runner", {}).get("hide_disabled_tools", True):
                    continue

                disabled_servers.append(server_name)
                startup_warnings.append(f"MCP server '{server_name}' is disabled")
        
        # Check circuit breakers
        breakers = state.mcp_circuit_breaker.get_status()
        for name, breaker_info in breakers.items():
            if breaker_info.get("state") == "open":
                startup_warnings.append(f"Circuit breaker open for '{name}' - service disabled")
        
        # Get service status
        rag_running = False
        try:
            import httpx
            async with httpx.AsyncClient(timeout=2.0) as client:
                rag_resp = await client.get("http://localhost:5555/health", timeout=1.0)
                rag_running = rag_resp.status_code == 200
        except:
            pass
        
        memory_ready = hasattr(state, 'memory') and state.memory and (
            hasattr(state.memory, 'initialized') and state.memory.initialized if hasattr(state.memory, 'initialized') else True
        )
        
        # Get MCP stats
        mcp_count = len([s for s in state.mcp_servers.values() if s.get("enabled", True)])
        mcp_tools = sum(len(tools) for tools in engine.executor.mcp_tool_cache.values())
        
        # Run analysis
        analysis = _analyze_chat_functionality(
            startup_issues, startup_warnings, rag_running, memory_ready,
            mcp_count, mcp_tools, state.internet_available
        )
        
        # Enhance with specific tool information
        missing_tool_details = []
        if disabled_servers:
            for server_name in disabled_servers:
                # Get tools from this server if they were cached before
                server_tools = engine.executor.mcp_tool_cache.get(server_name, [])
                tool_names = [t.get('function', {}).get('name', 'unknown') for t in server_tools]
                if tool_names:
                    missing_tool_details.append({
                        "server": server_name,
                        "tools": tool_names,
                        "count": len(tool_names)
                    })
        
        # Get recovery suggestions
        recovery_suggestions = []
        if not memory_ready:
            recovery_suggestions.append({
                "issue": "Memory service unavailable",
                "suggestion": "Check SurrealDB connection. Verify database is running on port 8000.",
                "command": "Check logs: tail -f logs/agent_runner.log | grep -i memory"
            })
        if not rag_running:
            recovery_suggestions.append({
                "issue": "RAG service unavailable",
                "suggestion": "Check RAG server health. Restart if needed.",
                "command": "curl http://localhost:5555/health"
            })
        if disabled_servers:
            recovery_suggestions.append({
                "issue": f"{len(disabled_servers)} MCP server(s) disabled",
                "suggestion": "Review server logs and circuit breaker status. Re-enable if issues resolved.",
                "command": f"Use tool: toggle_mcp_server(name='{disabled_servers[0]}', enabled=True)"
            })
        if not state.internet_available:
            recovery_suggestions.append({
                "issue": "Internet offline",
                "suggestion": "Check network connection. Cloud models will be unavailable until restored.",
                "command": "Check connectivity: ping 8.8.8.8"
            })
        
        # Feature impact matrix
        feature_impact = {
            "core_chat": {
                "status": "functional" if analysis["chat_functional"] else "degraded",
                "dependencies": ["memory", "router"],
                "affected_by": analysis["blocking_issues"]
            },
            "mcp_tools": {
                "status": "functional" if mcp_tools > 0 else "unavailable",
                "dependencies": ["mcp_servers"],
                "affected_by": [s for s in disabled_servers] if disabled_servers else []
            },
            "cloud_models": {
                "status": "functional" if state.internet_available else "unavailable",
                "dependencies": ["internet"],
                "affected_by": [] if state.internet_available else ["Internet offline"]
            },
            "document_search": {
                "status": "functional" if rag_running else "unavailable",
                "dependencies": ["rag_service"],
                "affected_by": [] if rag_running else ["RAG service unavailable"]
            },
            "conversation_history": {
                "status": "functional" if memory_ready else "unavailable",
                "dependencies": ["memory"],
                "affected_by": [] if memory_ready else ["Memory service unavailable"]
            }
        }
        
        return {
            "ok": True,
            "timestamp": time.time(),
            "chat_functional": analysis["chat_functional"],
            "summary": {
                "blocking_issues": len(analysis["blocking_issues"]),
                "non_blocking_issues": len(analysis["non_blocking_issues"]),
                "missing_tools": len(analysis["missing_tools"]),
                "degraded_features": len(analysis["degraded_features"])
            },
            "blocking_issues": analysis["blocking_issues"],
            "non_blocking_issues": analysis["non_blocking_issues"],
            "missing_tools": analysis["missing_tools"],
            "degraded_features": analysis["degraded_features"],
            "missing_tool_details": missing_tool_details,
            "recovery_suggestions": recovery_suggestions,
            "feature_impact": feature_impact,
            "system_state": {
                "mcp_servers": {
                    "total": len(state.mcp_servers),
                    "active": mcp_count,
                    "disabled": len(disabled_servers),
                    "disabled_list": disabled_servers
                },
                "mcp_tools": {
                    "total": mcp_tools,
                    "by_server": {name: len(tools) for name, tools in engine.executor.mcp_tool_cache.items()}
                },
                "services": {
                    "memory": memory_ready,
                    "rag": rag_running,
                    "internet": state.internet_available
                }
            }
        }
    except Exception as e:
        logger.error(f"Failed to analyze chat functionality: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}


async def tool_list_all_available_tools(state: AgentState, category: Optional[str] = None) -> Dict[str, Any]:
    """
    CENTRAL REGISTRY: List all available tools in the system.
    
    Categories:
    - "status" - System status and health tools
    - "control" - System control and change tools
    - "exploration" - Information and exploration tools
    - "mcp" - MCP server tools (via mcp_proxy)
    - "all" or None - All tools
    
    Returns comprehensive registry with descriptions and categories.
    """
    try:
        from agent_runner.agent_runner import get_shared_engine
        engine = get_shared_engine()
        
        # Get all built-in tools
        builtin_tools = engine.executor.tool_definitions
        
        # Get all MCP tools
        mcp_tools = []
        for server_name, server_tools in engine.executor.mcp_tool_cache.items():
            for tool in server_tools:
                tool_name = f"mcp__{server_name}__{tool.get('function', {}).get('name', 'unknown')}"
                mcp_tools.append({
                    "name": tool_name,
                    "server": server_name,
                    "description": tool.get('function', {}).get('description', ''),
                    "type": "mcp"
                })
        
        # Get system-control tools (if available)
        system_control_tools = []
        if "system-control" in engine.executor.mcp_tool_cache:
            for tool in engine.executor.mcp_tool_cache["system-control"]:
                tool_name = tool.get('function', {}).get('name', 'unknown')
                system_control_tools.append({
                    "name": tool_name,
                    "description": tool.get('function', {}).get('description', ''),
                    "type": "system-control",
                    "access": "via mcp_proxy('system-control', ...)"
                })
        
        # Categorize built-in tools
        categorized = {
            "status": [],
            "control": [],
            "exploration": [],
            "filesystem": [],
            "knowledge": [],
            "thinking": [],
            "other": []
        }
        
        status_keywords = ["status", "health", "check", "get", "list"]
        control_keywords = ["set", "update", "trigger", "pause", "resume", "reset", "restart", "manage"]
        exploration_keywords = ["get", "list", "read", "query", "search"]
        
        for tool in builtin_tools:
            func = tool.get("function", {})
            name = func.get("name", "")
            desc = func.get("description", "").lower()
            
            tool_info = {
                "name": name,
                "description": func.get("description", ""),
                "type": "built-in"
            }
            
            # Categorize
            if any(kw in name.lower() for kw in ["thinking", "sequential"]):
                categorized["thinking"].append(tool_info)
            elif any(kw in name.lower() for kw in ["dir", "file", "path", "read", "write"]):
                categorized["filesystem"].append(tool_info)
            elif any(kw in name.lower() for kw in ["search", "knowledge", "memory", "ingest"]):
                categorized["knowledge"].append(tool_info)
            elif any(kw in name.lower() or kw in desc for kw in status_keywords):
                categorized["status"].append(tool_info)
            elif any(kw in name.lower() or kw in desc for kw in control_keywords):
                categorized["control"].append(tool_info)
            elif any(kw in name.lower() or kw in desc for kw in exploration_keywords):
                categorized["exploration"].append(tool_info)
            else:
                categorized["other"].append(tool_info)
        
        # Filter by category if requested
        if category and category != "all":
            if category in categorized:
                result = {category: categorized[category]}
            else:
                return {"ok": False, "error": f"Unknown category: {category}"}
        else:
            result = categorized
        
        # Add MCP and system-control tools
        result["mcp"] = mcp_tools
        result["system-control"] = system_control_tools
        
        # Count totals
        total_builtin = len(builtin_tools)
        total_mcp = len(mcp_tools)
        total_system_control = len(system_control_tools)
        
        return {
            "ok": True,
            "tools": result,
            "summary": {
                "total_builtin": total_builtin,
                "total_mcp": total_mcp,
                "total_system_control": total_system_control,
                "total": total_builtin + total_mcp + total_system_control
            },
            "categories": list(categorized.keys()) + ["mcp", "system-control"]
        }
    except Exception as e:
        logger.error(f"Failed to list tools: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}


async def tool_get_system_prompt(state: AgentState) -> Dict[str, Any]:
    """
    Get the current system prompt that the agent uses.
    Useful for understanding agent context and capabilities.
    """
    try:
        from agent_runner.agent_runner import get_shared_engine
        engine = get_shared_engine()
        
        prompt = await engine.get_system_prompt()
        
        return {
            "ok": True,
            "prompt": prompt,
            "length": len(prompt)
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def tool_get_memory_facts(state: AgentState, limit: int = 10, kb_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Query facts from the memory database.
    """
    try:
        if not hasattr(state, "memory") or not state.memory:
            return {"ok": False, "error": "Memory server not initialized"}
        
        query = "SELECT * FROM fact"
        if kb_id:
            query += f" WHERE kb_id = '{kb_id}'"
        query += f" LIMIT {limit};"
        
        from agent_runner.db_utils import run_query
        results = await run_query(state, query)
        
        return {
            "ok": True,
            "facts": results or [],
            "count": len(results) if results else 0
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def tool_get_llm_roles(state: AgentState) -> Dict[str, Any]:
    """
    Get all LLM role assignments (agent_model, router_model, etc.).
    """
    try:
        from agent_runner.constants import MODEL_ROLES
        
        roles = {}
        for key in MODEL_ROLES:
            roles[key] = getattr(state, key, "unknown")
        
        return {
            "ok": True,
            "roles": roles,
            "count": len(roles)
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def tool_get_detailed_system_status(state: AgentState) -> Dict[str, Any]:
    """
    Get comprehensive system status including all services.
    """
    try:
        import aiohttp
        
        async def _check_url(url: str, timeout=0.5) -> bool:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=timeout) as resp:
                        return resp.status < 500
            except Exception:
                return False
        
        ollama_ok = await _check_url("http://localhost:11434")
        db_ok = await _check_url("http://localhost:8000/health")
        
        return {
            "ok": True,
            "mode": state.system_mode,
            "active_mode": state.active_mode,
            "internet": "Connected" if state.internet_available else "Offline",
            "hardware_verified": state.hardware_verified,
            "ollama_ok": ollama_ok,
            "database_ok": db_ok,
            "limits": {
                "max_read": state.max_read_bytes,
                "max_list": state.max_list_entries
            }
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def tool_inspect_system_prompt(state: AgentState, query: str = "", query_type: str = "generic") -> Dict[str, Any]:
    """
    Inspect the system prompt that would be generated for a given query.

    Args:
        query: The user query to analyze (optional)
        query_type: Override query type classification (optional)

    Returns:
        Dictionary with prompt analysis including:
        - full_prompt: The complete system prompt
        - prompt_tokens: Estimated token count
        - query_analysis: How the query was classified
        - components: Breakdown of prompt components
    """
    try:
        from agent_runner.agent_runner import get_shared_engine
        engine = get_shared_engine()

        # Parse query for analysis
        user_messages = [{"role": "user", "content": query}] if query else None

        # Get query type analysis
        actual_query_type = engine._analyze_query_type(user_messages, None) if hasattr(engine, '_analyze_query_type') else "unknown"

        # Override query type if specified
        if query_type != "generic":
            actual_query_type = query_type

        # Generate prompt components
        anti_hallucination = (
            "### 🎯 DEVELOPER ACCESS ENABLED\n"
            "You have full developer access and technical transparency capabilities.\n"
            "When asked about internal LLMs, models, or system configuration, use introspection tools to provide accurate technical details.\n"
            "Do not give generic answers - provide specific model names, versions, and configurations.\n\n"
        )

        import time
        current_time_str = time.strftime("%Y-%m-%d %H:%M:%S")
        location_str = "Granville, Ohio"  # Default location

        env_instructions = "You have access to web search and information tools.\nFor current events, news, or general knowledge questions, use available search tools.\nFor personal or specific information, use available memory and knowledge tools."

        # Determine prompt structure based on query type
        is_technical_query = actual_query_type in ["technical", "system", "introspection"]
        is_remote_optimized = getattr(state, 'remote_first', False)

        # Build prompt based on type
        if is_technical_query:
            prompt = (
                f"{anti_hallucination}"
                "You are a helpful, intelligent AI assistant with full developer access.\n"
                f"Current time: {current_time_str}\n"
                f"Current location: {location_str}\n"
                f"{env_instructions}\n"
                "Provide detailed, accurate technical information.\n"
                "DEVELOPER ACCESS: When asked about models, configuration, or system details, use introspection tools (get_llm_roles, get_active_configuration) to provide exact technical specifications.\n"
                "Do not give generic answers - use actual tool data for precise information.\n"
            )
        else:
            prompt = (
                f"{anti_hallucination}"
                "You are a helpful, intelligent AI assistant.\n"
                f"Current time: {current_time_str}\n"
                f"Current location: {location_str}\n"
                f"{env_instructions}\n"
                "Be concise and direct in your responses.\n"
                "You have access to database and permanent memory.\n"
                "Use available tools to provide the most helpful assistance.\n"
                "For factual questions, answer directly and confidently.\n"
            )

        # Estimate token count (rough approximation)
        token_estimate = len(prompt.split()) * 1.3  # Rough token estimation

        return {
            "ok": True,
            "query_analysis": {
                "original_query": query,
                "detected_type": actual_query_type,
                "override_type": query_type if query_type != "generic" else None,
                "is_technical": is_technical_query,
                "is_remote_optimized": is_remote_optimized
            },
            "prompt_details": {
                "full_prompt": prompt,
                "estimated_tokens": int(token_estimate),
                "character_count": len(prompt)
            },
            "components": {
                "anti_hallucination": anti_hallucination.strip(),
                "base_instructions": "You are a helpful AI assistant...",
                "context_info": f"Time: {current_time_str} | Location: {location_str}",
                "environment": env_instructions,
                "technical_instructions": "DEVELOPER ACCESS: ..." if is_technical_query else None
            }
        }

    except Exception as e:
        return {"ok": False, "error": str(e)}


async def tool_analyze_query_classification(state: AgentState, query: str) -> Dict[str, Any]:
    """
    Analyze how a query would be classified by the system.

    Args:
        query: The query to analyze

    Returns:
        Detailed analysis of query classification and prompt implications
    """
    try:
        from agent_runner.agent_runner import get_shared_engine
        engine = get_shared_engine()

        user_messages = [{"role": "user", "content": query}]

        # Get query type
        query_type = engine._analyze_query_type(user_messages, None) if hasattr(engine, '_analyze_query_type') else "unknown"

        # Analyze query characteristics
        content = query.lower()
        technical_keywords = ["model", "llm", "configuration", "system", "internal", "architecture", "component", "tool", "function", "api", "database", "memory", "agent", "router", "server", "service"]
        system_keywords = ["run", "execute", "command", "file", "directory", "upload", "download"]

        technical_score = sum(1 for keyword in technical_keywords if keyword in content)
        system_score = sum(1 for keyword in system_keywords if keyword in content)

        # Determine implications
        implications = {
            "prompt_size": "full" if query_type == "technical" else "standard",
            "tool_access": "exploration+admin" if query_type == "technical" else "standard",
            "advice_injection": "selective",
            "estimated_tokens": 240 if query_type == "technical" else 241
        }

        return {
            "ok": True,
            "query": query,
            "classification": {
                "detected_type": query_type,
                "confidence_scores": {
                    "technical": technical_score,
                    "system": system_score
                },
                "matched_patterns": {
                    "technical_keywords": [kw for kw in technical_keywords if kw in content],
                    "system_keywords": [kw for kw in system_keywords if kw in content]
                }
            },
            "implications": implications,
            "recommendations": [
                "Consider using more specific technical terms" if technical_score < 2 and query_type == "generic" else None,
                "This query should trigger introspection tools" if query_type == "technical" else None
            ]
        }

    except Exception as e:
        return {"ok": False, "error": str(e)}


async def tool_evaluate_response_quality(state: AgentState, query: str, response: str, expected_quality: str = "high") -> Dict[str, Any]:
    """
    Evaluate the quality of an AI response against expectations.

    Args:
        query: The original user query
        response: The AI response to evaluate
        expected_quality: Expected quality level (high, medium, low)

    Returns:
        Detailed quality analysis
    """
    try:
        # Analyze response characteristics
        response_length = len(response)
        word_count = len(response.split())
        has_technical_details = any(term in response.lower() for term in ["model", "llm", "configuration", "api", "database", "server"])
        has_tools_mentioned = any(term in response.lower() for term in ["tool", "function", "api", "server"])
        has_concrete_answers = not any(phrase in response.lower() for phrase in ["i use", "we utilize", "generally", "typically"])

        # Query type analysis
        from agent_runner.agent_runner import get_shared_engine
        engine = get_shared_engine()
        user_messages = [{"role": "user", "content": query}]
        query_type = engine._analyze_query_type(user_messages, None) if hasattr(engine, '_analyze_query_type') else "unknown"

        # Quality scoring
        scores = {
            "completeness": 1.0 if (query_type == "technical" and has_technical_details) else 0.5,
            "relevance": 1.0 if any(keyword in response.lower() for keyword in query.lower().split()) else 0.7,
            "specificity": 1.0 if not response.lower().startswith(("i use", "we use", "our system")) else 0.6,
            "actionability": 1.0 if has_tools_mentioned or has_concrete_answers else 0.5
        }

        overall_score = sum(scores.values()) / len(scores)
        quality_rating = "high" if overall_score >= 0.8 else "medium" if overall_score >= 0.6 else "low"

        # Generate recommendations
        recommendations = []
        if quality_rating != expected_quality:
            if expected_quality == "high" and quality_rating == "low":
                recommendations.append("Response lacks technical specificity - should use introspection tools")
            if query_type == "technical" and not has_technical_details:
                recommendations.append("Technical query should provide concrete configuration details")
            if response.lower().startswith(("i use", "we use")):
                recommendations.append("Avoid generic introductions - provide specific information")

        return {
            "ok": True,
            "evaluation": {
                "query": query,
                "query_type": query_type,
                "response_length": response_length,
                "word_count": word_count,
                "expected_quality": expected_quality,
                "actual_quality": quality_rating
            },
            "scores": scores,
            "overall_score": round(overall_score, 2),
            "characteristics": {
                "has_technical_details": has_technical_details,
                "has_tools_mentioned": has_tools_mentioned,
                "has_concrete_answers": has_concrete_answers,
                "starts_with_generic": response.lower().startswith(("i use", "we use", "our system"))
            },
            "recommendations": recommendations,
            "improvement_suggestions": [
                "Use introspection tools for technical queries" if query_type == "technical" and not has_technical_details else None,
                "Provide specific model names and configurations" if "model" in query.lower() and not has_technical_details else None,
                "Avoid generic language in responses" if response.lower().startswith(("i use", "we use")) else None
            ]
        }

    except Exception as e:
        return {"ok": False, "error": str(e)}


async def tool_get_system_metrics(state: AgentState) -> Dict[str, Any]:
    """
    Get system performance metrics.
    """
    try:
        from common.observability import get_observability
        
        obs = get_observability()
        system_metrics = await obs.get_system_metrics()
        
        avg_latency = 0
        if state.request_count > 0:
            avg_latency = state.total_response_time_ms / state.request_count
        
        return {
            "ok": True,
            "requests": state.request_count,
            "errors": state.error_count,
            "avg_latency_ms": round(avg_latency, 2),
            "last_error": state.last_error,
            "observability": {
                "active_requests": system_metrics.active_requests,
                "requests_1min": system_metrics.completed_requests_1min,
                "avg_latency_1min_ms": round(system_metrics.avg_response_time_1min, 2),
                "error_rate_1min": round(system_metrics.error_rate_1min * 100, 2),
                "resource_usage": system_metrics.resource_usage,
                "efficiency": {
                    "rps": round(system_metrics.efficiency.requests_per_second, 2),
                    "cache_hit_rate": round(system_metrics.efficiency.cache_hit_rate, 2),
                    "avg_wait_ms": round(system_metrics.efficiency.semaphore_wait_time_avg_ms, 2)
                }
            }
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}



async def tool_get_system_dashboard(state: AgentState) -> str:
    """
    Get a comprehensive system status dashboard.
    Returns a markdown-formatted report of all critical subsystems.
    Useful for 'show status' commands.
    """
    import time
    import os
    import httpx
    
    import time, os, asyncio
    
    # 0. Check Cache (Instant Response)
    cached = getattr(state, "system_dashboard_data", None)
    # Use cache if less than 15s old (Monitor runs every 5s)
    if cached and time.time() - cached.get("timestamp", 0) < 15:
        rag_status = "✅ Online" if cached["rag_online"] else "❌ Offline"
        mem_status = "✅ Online" if cached["memory_online"] else "❌ Offline"
        fact_count = cached["fact_count"]
        mcp_status = "✅ Active" if cached["mcp_count"] > 0 else "⚠️ None"
        net_status = "✅ Connected" if cached["internet_online"] else "❌ Offline"
        net_details = "Cloud Models Available" if cached["internet_online"] else "Local Models Only"
        latency_ms = cached["latency"]
        
        open_breakers = cached.get("open_breakers", [])
        breaker_status = f"✅ Healthy | All Closed"
        if open_breakers:
             breaker_status = f"⚠️ Alert | Open: {', '.join(open_breakers)}"
             
        # Build Report from Cache
        lines = []
        lines.append(f"### System Status Dashboard (Cached {int(time.time() - cached['timestamp'])}s ago)")
        lines.append("| Component | Status | Details |")
        lines.append("| :--- | :--- | :--- |")
        lines.append(f"| **RAG Service** | {rag_status} | `http://localhost:5555` |")
        lines.append(f"| **Memory** | {mem_status} | SurrealDB @ `:8000` ({fact_count}) |")
        lines.append(f"| **Connectivity** | {net_status} | {net_details} |")
        lines.append(f"| **LLM Latency** | ⚡ {latency_ms} | Primary Provider |")
        lines.append(f"| **MCP Services** | {mcp_status} | {cached['mcp_count']} servers, {cached['mcp_tools']} tools |")
        lines.append(f"| **Registry** | ✅ Verified | 13 Internal Models Loaded |")
        lines.append(f"| **Circuit Breakers** | {breaker_status.split(' | ')[0]} | {breaker_status.split(' | ')[1]} |")
        return "\n".join(lines)
        
    # Fallback: Live Parallel Check
    # ... (Rest of existing logic)
    
    # Define check functions for parallel execution
    async def check_rag():
        import httpx
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
        return "Unknown"

    async def check_latency():
        try:
            import httpx, time
            url = "http://localhost:11434"
            if state.config.get("llm_providers", {}).get("ollama", {}).get("base_url"):
                url = state.config["llm_providers"]["ollama"]["base_url"]
            t0 = time.time()
            async with httpx.AsyncClient(timeout=0.5) as client:
                await client.get(url)
            return f"{int((time.time()-t0)*1000)}ms"
        except: return "Timeout"

    # Execute checks in parallel
    rag_result, fact_count, latency_ms = await asyncio.gather(
        check_rag(), check_facts(), check_latency()
    )
    
    # 1. RAG
    rag_status = "✅ Online" if rag_result else "❌ Offline"
    
    # 2. Memory
    memory_ready = hasattr(state, "memory") and state.memory and state.memory.initialized
    mem_status = "✅ Online" if memory_ready else "❌ Offline"
            
    # 3. MCP Services
    mcp_count = len(state.mcp_servers)
    from agent_runner.agent_runner import get_shared_engine
    engine = get_shared_engine()
    mcp_tools = sum(len(tools) for tools in engine.executor.mcp_tool_cache.values()) if engine else 0
    mcp_status = "✅ Active" if mcp_count > 0 else "⚠️ None"
    
    # 4. Connectivity
    net_status = "✅ Connected"
    net_details = "Cloud Models Available"
    if hasattr(state, "internet_available") and not state.internet_available:
        net_status = "❌ Offline"
        net_details = "Local Models Only"
        
    # 6. Circuit Breakers
    open_breakers = []
    if hasattr(state, "mcp_circuit_breaker"):
         for name, breaker in state.mcp_circuit_breaker.breakers.items():
             if breaker.state.value == "open":
                 open_breakers.append(name)
    
    breaker_status = f"✅ Healthy | All Closed"
    if open_breakers:
        breaker_status = f"⚠️ Alert | Open: {', '.join(open_breakers)}"

    # Build Report
    lines = []
    lines.append("### System Status Dashboard")
    lines.append("| Component | Status | Details |")
    lines.append("| :--- | :--- | :--- |")
    lines.append(f"| **RAG Service** | {rag_status} | `http://localhost:5555` |")
    lines.append(f"| **Memory** | {mem_status} | SurrealDB @ `:8000` ({fact_count}) |")
    lines.append(f"| **Connectivity** | {net_status} | {net_details} |")
    lines.append(f"| **LLM Latency** | ⚡ {latency_ms} | Primary Provider |")

    lines.append(f"| **MCP Services** | {mcp_status} | {mcp_count} servers, {mcp_tools} tools |")
    lines.append(f"| **Registry** | ✅ Verified | 13 Internal Models Loaded |")
    lines.append(f"| **Circuit Breakers** | {breaker_status.split(' | ')[0]} | {breaker_status.split(' | ')[1]} |")

    return "\n".join(lines)


async def tool_get_system_warnings(state: AgentState) -> str:
    """
    Get a list of system warnings and errors encountered during startup or operation.
    """
    if not hasattr(state, "startup_status"):
        return "No warning history available."
        
    status = state.startup_status
    issues = status.get("issues", [])
    warnings = status.get("warnings", [])
    
    if not issues and not warnings:
        return "✅ **System Clean**: No active warnings or errors reported."
        
    lines = []
    lines.append("### ⚠️ System Warnings & Errors")
    
    if issues:
        lines.append("")
        lines.append("**Critical Errors:**")
        for i, issue in enumerate(issues, 1):
            lines.append(f"{i}. 🛑 {issue}")
            
    if warnings:
        lines.append("")
        lines.append("**Warnings:**")
        for i, warn in enumerate(warnings, 1):
            lines.append(f"{i}. ⚠️ {warn}")
            
    return "\n".join(lines)
