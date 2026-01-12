"""
Comprehensive Chat Interface Latency Testing

Tests the entire chat pipeline and breaks down latency by component.
"""

import logging
import time
import asyncio
from typing import Dict, Any, List, Optional
import httpx
from agent_runner.state import AgentState

logger = logging.getLogger("agent_runner.tools.chat_latency_test")


async def tool_run_chat_latency_test(
    state: AgentState,
    iterations: int = 5,
    test_message: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run comprehensive latency tests on the chat interface.
    
    Tests:
    - Router latency (query analysis, model selection)
    - Agent latency (system prompt generation, tool discovery)
    - MCP latency (tool execution)
    - Database latency (queries, fact storage)
    - Network latency (HTTP requests)
    - End-to-end latency (full chat cycle)
    
    Returns detailed breakdown by component.
    """
    try:
        if not test_message:
            test_message = "What is the weather today?"
        
        logger.info(f"Starting chat latency test ({iterations} iterations)...")
        
        results = {
            "iterations": iterations,
            "test_message": test_message,
            "components": {},
            "end_to_end": [],
            "summary": {}
        }
        
        # Component timings
        router_times = []
        agent_times = []
        mcp_times = []
        db_times = []
        network_times = []
        e2e_times = []
        
        for i in range(iterations):
            iteration_start = time.time()
            
            # 1. Router Latency
            router_start = time.time()
            router_latency = await _test_router_latency(state, test_message)
            router_times.append((time.time() - router_start) * 1000)
            results["components"]["router"] = router_latency
            
            # 2. Agent Latency
            agent_start = time.time()
            agent_latency = await _test_agent_latency(state, test_message)
            agent_times.append((time.time() - agent_start) * 1000)
            results["components"]["agent"] = agent_latency
            
            # 3. MCP Latency
            mcp_start = time.time()
            mcp_latency = await _test_mcp_latency(state)
            mcp_times.append((time.time() - mcp_start) * 1000)
            results["components"]["mcp"] = mcp_latency
            
            # 4. Database Latency
            db_start = time.time()
            db_latency = await _test_database_latency(state)
            db_times.append((time.time() - db_start) * 1000)
            results["components"]["database"] = db_latency
            
            # 5. Network Latency
            network_start = time.time()
            network_latency = await _test_network_latency(state)
            network_times.append((time.time() - network_start) * 1000)
            results["components"]["network"] = network_latency
            
            # 6. End-to-End Latency
            e2e_start = time.time()
            e2e_latency = await _test_end_to_end_latency(state, test_message)
            e2e_times.append((time.time() - e2e_start) * 1000)
            
            iteration_duration = (time.time() - iteration_start) * 1000
            results["end_to_end"].append({
                "iteration": i + 1,
                "total_ms": iteration_duration,
                "breakdown": {
                    "router": router_times[-1],
                    "agent": agent_times[-1],
                    "mcp": mcp_times[-1],
                    "database": db_times[-1],
                    "network": network_times[-1]
                }
            })
            
            # Small delay between iterations
            await asyncio.sleep(0.5)
        
        # Calculate statistics
        def calc_stats(times: List[float]) -> Dict[str, float]:
            if not times:
                return {"min": 0, "max": 0, "avg": 0, "median": 0}
            sorted_times = sorted(times)
            return {
                "min": min(times),
                "max": max(times),
                "avg": sum(times) / len(times),
                "median": sorted_times[len(sorted_times) // 2]
            }
        
        results["summary"] = {
            "router": calc_stats(router_times),
            "agent": calc_stats(agent_times),
            "mcp": calc_stats(mcp_times),
            "database": calc_stats(db_times),
            "network": calc_stats(network_times),
            "end_to_end": calc_stats(e2e_times)
        }
        
        # Identify bottlenecks
        avg_times = {
            "router": results["summary"]["router"]["avg"],
            "agent": results["summary"]["agent"]["avg"],
            "mcp": results["summary"]["mcp"]["avg"],
            "database": results["summary"]["database"]["avg"],
            "network": results["summary"]["network"]["avg"]
        }
        
        total_avg = sum(avg_times.values())
        bottlenecks = []
        for component, avg_time in sorted(avg_times.items(), key=lambda x: x[1], reverse=True):
            percentage = (avg_time / total_avg * 100) if total_avg > 0 else 0
            if percentage > 20:  # More than 20% of total time
                bottlenecks.append({
                    "component": component,
                    "avg_ms": avg_time,
                    "percentage": percentage
                })
        
        results["bottlenecks"] = bottlenecks
        results["ok"] = True
        
        logger.info(f"Chat latency test complete. Bottlenecks: {[b['component'] for b in bottlenecks]}")
        
        return results
    except Exception as e:
        logger.error(f"Chat latency test failed: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}


async def _test_router_latency(state: AgentState, message: str) -> Dict[str, Any]:
    """Test router component latency."""
    try:
        from agent_runner.router_analyzer import analyze_query
        
        start = time.time()
        
        # Test router analysis
        analysis = await analyze_query(
            query=message,
            messages=[{"role": "user", "content": message}],
            gateway_base=state.gateway_base,
            http_client=await state.get_http_client(),
            memory_server=state.memory if hasattr(state, "memory") else None
        )
        
        latency_ms = (time.time() - start) * 1000
        
        return {
            "latency_ms": latency_ms,
            "analysis_time": latency_ms,
            "query_type": analysis.query_type if hasattr(analysis, "query_type") else "unknown",
            "complexity": analysis.complexity if hasattr(analysis, "complexity") else "unknown"
        }
    except Exception as e:
        logger.debug(f"Router latency test error: {e}")
        return {"latency_ms": 0, "error": str(e)}


async def _test_agent_latency(state: AgentState, message: str) -> Dict[str, Any]:
    """Test agent component latency."""
    try:
        from agent_runner.service_registry import ServiceRegistry
        
        engine = ServiceRegistry.get_engine()
        if not engine:
            return {"latency_ms": 0, "error": "Engine not available"}
        
        # Test system prompt generation
        prompt_start = time.time()
        system_prompt = await engine.get_system_prompt([{"role": "user", "content": message}])
        prompt_time = (time.time() - prompt_start) * 1000
        
        # Test tool discovery
        tools_start = time.time()
        tools = await engine.get_all_tools([{"role": "user", "content": message}])
        tools_time = (time.time() - tools_start) * 1000
        
        total_latency = prompt_time + tools_time
        
        return {
            "latency_ms": total_latency,
            "prompt_generation_ms": prompt_time,
            "tool_discovery_ms": tools_time,
            "tool_count": len(tools)
        }
    except Exception as e:
        logger.debug(f"Agent latency test error: {e}")
        return {"latency_ms": 0, "error": str(e)}


async def _test_mcp_latency(state: AgentState) -> Dict[str, Any]:
    """Test MCP server latency."""
    try:
        # Test a simple MCP call (time server is usually fast)
        if "time" not in state.mcp_servers:
            return {"latency_ms": 0, "error": "Time server not available"}
        
        from agent_runner.tools.mcp import tool_mcp_proxy
        
        start = time.time()
        result = await tool_mcp_proxy(state, "time", "get_time", {})
        latency_ms = (time.time() - start) * 1000
        
        return {
            "latency_ms": latency_ms,
            "success": result.get("ok", False),
            "server": "time"
        }
    except Exception as e:
        logger.debug(f"MCP latency test error: {e}")
        return {"latency_ms": 0, "error": str(e)}


async def _test_database_latency(state: AgentState) -> Dict[str, Any]:
    """Test database query latency."""
    try:
        if not hasattr(state, "memory") or not state.memory:
            return {"latency_ms": 0, "error": "Memory server not available"}
        
        await state.memory.ensure_connected()
        
        from agent_runner.db_utils import run_query
        # Test simple query
        start = time.time()
        result = await run_query(state, "SELECT count() FROM fact;")
        query_time = (time.time() - start) * 1000
        
        # Test complex query
        complex_start = time.time()
        complex_result = await run_query(
            state,
            "SELECT * FROM fact WHERE entity = 'test' LIMIT 10;"
        )
        complex_time = (time.time() - complex_start) * 1000
        
        return {
            "latency_ms": query_time,
            "simple_query_ms": query_time,
            "complex_query_ms": complex_time,
            "fact_count": result[0].get("count", 0) if result else 0
        }
    except Exception as e:
        logger.debug(f"Database latency test error: {e}")
        return {"latency_ms": 0, "error": str(e)}


async def _test_network_latency(state: AgentState) -> Dict[str, Any]:
    """Test network/HTTP latency."""
    try:
        client = await state.get_http_client()
        
        # Test local gateway
        gateway_start = time.time()
        try:
            response = await client.get(f"{state.gateway_base}/health", timeout=2.0)
            gateway_time = (time.time() - gateway_start) * 1000
            gateway_success = response.status_code == 200
        except Exception:
            gateway_time = 0
            gateway_success = False
        
        # Test external (if internet available)
        external_time = 0
        external_success = False
        if state.internet_available:
            external_start = time.time()
            try:
                response = await client.get("https://www.google.com", timeout=2.0)
                external_time = (time.time() - external_start) * 1000
                external_success = response.status_code == 200
            except Exception:
                external_time = 0
        
        return {
            "latency_ms": gateway_time,
            "gateway_ms": gateway_time,
            "gateway_success": gateway_success,
            "external_ms": external_time,
            "external_success": external_success
        }
    except Exception as e:
        logger.debug(f"Network latency test error: {e}")
        return {"latency_ms": 0, "error": str(e)}


async def _test_end_to_end_latency(state: AgentState, message: str) -> Dict[str, Any]:
    """Test full end-to-end chat latency."""
    try:
        from agent_runner.service_registry import ServiceRegistry
        
        engine = ServiceRegistry.get_engine()
        if not engine:
            return {"latency_ms": 0, "error": "Engine not available"}
        
        # Simulate a minimal chat cycle
        start = time.time()
        
        # Get tools
        tools = await engine.get_all_tools([{"role": "user", "content": message}])
        
        # Get system prompt
        system_prompt = await engine.get_system_prompt([{"role": "user", "content": message}])
        
        # Simulate one tool call (if needed)
        # This is a simplified test - full cycle would include LLM call
        
        latency_ms = (time.time() - start) * 1000
        
        return {
            "latency_ms": latency_ms,
            "tools_loaded": len(tools),
            "prompt_generated": len(system_prompt) > 0
        }
    except Exception as e:
        logger.debug(f"End-to-end latency test error: {e}")
        return {"latency_ms": 0, "error": str(e)}







