
import asyncio
import logging
import subprocess
from typing import Dict, Any, List
from agent_runner.state import AgentState
from agent_runner.registry import SystemRegistry

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
        # Light instantiation (loads very small JSON, handles caching internally)
        sentinel = Sentinel(state)
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
    Set a system configuration key. Validates input against SystemRegistry.
    persist=True always.
    """
    # 1. Validate Input via Registry
    if not SystemRegistry.validate_toggle_value(key, value):
        toggle = SystemRegistry.get_toggle(key)
        valid_opts = toggle.options if toggle else "Unknown Key"
        return {"ok": False, "error": f"Invalid value '{value}' for key '{key}'. Valid options: {valid_opts}"}

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
        # We handle the import re locally to avoid polluting top level
        import re
        # Convert to strict start match, wildcard end
        safe_pattern = f"^{re.escape(command.strip())}.*"
        
        # [FIX] learn_pattern is now async for DB calls
        await sentinel.learn_pattern(safe_pattern, True, "User Override via tool_sentinel_authorize")
        
        return {"ok": True, "message": f"Pattern learned. You may now execute: {command}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

