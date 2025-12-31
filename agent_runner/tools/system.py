
import asyncio
import logging
import subprocess
from typing import Dict, Any, List
from agent_runner.state import AgentState

logger = logging.getLogger("agent_runner.tools.system")

async def tool_run_command(state: AgentState, command: str, background: bool = False) -> Dict[str, Any]:
    """
    Run a shell command in the agent's environment.
    
    Args:
        command: The shell command to execute.
        background: If true, run in background (fire and forget-ish).
    """
    if not state.config.get("agent_runner", {}).get("enable_command_execution", False):
        return {"ok": False, "error": "Command execution is disabled in configuration."}
        
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
            
            return {
                "ok": process.returncode == 0,
                "returncode": process.returncode,
                "stdout": stdout.decode("utf-8", errors="replace"),
                "stderr": stderr.decode("utf-8", errors="replace"),
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
