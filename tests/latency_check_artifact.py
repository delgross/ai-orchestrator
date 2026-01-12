
import asyncio
import time
import logging
import json
import statistics
import httpx
import random
from typing import Dict, Any, List

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

async def _run_suite_background(state_ref: AgentState, request_id: str):
    """
    Background worker for latency suite.
    Writes results to Live Stream (Healer).
    """
    logger.info(f"[{request_id}] Starting Async Latency Suite...")
    
    suite = LatencySuite(state_ref)
    report = await suite.run_full_suite()
    
    # Format for Healer/Live Stream
    # We use a special marker that the Frontend/LogSorter might highlight
    summary = report["summary"]
    
    # 1. Log to generic logger (standard)
    logger.info(f"[{request_id}] Latency Result: {json.dumps(report['results'])}")
    
    # 2. Inject into Main Graph/Chat if possible. 
    # Since we can't push to Chat UI directly, we write to live_stream.md with a header.
    # The LogSorter picks this up.
    
    msg = f"""
## ⚡ System Latency Report
**Request ID:** `{request_id}`
**Time:** {time.strftime('%H:%M:%S')}

- **Router Ping:** `{report['results']['ping']:.1f} ms`
- **Embedding:** `{report['results']['embedding']:.1f} ms`
- **DB Write:** `{report['results']['db_write']:.1f} ms`
- **Chat TTFT:** `{report['results']['chat_ttft']:.1f} ms`
"""
    # Write to live stream via simple append (safe-ish) or use LogSorter if exposed
    # For now, we append to a dedicated performance log that heuristic analysis watches?
    # Or just use the existing live_stream.md path if we have write access.
    # The user is WATCHING live_stream.md.
    
    try:
        live_path = state_ref.agent_fs_root / "logs" / "live_stream.md"
        with open(live_path, "a") as f:
            f.write(f"\n{msg}\n")
    except Exception as e:
        logger.error(f"Failed to write to live_stream: {e}")

async def tool_run_latency_tests(state: AgentState, background: bool = True) -> Dict[str, Any]:
    """
    Run an integrated set of latency tests.
    
    Args:
        background: If true (default), runs asynchronously and reports to live stream.
    """
    import uuid
    req_id = str(uuid.uuid4())[:8]
    
    if background:
        tm = ServiceRegistry.get_task_manager()
        # Fire and forget
        # We need a wrapper because task manager runs periodic/scheduled tasks usually,
        # but we can also trigger one-offs.
        # Ideally we just use asyncio.create_task for a true one-off if TM doesn't support ad-hoc well yet.
        # TM.trigger_task is for registered tasks.
        # We'll just use asyncio.create_task here for simplicity.
        asyncio.create_task(_run_suite_background(state, req_id))
        
        return {
            "ok": True, 
            "message": f"Latency tests initiated (ID: {req_id}). Results will appear in the Live Stream.",
            "request_id": req_id
        }
    else:
        # Sync run
        suite = LatencySuite(state)
        report = await suite.run_full_suite()
        return {"ok": True, "report": report}

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
