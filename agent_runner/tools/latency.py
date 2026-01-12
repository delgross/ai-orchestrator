
import asyncio
import time
import logging
import json
import statistics
import httpx
import random
from typing import Dict, Any, List, Optional

from agent_runner.state import AgentState
from agent_runner.service_registry import ServiceRegistry
from common.sovereign import get_sovereign_model

logger = logging.getLogger("agent_runner.tools.latency")

class LatencySuite:
    """
    Unified Latency Testing logic.
    Propagates metrics to logs and eventually to the dashboard/chat.
    """
    def __init__(self, state: AgentState):
        self.state = state
        self.gateway_base = state.gateway_base
        # Default fallback if config missing
        self.surreal_url = "http://127.0.0.1:8000/sql"
        self.ns = "antigravity"
        self.db = "brain"
        self.auth = ("root", "root")

    async def run_full_suite(self) -> Dict[str, Any]:
        """Run all tests and return report."""
        report = {
            "timestamp": time.time(),
            "results": {},
            "summary": ""
        }
        
        # 1. PING (Router Roundtrip)
        report["results"]["ping"] = await self.test_ping()
        
        # 2. EMBEDDING (Model Latency)
        report["results"]["embedding"] = await self.test_embedding()
        
        # 3. DB WRITE (Surreal)
        report["results"]["db_write"] = await self.test_db_write()
        
        # 4. CHAT (Token Generation)
        report["results"]["chat_ttft"] = await self.test_chat_ttft()
        
        # Summary
        p = report["results"]["ping"]
        e = report["results"]["embedding"]
        d = report["results"]["db_write"]
        c = report["results"]["chat_ttft"]
        
        summary = (
            f"Latency Report:\n"
            f"- Router Ping: {p:.1f}ms\n"
            f"- Embedding: {e:.1f}ms\n"
            f"- DB Write:  {d:.1f}ms\n"
            f"- Chat TTFT: {c:.1f}ms\n"
        )
        report["summary"] = summary
        
        return report

    async def test_ping(self) -> float:
        """Measure basic HTTP roundtrip to Router."""
        try:
            start = time.perf_counter()
            async with httpx.AsyncClient() as client:
                await client.get(f"{self.gateway_base}/health", timeout=2.0)
            return (time.perf_counter() - start) * 1000
        except Exception as e:
            logger.error(f"Ping failed: {e}")
            return -1.0

    async def test_embedding(self) -> float:
        """Measure embedding generation time."""
        try:
            # Requires 'mxbai-embed-large' or configured model
            # Use Sovereign model for 'healer' or 'memory' if possible, or hardcode typical
            model = "mxbai-embed-large" 
            text = "Latency check payload."
            
            start = time.perf_counter()
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self.state.router_auth_token}"} if self.state.router_auth_token else {}
                await client.post(
                    f"{self.gateway_base}/v1/embeddings", 
                    json={"input": text, "model": model}, 
                    headers=headers,
                    timeout=5.0
                )
            return (time.perf_counter() - start) * 1000
        except Exception:
            return -1.0

    async def test_db_write(self) -> float:
        """Measure SurrealDB write latency."""
        try:
            # We assume local for now, or fetch from config
            # config = self.state.config...
            sql = "RETURN time::now();"
            start = time.perf_counter()
            async with httpx.AsyncClient() as client:
                await client.post(
                    self.surreal_url,
                    data=sql,
                    auth=self.auth,
                    headers={"Accept": "application/json", "NS": self.ns, "DB": self.db},
                    timeout=2.0
                )
            return (time.perf_counter() - start) * 1000
        except Exception:
            return -1.0

    async def test_chat_ttft(self) -> float:
        """Measure Time To First Token for Chat."""
        try:
            # Use 'agent:mcp' to verify Agent Runner connectivity
            model = "agent:mcp"
            start = time.perf_counter()
            ttft = None
            
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self.state.router_auth_token}"} if self.state.router_auth_token else {}
                async with client.stream(
                    "POST", 
                    f"{self.gateway_base}/v1/chat/completions",
                    json={"model": model, "messages": [{"role": "user", "content": "ping"}], "stream": True},
                    headers=headers,
                    timeout=10.0
                ) as response:
                    async for chunk in response.aiter_bytes():
                        ttft = time.perf_counter()
                        break # Got first chunk
            
            if ttft:
                return (ttft - start) * 1000
            return (time.perf_counter() - start) * 1000 # Fallback total
        except Exception:
            return -1.0

    async def test_ingestor(self) -> Dict[str, Any]:
        """Check status of Knowledge Ingestion (Vector DB)."""
        try:
            # simple check: count vectors in the 'vectors' table
            sql = "SELECT count() FROM vectors GROUP ALL;"
            start = time.perf_counter()
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    self.surreal_url,
                    data=sql,
                    auth=self.auth,
                    headers={"Accept": "application/json", "NS": self.ns, "DB": self.db},
                    timeout=2.0
                )
            duration = (time.perf_counter() - start) * 1000
            
            count = 0
            if resp.status_code == 200:
                data = resp.json()
                # Parse Surreal Result "result": [{"count": 123}] or similar
                # data list -> item -> result -> list -> item -> count
                if data and isinstance(data, list) and data[0].get("status") == "OK":
                     res = data[0].get("result", [])
                     if res:
                         count = res[0].get("count", 0)
            
            return {
                "ok": True,
                "vector_count": count,
                "latency_ms": duration
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

    async def test_dashboard_load(self) -> float:
        """Measure Frontend Load Time."""
        try:
            start = time.perf_counter()
            async with httpx.AsyncClient() as client:
                await client.get(f"{self.gateway_base}/v2/index.html", timeout=2.0)
            return (time.perf_counter() - start) * 1000
        except:
            return -1.0

async def _run_investigation_background(state_ref: AgentState, request_id: str, components: List[str]):
    """Background worker for detailed investigation."""
    logger.info(f"[{request_id}] Starting System Investigation: {components}")
    
    suite = LatencySuite(state_ref)
    results = {}
    report_lines = []
    
    # 1. LATENCY (Router/Model/DB)
    if "latency" in components:
        report_lines.append("### ⚡ Latency Metrics")
        # Ping
        ping = await suite.test_ping()
        results["ping"] = ping
        report_lines.append(f"- **Router Ping**: `{ping:.1f}ms`")
        
        # Embedding
        emb = await suite.test_embedding()
        results["embedding"] = emb
        report_lines.append(f"- **Embedding**: `{emb:.1f}ms`")
        
        # DB Write
        dbw = await suite.test_db_write()
        results["db_write"] = dbw
        report_lines.append(f"- **DB Write**: `{dbw:.1f}ms`")
        
        # Chat TTFT
        ttft = await suite.test_chat_ttft()
        results["chat_ttft"] = ttft
        report_lines.append(f"- **Chat TTFT**: `{ttft:.1f}ms`")
    
    # 2. INGESTOR (Memory)
    if "ingestor" in components:
        report_lines.append("\n### 🧠 Knowledge Ingestion")
        ing = await suite.test_ingestor()
        results["ingestor"] = ing
        if ing.get("ok"):
             report_lines.append(f"- **Vector Count**: `{ing.get('vector_count', 0):,}`")
             report_lines.append(f"- **Check Latency**: `{ing.get('latency_ms', 0):.1f}ms`")
        else:
             report_lines.append(f"- **Status**: 🔴 Error ({ing.get('error')})")

    # 3. DASHBOARD (Frontend)
    if "dashboard" in components:
        dash = await suite.test_dashboard_load()
        results["dashboard_load"] = dash
        report_lines.append(f"\n- **Dashboard Load**: `{dash:.1f}ms`")

    # 4. MCP HEALTH (Availability)
    if "mcp" in components:
        from agent_runner.health_monitor import MCP_SERVERS, check_mcp_server_health
        report_lines.append("\n### 🔌 MCP Services")
        
        # We assume health monitor is initialized global-ish or we access via state if linked
        # Ideally we re-use the check functions directly if capable
        # Simple check for now:
        for name in MCP_SERVERS.keys():
             h = await check_mcp_server_health(name)
             icon = "🟢" if h.get("ok") else "🔴"
             report_lines.append(f"- {icon} **{name}**: {'OK' if h.get('ok') else h.get('error')}")

    # 5. ZOMBIES (Runaways)
    if "zombies" in components:
        # We can re-use the check logic, but we need to return it instead of just logging
        # For investigation, we just SCAN
        report_lines.append("\n### 🧟 Zombie Processes")
        # Inline scan logic for report (simplified version of monitor)
        try:
             cmd = "ps -eo pid,etime,command | grep 'curl' | grep 'admin/mcp' | grep -v grep"
             proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
             stdout, _ = await proc.communicate()
             lines = stdout.decode().splitlines()
             if lines:
                 report_lines.append(f"- ⚠️ **Found {len(lines)} potential zombies**")
                 for l in lines[:3]: # limit output
                      report_lines.append(f"  - `{l.strip()}`")
             else:
                 report_lines.append("- ✅ No stuck processes found.")
        except Exception:
             report_lines.append("- ❓ Check failed.")

    # PUBLISH
    msg = f"""
## 🕵️ System Investigation Report
**Request ID:** `{request_id}`
**Scope:** `{', '.join(components)}`
**Time:** {time.strftime('%H:%M:%S')}

{chr(10).join(report_lines)}
"""
    
    try:
        live_path = state_ref.agent_fs_root / "logs" / "live_stream.md"
        with open(live_path, "a") as f:
            f.write(f"\n{msg}\n")
    except Exception as e:
        logger.error(f"Failed to write to live_stream: {e}")


async def tool_investigate_system_performance(
    state: AgentState, 
    components: List[str] = None, 
    background: bool = True
) -> Dict[str, Any]:
    """
    Run a granular investigation of system subsystems.
    
    Args:
        components: List[str]. Options: ["latency", "mcp", "ingestor", "zombies", "dashboard"]. 
                   If None, runs ALL.
        background: If True (default), runs async and reports to Live Stream.
    """
    valid_opts = ["latency", "mcp", "ingestor", "zombies", "dashboard"]
    
    # Default to ALL if not specified
    if not components:
        components = valid_opts
    
    # Validate
    components = [c.lower() for c in components if c.lower() in valid_opts]
    if not components:
        return {"ok": False, "error": f"No valid components specified. Options: {valid_opts}"}

    import uuid
    req_id = str(uuid.uuid4())[:8]
    
    if background:
        # Fire and forget
        asyncio.create_task(_run_investigation_background(state, req_id, components))
        
        return {
            "ok": True, 
            "message": f"Investigation started for {components}. Watch the Live Stream.",
            "request_id": req_id
        }
    else:
        # Sync run (not fully implemented for report return, simpler to force background for now for consistent reporting)
        # But for Agent use, maybe they want the JSON?
        # Let's support background mostly.
        asyncio.create_task(_run_investigation_background(state, req_id, components))
        return {"ok": True, "message": "Investigation started (Async enforced for heavy tools)."}

async def tool_run_chat_latency_test(state: AgentState, iterations: int = 5, test_message: Optional[str] = None) -> Dict[str, Any]:
    """Run comprehensive chat interface latency test."""
    from agent_runner.tools.chat_latency_test import tool_run_chat_latency_test as _run_test
    return await _run_test(state, iterations, test_message)

# Alias for backward compatibility if needed, or just remove
# We keep it but route to new logic
async def tool_run_latency_tests(state: AgentState, background: bool = True) -> Dict[str, Any]:
    """Legacy alias for Latency checks."""
    return await tool_investigate_system_performance(state, components=["latency"], background=background)


if __name__ == "__main__":
    # Minimal mock state for CLI testing
    class MockState:
        gateway_base = "http://127.0.0.1:5455"
        router_auth_token = None
    
    import asyncio
    
    async def run():
        print("Running Latency Suite...")
        suite = LatencySuite(MockState())
        report = await suite.run_full_suite()
        print(json.dumps(report, indent=2))
        print("\n" + report["summary"])

    asyncio.run(run())
