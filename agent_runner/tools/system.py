
import asyncio
import logging
import subprocess
from typing import Dict, Any, List, Optional
from agent_runner.state import AgentState

logger = logging.getLogger("agent_runner.tools.system")

async def tool_run_command(state: AgentState, command: str, background: bool = False, dry_run: bool = False) -> Dict[str, Any]:
    """
    Run a shell command in the agent's environment.
    
    Args:
        command: The shell command to execute.
        background: If true, run in background (fire and forget-ish).
        dry_run: If true, simulates the execution and safety check without running logic.
    """
    if not state.config.get("agent_runner", {}).get("enable_command_execution", False):
        return {"ok": False, "error": "Command execution is disabled in configuration."}
    
    # [SENTINEL] Security Check
    try:
        from agent_runner.services.sentinel import Sentinel
        # Light instantiation (loads cache, syncs from DB if available)
        sentinel = Sentinel(state)
        # Initialize (sync from database if available)
        await sentinel.initialize()
        # Evaluate
        is_safe, reason = await sentinel.evaluate(command)
        
        if dry_run:
             return {
                 "ok": True, 
                 "dry_run": True,
                 "is_safe": is_safe,
                 "sentinel_reason": reason,
                 "command": command,
                 "message": f"[DRY RUN] Command would be {'ALLOWED' if is_safe else 'BLOCKED'}. Reason: {reason}"
             }
             
        if not is_safe:
            msg = f"SECURITY BLOCK (Sentinel): {reason}\nTo override and learn this pattern, reply with: 'Authorize: {command}'"
            return {"ok": False, "error": msg}
    except ImportError:
        pass # Fallback if module missing during refactor
    except Exception as e:
        logger.error(f"Sentinel Check Failed: {e}")
        # Fail safe? Or Fail Open? For dev mode, maybe warn. But strict security says fail closed.
        return {"ok": False, "error": f"Security Audit Failed: {str(e)}"}

    cwd = state.agent_fs_root
    
    logger.info(f"Executing command: {command} (cwd={cwd})")
    
    try:
        if background:
            # Fire and forget (roughly) - in a real system we might track this
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd
            )
            return {"ok": True, "message": "Command started in background", "pid": process.pid}
            
        else:
            # Run and wait
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd
            )
            stdout, stderr = await process.communicate()
            
            # [ROBUSTNESS] Output Truncation
            # Prevent context overflow from massive logs
            MAX_OUTPUT_CHARS = 4000
            
            decoded_stdout = stdout.decode("utf-8", errors="replace")
            decoded_stderr = stderr.decode("utf-8", errors="replace")
            
            full_output = decoded_stdout + "\n" + decoded_stderr
            
            if len(full_output) > MAX_OUTPUT_CHARS:
                # Truncate and Save
                import time
                import hashlib
                
                # Ensure log dir exists
                log_dir = state.agent_fs_root / "logs" / "outputs"
                log_dir.mkdir(parents=True, exist_ok=True)
                
                # Allow user to locate it easily
                ts = time.strftime("%Y%m%d_%H%M%S")
                h = hashlib.md5(command.encode()).hexdigest()[:8]
                filename = f"cmd_{ts}_{h}.txt"
                log_path = log_dir / filename
                
                with open(log_path, "w") as f:
                    f.write(f"Command: {command}\n\nSTDOUT:\n{decoded_stdout}\n\nSTDERR:\n{decoded_stderr}")
                    
                # Truncate for Chat
                trunc_stdout = decoded_stdout[:2000] + f"\n... [TRUNCATED view file: logs/outputs/{filename}]" if len(decoded_stdout) > 2000 else decoded_stdout
                trunc_stderr = decoded_stderr[:2000] + f"\n... [TRUNCATED view file: logs/outputs/{filename}]" if len(decoded_stderr) > 2000 else decoded_stderr
                
                return {
                    "ok": process.returncode == 0,
                    "returncode": process.returncode,
                    "stdout": trunc_stdout,
                    "stderr": trunc_stderr,
                    "truncated": True,
                    "full_log": str(log_path)
                }

            return {
                "ok": process.returncode == 0,
                "returncode": process.returncode,
                "stdout": decoded_stdout,
                "stderr": decoded_stderr,
            }
            
    except Exception as e:
        logger.error(f"Command failed: {e}")
        return {"ok": False, "error": str(e)}

async def tool_set_mode(state: AgentState, mode: str) -> Dict[str, Any]:
    """
    Switch the Agent's active mode (e.g. 'chat' -> 'coding').
    This persists across restarts via Sovereign Memory.
    
    Args:
        mode: The target mode (chat, coding, admin, etc).
    """
    mode = mode.lower().strip()
    
    # Validation against Sovereign Config
    known_modes = list(state.modes.keys()) if state.modes else ["chat"]
    if mode not in known_modes:
         # Fallback allowance for bootstrapping
         if mode not in ["chat", "coding", "admin"]:
             return {"ok": False, "error": f"Unknown mode '{mode}'. Available: {known_modes}"}
    
    # Update State (Triggers DB Sync via Property Setter)
    state.active_mode = mode
    logger.info(f"Agent Mode Switched to: {mode.upper()}")
    
    return {"ok": True, "message": f"Mode switched to {mode.upper()}. System prompt will adapt on next turn."}

async def tool_trigger_task(state: AgentState, task_name: str) -> Dict[str, Any]:
    """
    Manually trigger a registered background task to run immediately.
    
    Args:
        task_name: The name of the task to trigger (e.g. 'night_shift_refactor')
    """
    from agent_runner.background_tasks import get_task_manager
    tm = get_task_manager()
    return await tm.trigger_task(task_name)

async def tool_report_missing_tool(state: AgentState, tool_name: str, reason: str) -> Dict[str, Any]:
    """
    Report a tool that is missing but required to complete a task.
    This creates a feedback loop for the user to add new capabilities.
    
    Args:
        tool_name: The name of the tool you wish you had (e.g. 'browser_screenshot', 'csv_parser').
        reason: Why you need this tool and what you tried to do.
    """
    import time
    from pathlib import Path
    
    log_path = state.agent_fs_root / "missing_tools.md"
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
    entry = f"\n## [{timestamp}] Missing: `{tool_name}`\n"
    entry += f"**Reason**: {reason}\n"
    entry += f"**Context**: Task execution paused.\n"
    
    # Append to file
    try:
        with open(log_path, "a") as f:
            f.write(entry)
        
        logger.info(f"Registered missing tool request: {tool_name}")
        return {"ok": True, "message": f"Logged missing tool request for '{tool_name}'. The user has been notified."}
    except Exception as e:
        return {"ok": False, "error": str(e)}

async def tool_run_memory_consolidation(state: AgentState) -> Dict[str, Any]:
    """
    Runs the specialized memory consolidation logic (extracting facts from episodes).
    """
    from agent_runner.memory_tasks import memory_consolidation_task
    try:
        await memory_consolidation_task(state)
        return {"ok": True, "message": "Memory consolidation cycle completed."}
    except Exception as e:
        return {"ok": False, "error": str(e)}

async def tool_check_system_health(state: AgentState) -> Dict[str, Any]:
    """
    Query the Orchestrator Router for a detailed health report, including Circuit Breakers.
    This allows the Agent to check on the health of the system it is running in.
    """
    try:
        base = state.gateway_base # e.g. http://127.0.0.1:5455
        url = f"{base}/admin/health/summary"
        
        client = await state.get_http_client()
        resp = await client.get(url, timeout=5.0)
        
        if resp.status_code != 200:
             return {"ok": False, "error": f"Router API returned {resp.status_code}"}
             
        data = resp.json()
        
        # Build Summary
        status = data.get("status", "unknown").upper()
        crit = data.get("critical_count", 0)
        warn = data.get("warning_count", 0)
        
        breakers = data.get("overall_status", {})
        
        report = f"## SYSTEM HEALTH: {status}\n"
        report += f"- Critical Issues: {crit}\n"
        report += f"- Warnings: {warn}\n\n"
        
        if breakers:
             report += "### Circuit Breakers\n"
             report += "| Service | State | Failures | Recover In |\n"
             report += "|---|---|---|---|\n"
             for name, b in breakers.items():
                  state_str = b.get("state", "??")
                  fails = b.get("failures", 0)
                  rem = int(b.get("seconds_remaining", 0))
                  icon = "🟢" if state_str == "closed" else "🔴" if state_str == "open" else "🟡"
                  report += f"| {icon} {name} | {state_str.upper()} | {fails} | {rem}s |\n"
        
        # --- AGENT LOCAL STATUS ---
        report += "\n### AGENT STATE\n"
        report += f"- **Mode**: `{state.active_mode.upper()}`\n"
        report += f"- **Model**: `{state.agent_model}`\n"
        report += f"- **Connection**: {'🟢 Online' if state.internet_available else '🔴 Offline'}\n"
        report += f"- **Tools**: {len(state.executor.tool_definitions) if hasattr(state, 'executor') else '?'}\n"
        
        return {
             "ok": True,
             "report": report,
             "raw": data
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}

async def tool_query_logs(state: AgentState, limit: int = 50, level: str = None, service: str = None, needs_review: bool = None) -> Dict[str, Any]:
    """
    Query the centralized 'diagnostic_log' table.
    
    Args:
        limit: Max logs to retrieve (default 50)
        level: Optional minimum log level (INFO, WARNING, ERROR, CRITICAL).
        service: Optional service name to filter by.
        needs_review: If True, only return logs flagged by Sorter as 'UNKNOWN' / needing review.
    """
    try:
        import os
        
        where_clauses = []
        if service:
            where_clauses.append(f"service = '{service}'")
        
        if needs_review is not None:
             val = "true" if needs_review else "false"
             where_clauses.append(f"needs_review = {val}")

        if level:
            # Simple exact match or subset useful for now
            if level == "ERROR":
                where_clauses.append("(level = 'ERROR' OR level = 'CRITICAL')")
            elif level == "WARNING":
                where_clauses.append("(level = 'WARNING' OR level = 'ERROR' OR level = 'CRITICAL')")
            else:
                where_clauses.append(f"level = '{level}'")
            
        where_str = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        query = f"USE NS {os.getenv('SURREAL_NS', 'orchestrator')}; USE DB {os.getenv('SURREAL_DB', 'memory')}; SELECT * FROM diagnostic_log {where_str} ORDER BY timestamp DESC LIMIT {limit};"
        
        # Use State's client
        client = await state.get_http_client()
        url = f"{state.config.get('surreal', {}).get('url', 'http://localhost:8000')}/sql"
        
        headers = {
            "Accept": "application/json", 
            "Content-Type": "text/plain",
            # Fallback headers for older surreal versions if content-type isn't enough
            "ns": os.getenv("SURREAL_NS", "orchestrator"),
            "db": os.getenv("SURREAL_DB", "memory")
        }
        
        auth = (os.getenv("SURREAL_USER", "root"), os.getenv("SURREAL_PASS", "root"))
        
        # We use a fresh request for DB to be safe on Auth/Headers
        import httpx
        async with httpx.AsyncClient() as db_client:
            resp = await db_client.post(url, content=query, auth=auth, headers=headers, timeout=5.0)
            
        if resp.status_code != 200:
             return {"ok": False, "error": f"DB Query failed: {resp.text}"}
             
        data = resp.json()
        
        # Parse Multi-Statement Result (USE; USE; SELECT)
        results = []
        for item in data:
            if item.get("status") == "OK" and isinstance(item.get("result"), list):
                 res_list = item.get("result", [])
                 if res_list:
                     results = res_list
                     break
        
        return {
            "ok": True,
            "count": len(results),
            "logs": results
        }

    except Exception as e:
        return {"ok": False, "error": str(e)}

async def tool_add_lexicon_entry(state: AgentState, pattern: str, label: str, severity: str = "WARNING") -> Dict[str, Any]:
    """
    Add a new learned error pattern to the system lexicon.
    This allows the system to recognize this error in the future.
    
    Args:
        pattern: Regex pattern to match the error (e.g. "Connection refused.*port 5432").
        label: specialized classifier label (e.g. "DB_CONNECTION_FAILURE").
        severity: INFO, WARNING, ERROR, or CRITICAL.
    """
    import yaml
    from pathlib import Path
    
    # agent_fs_root is usually "agent_fs_root". Config is parallel to it.
    lex_dir = state.agent_fs_root.parent / "config" / "lexicons"
    lex_dir.mkdir(parents=True, exist_ok=True)
    
    target_file = lex_dir / "learned_patterns.yaml"
    
    entry = {
        "pattern": pattern,
        "label": label,
        "severity": severity,
        "source": "diagnostician_auto_learn",
        "created_at": str(state.started_at) # simplistic timestamp, accurate enough
    }
    
    try:
        # Load existing
        data = {"patterns": []}
        if target_file.exists():
            with open(target_file, "r") as f:
                loaded = yaml.safe_load(f)
                if loaded and "patterns" in loaded:
                    data = loaded
        
        # Append
        data["patterns"].append(entry)
        
        # Save
        with open(target_file, "w") as f:
            yaml.dump(data, f, sort_keys=False)
            
        logger.info(f"Learned new pattern: {label} -> {pattern}")
        return {"ok": True, "message": f"Successfully learned pattern for {label}"}
        
    except Exception as e:
        return {"ok": False, "error": str(e)}

async def tool_get_system_config(state: AgentState, key: str) -> Dict[str, Any]:
    """
    Get a system configuration value (e.g. 'router_mode').
    """
    try:
        base = state.gateway_base # e.g. http://127.0.0.1:5455
        url = f"{base}/config/{key}"
        
        client = await state.get_http_client()
        resp = await client.get(url, timeout=5.0)
        
        if resp.status_code != 200:
             return {"ok": False, "error": f"API Error {resp.status_code}"}
             
        data = resp.json()
        return {"ok": True, "value": data.get("value")}
    except Exception as e:
        return {"ok": False, "error": str(e)}

async def tool_set_system_config(state: AgentState, key: str, value: str) -> Dict[str, Any]:
    """
    Set a system configuration key.
    persist=True always.
    """
    # TODO: SystemRegistry not yet implemented - validation skipped for now
    # if not SystemRegistry.validate_toggle_value(key, value):
    #     toggle = SystemRegistry.get_toggle(key)
    #     valid_opts = toggle.options if toggle else "Unknown Key"
    #     return {"ok": False, "error": f"Invalid value '{value}' for key '{key}'. Valid options: {valid_opts}"}

    try:
        base = state.gateway_base
        client = await state.get_http_client()
        url = f"{base}/config/{key}"
        
        # Determine if we need to call Agent config or Router config or Policy
        # Currently we only really support Router/Surreal config via the Router API
        
        resp = await client.post(url, json={"value": value}, timeout=5.0)
        
        if resp.status_code == 200:
            return {"ok": True, "result": f"Successfully set '{key}' to '{value}'"}
        else:
            return {"ok": False, "error": f"Router API error: {resp.status_code} - {resp.text}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

async def tool_sentinel_authorize(state: AgentState, command: str) -> Dict[str, Any]:
    """
    Explicitly authorize a command pattern that was previously blocked by Sentinel.
    This 'teaches' the system that this pattern is safe for future use.
    """
    try:
        from agent_runner.services.sentinel import Sentinel
        sentinel = Sentinel(state)
        await sentinel.initialize()  # Sync from database
        # We handle the import re locally to avoid polluting top level
        import re
        # Convert to strict start match, wildcard end
        safe_pattern = f"^{re.escape(command.strip())}.*"
        
        # [FIX] learn_pattern is now async for DB calls
        await sentinel.learn_pattern(safe_pattern, True, "User Override via tool_sentinel_authorize")
        
        return {"ok": True, "message": f"Pattern learned. You may now execute: {command}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

async def tool_register_trigger(state: AgentState, pattern: str, action_type: str, action_data: str, description: str) -> Dict[str, Any]:
    """
    Register a new dynamic trigger (Slash Command or Keyword) for the Agent.
    
    Args:
        pattern: The keyword or phrase to listen for (e.g. 'cwindow', 'qq').
        action_type: One of ['control_ui', 'menu', 'system_prompt'].
        action_data: JSON string of parameters for the action.
        description: Human readable description for the help menu.
    """
    try:
        import json
        data = {}
        if action_data:
            try:
                data = json.loads(action_data)
            except:
                return {"ok": False, "error": "action_data must be valid JSON string"}

        # TODO: SystemRegistry not yet implemented - using sovereign triggers instead
        from common.sovereign import get_sovereign_triggers
        # For now, triggers are managed via sovereign.yaml
        # SystemRegistry.add_trigger(pattern, action_type, data, description)
        return {"ok": False, "error": "Trigger registration not yet implemented. Use sovereign.yaml for now."}
    except Exception as e:
        return {"ok": False, "error": str(e)}

async def tool_remove_trigger(state: AgentState, pattern: str) -> Dict[str, Any]:
    """Remove a dynamic trigger by its pattern."""
    try:
        # TODO: SystemRegistry not yet implemented
        # SystemRegistry.remove_trigger(pattern)
        return {"ok": False, "error": "Trigger removal not yet implemented. Edit sovereign.yaml for now."}
    except Exception as e:
        return {"ok": False, "error": str(e)}

async def tool_list_triggers(state: AgentState) -> Dict[str, Any]:
    """List all active triggers in the registry."""
    # TODO: SystemRegistry not yet implemented - using sovereign triggers instead
    from common.sovereign import get_sovereign_triggers
    triggers = get_sovereign_triggers()
    return {"ok": True, "triggers": triggers}



async def tool_manage_secret(state: AgentState, key: str, value: str) -> Dict[str, Any]:
    """
    Securely add or update a secret (API Key, Token) in the .env file.
    This allows the system to persist credentials provided in chat.
    
    Args:
        key: The environment variable name (e.g. OPENWEATHER_API_KEY).
        value: The secret value.
    """
    try:
        from agent_runner.config_manager import ConfigManager
        manager = ConfigManager(state)
        
        # Use the robust patch method from ConfigManager
        await manager._patch_env_file(key, value)
        
        # Also sync to DB immediately to be safe
        await manager._update_db_config(key, value, "agent_tool")
        
        return {
            "ok": True, 
            "message": f"Secret '{key}' saved to .env and Registry. Restarting agent is recommended to apply changes."
        }
    except Exception as e:
        logger.error(f"Failed to save secret {key}: {e}")
        return {"ok": False, "error": str(e)}

async def tool_restart_agent(state: AgentState, reason: str = "manual_triggered") -> Dict[str, Any]:
    """
    Gracefully restart the Agent Runner service.
    Sets a flag in the DB so the Agent can notify the user upon successful boot.
    
    Args:
        reason: Why the restart was triggered (for logging).
    """
    try:
        logger.info(f"Initiating Graceful Restart. Reason: {reason}")
        
        # 1. Update DB Flag for "I am back online" notification
        # We use strict SQL to ensure it persists
        q = "UPDATE system_state SET details.pending_restart_notification = true WHERE item = 'agent_lifecycle'; "
        q += "IF count(SELECT * FROM system_state WHERE item = 'agent_lifecycle') == 0 THEN CREATE system_state SET item = 'agent_lifecycle', details = {pending_restart_notification: true} END;"
        
        # Direct DB call via MemoryServer if available
        if hasattr(state, "memory") and state.memory:
            from agent_runner.db_utils import run_query
            await run_query(state, q)
            logger.info("✅ Restart notification flag set in database")
        else:
            logger.warning("Agent memory not ready, restart flag might not persist.")
             
        # 2. Find and trigger restart script
        # Try multiple possible locations for manage.sh
        from pathlib import Path
        import os
        
        # Get project root (parent of agent_runner directory)
        project_root = Path(__file__).parent.parent.parent.resolve()
        
        # Try multiple possible script locations
        possible_scripts = [
            project_root / "manage.sh",  # Root directory
            project_root / "bin" / "manage.sh",  # bin directory
            project_root / "bin" / "restart_all.sh",  # Alternative script
        ]
        
        manage_script = None
        for script_path in possible_scripts:
            if script_path.exists() and script_path.is_file():
                manage_script = script_path
                logger.info(f"✅ Found restart script at: {manage_script}")
                break
        
        # 3. Use launchctl kickstart directly (most reliable method)
        # This works even when called from within the agent process
        import subprocess
        import os
        
        # Determine launchd domain
        user_uid = os.getuid()
        domain = f"gui/{user_uid}"
        
        # Check if domain exists, fallback to user domain
        try:
            result = subprocess.run(
                ["launchctl", "print", domain],
                capture_output=True,
                timeout=2
            )
            if result.returncode != 0:
                domain = f"user/{user_uid}"
        except Exception:
            domain = f"user/{user_uid}"
        
        agent_label = "local.ai.agent_runner"
        service_path = f"{domain}/{agent_label}"
        
        try:
            # Use launchctl kickstart -k to restart the service
            # This is the modern, reliable way to restart a launchd service
            logger.info(f"Triggering restart via launchctl kickstart: {service_path}")
            
            # Schedule restart in a background task with a small delay
            # This ensures the HTTP response is sent before the service restarts
            import asyncio
            async def _delayed_restart():
                # Wait 1 second to allow response to be sent
                await asyncio.sleep(1.0)
                try:
                    process = subprocess.Popen(
                        ["launchctl", "kickstart", "-k", service_path],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        start_new_session=True
                    )
                    logger.info(f"✅ Restart command sent (PID: {process.pid})")
                    
                    # If manage.sh was found, also try that as a backup
                    if manage_script:
                        logger.info(f"Also attempting restart via script: {manage_script}")
                        script_args = ["restart-agent"] if "manage.sh" in str(manage_script) else []
                        try:
                            os.chmod(manage_script, 0o755)
                        except Exception:
                            pass
                        
                        subprocess.Popen(
                            [str(manage_script)] + script_args,
                            cwd=str(manage_script.parent),
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            start_new_session=True
                        )
                except Exception as restart_err:
                    logger.error(f"Delayed restart failed: {restart_err}", exc_info=True)
            
            # Schedule the restart task (fire and forget)
            asyncio.create_task(_delayed_restart())
            
            return {"ok": True, "message": "Restart initiated. See you on the other side. 🫡", "method": "launchctl_kickstart", "service": service_path}
            
        except Exception as launch_err:
            logger.error(f"Launchctl kickstart failed: {launch_err}", exc_info=True)
            
            # Fallback: Try manage.sh if available
            if manage_script:
                try:
                    logger.info(f"Falling back to script: {manage_script}")
                    script_args = ["restart-agent"] if "manage.sh" in str(manage_script) else []
                    try:
                        os.chmod(manage_script, 0o755)
                    except Exception:
                        pass
                    
                    process = subprocess.Popen(
                        [str(manage_script)] + script_args,
                        cwd=str(manage_script.parent),
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        start_new_session=True
                    )
                    logger.info(f"✅ Restart script spawned (PID: {process.pid})")
                    return {"ok": True, "message": "Restart initiated via script. See you on the other side. 🫡", "script": str(manage_script), "pid": process.pid}
                except Exception as script_err:
                    logger.error(f"Script restart also failed: {script_err}")
                    return {"ok": False, "error": f"Both launchctl and script restart failed. Launchctl: {launch_err}, Script: {script_err}"}
            else:
                return {"ok": False, "error": f"Launchctl restart failed and no script found. Error: {launch_err}"}
        
    except Exception as e:
        logger.error(f"Restart failed: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}


async def tool_get_boot_status(state: AgentState) -> Dict[str, Any]:
    """
    Check if a restart notification is pending. Used by Boot Scheduler.
    Returns: {"pending": bool}
    """
    try:
        q = "SELECT details.pending_restart_notification as pending FROM system_state WHERE item = 'agent_lifecycle'"
        if hasattr(state, "memory") and state.memory:
            from agent_runner.db_utils import run_query
            res = await run_query(state, q)
            if res and len(res) > 0:
                return {"ok": True, "pending": res[0].get("pending", False)}
        return {"ok": True, "pending": False}
    except Exception:
        return {"ok": False, "pending": False}


async def tool_clear_boot_status(state: AgentState) -> Dict[str, Any]:
    """Clear the pending restart flag."""
    try:
        q = "UPDATE system_state SET details.pending_restart_notification = false WHERE item = 'agent_lifecycle'"
        if hasattr(state, "memory") and state.memory:
            from agent_runner.db_utils import run_query
            await run_query(state, q)
        return {"ok": True}
    except Exception:
        return {"ok": False}



# ============================================================================
# Layer Control Tools - Quality/Speed Control System
# ============================================================================

async def tool_set_quality_tier(state: AgentState, tier: str) -> Dict[str, Any]:
    """
    Set the system quality tier.
    
    Tiers:
    - fastest: Minimal quality, maximum speed (50-100ms, 200-300 tokens)
    - fast: Reduced quality, high speed (100-150ms, 300-500 tokens)
    - balanced: Good balance (150-250ms, 500-1000 tokens) [default]
    - quality: High quality, moderate speed (200-350ms, 1000-1500 tokens)
    - maximum: Best quality, slower speed (300-500ms, 1500-2500 tokens)
    """
    if not state:
        logger.error("tool_set_quality_tier: state is None")
        return {"ok": False, "error": "Internal error: state not available"}
    
    if not isinstance(tier, str):
        logger.warning(f"tool_set_quality_tier: invalid tier type: {type(tier)}")
        return {"ok": False, "error": f"Tier must be a string, got {type(tier).__name__}"}
    
    try:
        from agent_runner.quality_tiers import QualityTier, get_tier_performance_estimate, get_tier_description
        quality_tier = QualityTier(tier.lower())
        
        # Validate state has required method
        if not hasattr(state, 'set_quality_tier'):
            logger.error("tool_set_quality_tier: state missing set_quality_tier method")
            return {"ok": False, "error": "Internal error: quality tier system not initialized"}
        
        state.set_quality_tier(quality_tier)
        
        estimate = get_tier_performance_estimate(quality_tier)
        description = get_tier_description(quality_tier)
        
        logger.info(f"Quality tier set to '{tier}' (latency: {estimate['latency_ms'][0]}-{estimate['latency_ms'][1]}ms)")
        
        return {
            "ok": True,
            "tier": tier,
            "description": description,
            "estimated_latency_ms": estimate["latency_ms"],
            "estimated_context_tokens": estimate["context_tokens"],
            "message": f"Quality tier set to '{tier}'. {description}. Estimated latency: {estimate['latency_ms'][0]}-{estimate['latency_ms'][1]}ms, Context: {estimate['context_tokens'][0]}-{estimate['context_tokens'][1]} tokens."
        }
    except ValueError as e:
        logger.warning(f"tool_set_quality_tier: invalid tier '{tier}': {e}")
        return {
            "ok": False, 
            "error": f"Invalid tier: {tier}. Must be one of: fastest, fast, balanced, quality, maximum"
        }
    except AttributeError as e:
        logger.error(f"tool_set_quality_tier: missing attribute: {e}", exc_info=True)
        return {"ok": False, "error": f"Internal error: {str(e)}"}
    except Exception as e:
        logger.error(f"tool_set_quality_tier: unexpected error: {e}", exc_info=True)
        return {"ok": False, "error": f"Failed to set quality tier: {str(e)}"}


async def tool_get_quality_tier(state: AgentState) -> Dict[str, Any]:
    """Get current quality tier and configuration."""
    if not state:
        logger.error("tool_get_quality_tier: state is None")
        return {"ok": False, "error": "Internal error: state not available"}
    
    try:
        from agent_runner.quality_tiers import QualityTier, get_tier_config, get_tier_performance_estimate, get_tier_description
        
        # Safe attribute access with fallback
        tier = getattr(state, 'quality_tier', QualityTier.BALANCED)
        if tier is None:
            tier = QualityTier.BALANCED
            logger.warning("tool_get_quality_tier: quality_tier was None, using BALANCED default")
        
        config = get_tier_config(tier)
        estimate = get_tier_performance_estimate(tier)
        description = get_tier_description(tier)
        
        logger.debug(f"Retrieved quality tier: {tier.value}")
        
        return {
            "ok": True,
            "current_tier": tier.value,
            "description": description,
            "config": config,
            "estimated_latency_ms": estimate["latency_ms"],
            "estimated_context_tokens": estimate["context_tokens"],
            "available_tiers": [t.value for t in QualityTier]
        }
    except AttributeError as e:
        logger.error(f"tool_get_quality_tier: missing attribute: {e}", exc_info=True)
        return {"ok": False, "error": f"Internal error: {str(e)}"}
    except Exception as e:
        logger.error(f"tool_get_quality_tier: unexpected error: {e}", exc_info=True)
        return {"ok": False, "error": f"Failed to get quality tier: {str(e)}"}


async def tool_control_refinement(state: AgentState, enabled: Optional[bool] = None,
                                  memory_limit: Optional[int] = None,
                                  arch_limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Control query refinement and memory retrieval.
    
    Args:
        enabled: Enable/disable query refinement (None = no change)
        memory_limit: Number of memory facts to retrieve (None = no change, 0 = disable)
        arch_limit: Number of architecture facts to retrieve (None = no change, 0 = disable)
    """
    if not state:
        logger.error("tool_control_refinement: state is None")
        return {"ok": False, "error": "Internal error: state not available"}
    
    try:
        changes = []
        
        # Validate inputs
        if enabled is not None and not isinstance(enabled, bool):
            logger.warning(f"tool_control_refinement: invalid enabled type: {type(enabled)}")
            return {"ok": False, "error": f"enabled must be boolean, got {type(enabled).__name__}"}
        
        if memory_limit is not None:
            if not isinstance(memory_limit, int):
                logger.warning(f"tool_control_refinement: invalid memory_limit type: {type(memory_limit)}")
                return {"ok": False, "error": f"memory_limit must be integer, got {type(memory_limit).__name__}"}
            if memory_limit < 0:
                logger.warning(f"tool_control_refinement: invalid memory_limit value: {memory_limit}")
                return {"ok": False, "error": "memory_limit must be >= 0"}
        
        if arch_limit is not None:
            if not isinstance(arch_limit, int):
                logger.warning(f"tool_control_refinement: invalid arch_limit type: {type(arch_limit)}")
                return {"ok": False, "error": f"arch_limit must be integer, got {type(arch_limit).__name__}"}
            if arch_limit < 0:
                logger.warning(f"tool_control_refinement: invalid arch_limit value: {arch_limit}")
                return {"ok": False, "error": "arch_limit must be >= 0"}
        
        if enabled is not None:
            state.skip_refinement_default = not enabled
            changes.append(f"Refinement: {'enabled' if enabled else 'disabled'}")
        
        if memory_limit is not None:
            if not hasattr(state, 'memory_retrieval_limit'):
                state.memory_retrieval_limit = 10  # Default
            state.memory_retrieval_limit = memory_limit
            if memory_limit == 0:
                changes.append("Memory retrieval: disabled")
            else:
                changes.append(f"Memory retrieval: {memory_limit} facts")
        
        if arch_limit is not None:
            if not hasattr(state, 'architecture_context_limit'):
                state.architecture_context_limit = 50  # Default
            state.architecture_context_limit = arch_limit
            if arch_limit == 0:
                changes.append("Architecture context: disabled")
            else:
                changes.append(f"Architecture context: {arch_limit} facts")
        
        if changes:
            logger.info(f"Refinement control updated: {', '.join(changes)}")
        else:
            logger.debug("tool_control_refinement: no changes requested")
        
        return {
            "ok": True,
            "changes": changes,
            "config": {
                "refinement_enabled": not getattr(state, 'skip_refinement_default', False),
                "memory_limit": getattr(state, 'memory_retrieval_limit', 10),
                "arch_limit": getattr(state, 'architecture_context_limit', 50)
            }
        }
    except AttributeError as e:
        logger.error(f"tool_control_refinement: missing attribute: {e}", exc_info=True)
        return {"ok": False, "error": f"Internal error: {str(e)}"}
    except Exception as e:
        logger.error(f"tool_control_refinement: unexpected error: {e}", exc_info=True)
        return {"ok": False, "error": f"Failed to control refinement: {str(e)}"}


async def tool_set_context_prune_limit(state: AgentState, limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Set context pruning limit.
    
    Args:
        limit: Number of messages to keep (None = no pruning, 0 = current message only, 20 = default)
    """
    if not state:
        logger.error("tool_set_context_prune_limit: state is None")
        return {"ok": False, "error": "Internal error: state not available"}
    
    try:
        if limit is None:
            state.context_prune_limit = None
            logger.info("Context pruning disabled (no limit)")
            return {"ok": True, "prune_limit": None, "message": "Context pruning disabled (no limit)"}
        
        # Validate input
        if not isinstance(limit, int):
            logger.warning(f"tool_set_context_prune_limit: invalid limit type: {type(limit)}")
            return {"ok": False, "error": f"Limit must be integer, got {type(limit).__name__}"}
        
        if limit < 0:
            logger.warning(f"tool_set_context_prune_limit: invalid limit value: {limit}")
            return {"ok": False, "error": "Limit must be >= 0"}
        
        state.context_prune_limit = limit
        message = f"Context pruning set to {limit} messages" if limit > 0 else "Context pruning disabled"
        logger.info(message)
        
        return {
            "ok": True,
            "prune_limit": limit,
            "message": message
        }
    except AttributeError as e:
        logger.error(f"tool_set_context_prune_limit: missing attribute: {e}", exc_info=True)
        return {"ok": False, "error": f"Internal error: {str(e)}"}
    except Exception as e:
        logger.error(f"tool_set_context_prune_limit: unexpected error: {e}", exc_info=True)
        return {"ok": False, "error": f"Failed to set context prune limit: {str(e)}"}


async def tool_filter_tools_by_category(state: AgentState, 
                                        categories: Optional[List[str]] = None,
                                        enabled: bool = True) -> Dict[str, Any]:
    """
    Filter tools by category.
    
    Args:
        categories: List of categories (e.g., ["filesystem", "status"]). If None, disable filtering.
        enabled: If False, disable category filtering
    
    Available categories: web_search, filesystem, code, browser, memory, scraping, 
                          automation, http, weather, document, ollama, system, status, 
                          control, exploration, thinking, knowledge, admin
    """
    if not state:
        logger.error("tool_filter_tools_by_category: state is None")
        return {"ok": False, "error": "Internal error: state not available"}
    
    try:
        from agent_runner.tool_categories import VALID_CATEGORIES
        
        # Validate enabled parameter
        if not isinstance(enabled, bool):
            logger.warning(f"tool_filter_tools_by_category: invalid enabled type: {type(enabled)}")
            return {"ok": False, "error": f"enabled must be boolean, got {type(enabled).__name__}"}
        
        if not enabled or categories is None:
            state.tool_category_filter = None
            logger.info("Tool category filtering disabled")
            return {"ok": True, "filtering": "disabled", "message": "Tool category filtering disabled"}
        
        # Validate categories parameter
        if not isinstance(categories, list):
            logger.warning(f"tool_filter_tools_by_category: invalid categories type: {type(categories)}")
            return {"ok": False, "error": f"categories must be a list, got {type(categories).__name__}"}
        
        # Validate each category
        invalid = [c for c in categories if not isinstance(c, str) or c not in VALID_CATEGORIES]
        if invalid:
            logger.warning(f"tool_filter_tools_by_category: invalid categories: {invalid}")
            return {"ok": False, "error": f"Invalid categories: {invalid}. Valid: {list(VALID_CATEGORIES)}"}
        
        state.tool_category_filter = categories
        message = f"Tool filtering enabled for categories: {', '.join(categories)}"
        logger.info(message)
        
        return {
            "ok": True,
            "categories": categories,
            "message": message
        }
    except ImportError as e:
        logger.error(f"tool_filter_tools_by_category: failed to import VALID_CATEGORIES: {e}", exc_info=True)
        return {"ok": False, "error": "Internal error: tool categories module not available"}
    except AttributeError as e:
        logger.error(f"tool_filter_tools_by_category: missing attribute: {e}", exc_info=True)
        return {"ok": False, "error": f"Internal error: {str(e)}"}
    except Exception as e:
        logger.error(f"tool_filter_tools_by_category: unexpected error: {e}", exc_info=True)
        return {"ok": False, "error": f"Failed to filter tools by category: {str(e)}"}


async def tool_get_layer_status(state: AgentState) -> Dict[str, Any]:
    """Get status of all chat layers."""
    if not state:
        logger.error("tool_get_layer_status: state is None")
        return {"ok": False, "error": "Internal error: state not available"}
    
    try:
        # Safe attribute access with defaults
        quality_tier_value = 'balanced'
        if hasattr(state, 'quality_tier') and state.quality_tier:
            try:
                quality_tier_value = state.quality_tier.value
            except (AttributeError, TypeError):
                logger.warning("tool_get_layer_status: quality_tier exists but has no value attribute, using default")
        
        status = {
            "ok": True,
            "layers": {
                "nexus": {
                    "enabled": True,
                    "description": "Input/Output Regulator - First gate for user input",
                    "capabilities": ["trigger_matching", "system_message_injection", "event_filtering"]
                },
                "refinement": {
                    "enabled": not getattr(state, 'skip_refinement_default', False),
                    "skip_refinement": getattr(state, 'skip_refinement_default', False),
                    "memory_limit": getattr(state, 'memory_retrieval_limit', 10),
                    "arch_limit": getattr(state, 'architecture_context_limit', 50),
                    "description": "Query Refinement - Controls memory retrieval and context"
                },
                "context": {
                    "prune_limit": getattr(state, 'context_prune_limit', 20),
                    "file_context": True,  # Always enabled if files exist
                    "service_alerts": True,  # Always enabled if services down
                    "description": "System Prompt Construction - Context filtering"
                },
                "tool_filtering": {
                    "enabled": True,
                    "mode": "intent_based",  # or "core_only", "all"
                    "category_filter": getattr(state, 'tool_category_filter', None),
                    "max_tools": 120,
                    "description": "Tool Filtering - Controls which tools are available"
                },
                "stream_events": {
                    "enabled": True,
                    "description": "Stream Event Filtering - Controls what events are yielded"
                }
            },
            "quality_tier": quality_tier_value
        }
        
        logger.debug("Retrieved layer status")
        return status
    except Exception as e:
        logger.error(f"tool_get_layer_status: unexpected error: {e}", exc_info=True)
        return {"ok": False, "error": f"Failed to get layer status: {str(e)}"}


# Security Functions

async def get_tool_requires_admin(state: AgentState, tool_name: str) -> bool:
    """
    Get whether tool requires admin access.
    Checks database first, falls back to code defaults.
    """
    # 1. Check database (source of truth)
    if hasattr(state, "memory") and state.memory:
        try:
            from agent_runner.db_utils import run_query
            result = await run_query(state, """
                SELECT requires_admin FROM tool_definition 
                WHERE name = $name LIMIT 1;
            """, {"name": tool_name})
            
            if result and len(result) > 0:
                return result[0].get("requires_admin", False)
        except Exception as e:
            logger.debug(f"Failed to check tool security in DB: {e}")
    
    # 2. Fallback to code defaults
    from agent_runner.tool_security import tool_requires_admin
    return tool_requires_admin(tool_name)


async def require_admin(state: AgentState, password: Optional[str] = None) -> bool:
    """
    Check if admin access is granted.
    Returns True if admin_override_active or password matches.
    Auto-unlocks if password provided.
    """
    from agent_runner.tools.admin import _get_secret_passphrase
    secret_passphrase = await _get_secret_passphrase(state)
    
    # Check password first (allows one-time unlock)
    if password == secret_passphrase:
        import time
        state.admin_override_active = True
        state.sudo_granted_at = time.time()
        return True
    
    # Check sticky sudo
    if state.admin_override_active:
        # Verify not idle (auto-revert check)
        await state.check_and_revert_sudo()
        return state.admin_override_active
    
    return False


async def check_tool_security(
    state: AgentState,
    tool_name: str,
    password: Optional[str] = None
) -> Dict[str, Any]:
    """
    Check if tool can be executed with current permissions.
    
    Returns:
        {
            "allowed": bool,
            "requires_admin": bool,
            "reason": str,
            "hint": str
        }
    """
    requires_admin = await get_tool_requires_admin(state, tool_name)
    
    if not requires_admin:
        return {
            "allowed": True,
            "requires_admin": False,
            "reason": "",
            "hint": ""
        }
    
    # Tool requires admin - check access
    has_access = require_admin(state, password)
    
    if has_access:
        return {
            "allowed": True,
            "requires_admin": True,
            "reason": "",
            "hint": ""
        }
    else:
        return {
            "allowed": False,
            "requires_admin": True,
            "reason": f"Tool '{tool_name}' requires admin access",
            "hint": "Use unlock_session(password='lloovies') first or provide password parameter"
        }


# Quality Tier Management Tools

async def tool_set_quality_tier(state: AgentState, tier: str) -> Dict[str, Any]:
    """
    Set the system quality tier for response generation.

    This controls the trade-off between response quality and speed.
    Available tiers: fastest, fast, balanced, quality, maximum

    Args:
        tier: The quality tier to set (fastest, fast, balanced, quality, maximum)
    """
    try:
        from agent_runner.quality_tiers import QualityTier, get_tier_config, get_tier_performance_estimate

        quality_tier = QualityTier(tier.lower())
        state.set_quality_tier(quality_tier)

        config = get_tier_config(quality_tier)
        estimate = get_tier_performance_estimate(quality_tier)

        return {
            "ok": True,
            "tier": tier,
            "config": config,
            "estimated_latency_ms": estimate["latency_ms"],
            "estimated_context_tokens": estimate["context_tokens"],
            "message": f"Quality tier set to '{tier}'. Estimated latency: {estimate['latency_ms'][0]}-{estimate['latency_ms'][1]}ms"
        }
    except ValueError:
        return {
            "ok": False,
            "error": f"Invalid tier: {tier}. Must be one of: fastest, fast, balanced, quality, maximum"
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def tool_get_quality_tier(state: AgentState) -> Dict[str, Any]:
    """
    Get the current quality tier and configuration.
    """
    try:
        from agent_runner.quality_tiers import get_tier_config, get_tier_performance_estimate

        tier = state.quality_tier
        config = get_tier_config(tier)
        estimate = get_tier_performance_estimate(tier)

        return {
            "ok": True,
            "current_tier": tier.value,
            "config": config,
            "estimated_latency_ms": estimate["latency_ms"],
            "estimated_context_tokens": estimate["context_tokens"],
            "available_tiers": [t.value for t in state.quality_tier.__class__]
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def tool_get_quality_tier_comparison(state: AgentState) -> Dict[str, Any]:
    """
    Compare all quality tiers side-by-side with their configurations and performance estimates.
    """
    try:
        from agent_runner.quality_tiers import QualityTier, get_tier_config, get_tier_performance_estimate

        comparison = {}
        for tier in QualityTier:
            config = get_tier_config(tier)
            estimate = get_tier_performance_estimate(tier)
            comparison[tier.value] = {
                "config": config,
                "estimated_latency_ms": estimate["latency_ms"],
                "estimated_context_tokens": estimate["context_tokens"]
            }

        return {"ok": True, "tiers": comparison}
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def tool_save_model_preset(state: AgentState, name: str, description: Optional[str] = None) -> Dict[str, Any]:
    """
    Save the current model configuration as a named preset in the database.
    """
    try:
        from agent_runner.db_utils import run_query
        import json
        
        # 1. Collect current models
        models = {
            "AGENT_MODEL": state.agent_model,
            "ROUTER_MODEL": state.router_model,
            "TASK_MODEL": state.task_model,
            "SUMMARIZATION_MODEL": state.summarization_model,
            "VISION_MODEL": state.vision_model,
            "MCP_MODEL": state.mcp_model,
            "FINALIZER_MODEL": state.finalizer_model,
            "FALLBACK_MODEL": state.fallback_model,
            "INTENT_MODEL": state.intent_model,
            "PRUNER_MODEL": state.pruner_model,
            "HEALER_MODEL": state.healer_model,
            "CRITIC_MODEL": state.critic_model,
            "QUERY_REFINEMENT_MODEL": state.query_refinement_model
        }
        
        # 2. Check existence
        check_q = f"SELECT * FROM model_preset WHERE name = '{name}'"
        existing = await run_query(state, check_q)
        
        # Prepare the full object for CONTENT clause
        preset_data = {
            "name": name,
            "models": models,
            "description": description or "",
            "created_by": "user",
            # Dates: We let DB handle created_at default, but we should set updated_at
        }
        
        # We handle created_at/updated_at manually in logic below or let DB defaults work for create
        
        row_json = json.dumps(preset_data)
        
        if existing:
            # Update using MERGE to only update specified fields (safer than SET for objects)
            # We explicitly update the 'models' object
            q = f"UPDATE model_preset MERGE {row_json} WHERE name = '{name}'"
            logger.info(f"Saving preset UPDATE: {q}")
            await run_query(state, q)
            action = "Updated"
        else:
            # Create using CONTENT
            q = f"CREATE model_preset CONTENT {row_json}"
            logger.info(f"Saving preset CREATE: {q}")
            await run_query(state, q)
            action = "Created"

        return {
            "ok": True,
            "message": f"{action} preset '{name}' with {len(models)} model configurations.",
            "models": models
        }
    except Exception as e:
        logger.error(f"Failed to save preset: {e}")
        return {"ok": False, "error": str(e)}

async def tool_load_model_preset(state: AgentState, name: str) -> Dict[str, Any]:
    """
    Load a model configuration preset from the database and apply it.
    This updates the current runtime state AND persists changes to config_state.
    
    Args:
        name: The name of the preset to load.
    """
    try:
        from agent_runner.db_utils import run_query
        from agent_runner.config_manager import ConfigManager
        
        # 1. Fetch Preset
        results = await run_query(state, f"SELECT * FROM model_preset WHERE name = '{name}'")
        if not results:
             return {"ok": False, "error": f"Preset '{name}' not found."}
             
        preset = results[0]
        models = preset.get("models", {})
        
        if not models:
             return {"ok": False, "error": f"Preset '{name}' has no model data."}
        
        config_manager = ConfigManager(state)
        applied = []
        
        # 2. Apply and Persist
        for key, model in models.items():
            # Update Runtime (via setters which map key -> prop)
            state._update_attribute_from_config(key, model)
            
            # Update Persistence (config_state)
            await config_manager.set_config_value(key, model)
            applied.append(f"{key}: {model}")
            
        return {
            "ok": True,
            "message": f"Loaded preset '{name}'. Applied {len(applied)} changes.",
            "changes": applied
        }
    except Exception as e:
        logger.error(f"Failed to load preset: {e}")
        return {"ok": False, "error": str(e)}

async def tool_list_model_presets(state: AgentState) -> Dict[str, Any]:
    """List all available model presets."""
    try:
        from agent_runner.db_utils import run_query
        results = await run_query(state, "SELECT name, description, created_at FROM model_preset ORDER BY name ASC")
        return {"ok": True, "presets": results}
    except Exception as e:
        return {"ok": False, "error": str(e)}
