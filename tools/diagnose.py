
import asyncio
import sys
import os
import json
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from agent_runner.system_control_server import SystemControlServer
from agent_runner.memory_server import MemoryServer

# ANSI Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def print_status(component, status, details=None):
    color = GREEN if status == "ONLINE" or status == "PASS" else RED
    print(f"{component:<20} [{color}{status}{RESET}] {details or ''}")

async def main():
    print(f"\n{YELLOW}=== Antigravity System Diagnostic ==={RESET}\n")
    
    # 1. System Health (via SystemControl)
    ctrl = SystemControlServer()
    print(f"{YELLOW}1. Infrastructure Health:{RESET}")
    try:
        health = await ctrl.get_system_health()
        
        # Router
        router = health.get("router", {})
        r_status = "ONLINE" if router.get("status") == "online" else "OFFLINE"
        print_status("Router", r_status, router.get("error"))
        
        # Agent Runner
        # Check for new schema (direct healthy response) or legacy schema
        if health.get("status") == "healthy":
            runner = {"status": "online", "details": health}
            # In new schema, we might not have explicit router status unless we fetch it separately
            # For now, mark router as UNKNOWN or assume online if runner is up
            if router == {}: router = {"status": "UNKNOWN", "error": "Not reported in detailed view"}
        else:
            runner = health.get("agent_runner", {})

        a_status = "ONLINE" if runner.get("status") in ["online", "healthy"] else "OFFLINE"
        print_status("Agent Runner", a_status, runner.get("error"))
        
        # Topology
        if "detailed_health" in runner.get("details", {}):
            topo = runner["details"]["detailed_health"]
            print(f"   - Function Registry: {len(topo.get('tools', []))} tools")
            print(f"   - Periodic Tasks: {len(topo.get('tasks', []))} active")
            
    except Exception as e:
        print_status("Health Check", "FAIL", str(e))

    # 2. Memory Backlog (Direct DB Check)
    print(f"\n{YELLOW}2. Memory System:{RESET}")
    try:
        mem = MemoryServer()
        await mem.ensure_connected()
        
        # Backlog
        uncon_res = await mem._execute_query("SELECT count() FROM episode WHERE consolidated = false GROUP ALL")
        backlog = uncon_res[0].get("count", 0) if uncon_res else 0
        
        msg = f"{backlog} pending episodes"
        status = "PASS" if backlog < 1000 else "WARN" 
        print_status("Backlog", status, msg)
        
        # Facts
        fact_res = await mem._execute_query("SELECT count() FROM fact GROUP ALL")
        facts = fact_res[0].get("count", 0) if fact_res else 0
        print_status("Knowledge Base", "INFO", f"{facts} total facts")
        
    except Exception as e:
         print_status("Memory DB", "FAIL", str(e))

    # 3. Recent Errors (Log Scan)
    print(f"\n{YELLOW}3. Recent Critical Errors (Last 50 lines):{RESET}")
    try:
        res = await ctrl.read_service_logs("agent_runner", lines=50)
        logs = res.get("content", "").splitlines()
        errors = [l for l in logs if "ERROR" in l or "CRITICAL" in l]
        
        if not errors:
            print_status("Error Logs", "CLEAN", "No recent errors found.")
        else:
            print(f"{RED}Found {len(errors)} recent errors:{RESET}")
            for err in errors[-3:]: # Show last 3
                print(f"   - {err}")
    except Exception as e:
        print_status("Log Reader", "FAIL", str(e))

    print(f"\n{YELLOW}=== Diagnostic Complete ==={RESET}\n")

if __name__ == "__main__":
    asyncio.run(main())
