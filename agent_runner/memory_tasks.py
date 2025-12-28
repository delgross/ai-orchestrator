import asyncio
import logging
import json
from typing import Dict, Any, List
from agent_runner.state import AgentState
from common.constants import OBJ_MODEL

logger = logging.getLogger("agent_runner.memory_tasks")

async def memory_consolidation_task(state: AgentState):
    """
    Periodically fetches unconsolidated episodes and extracts facts.
    """
    logger.debug("Starting memory consolidation cycle")
    try:
        from agent_runner.tools.mcp import tool_mcp_proxy
        
        # 1. Get unconsolidated episodes
        res = await tool_mcp_proxy(state, "project-memory", "get_unconsolidated_episodes", {"limit": 5})
        if not res.get("ok"):
            return
        
        # Parse MCP Tool Result to get episodes
        episodes = []
        try:
            tool_res = res.get("result", {})
            # Check if directly in dict (unlikely via MCP) or in content text
            if "episodes" in tool_res:
                episodes = tool_res["episodes"]
            elif "content" in tool_res:
                # Standard MCP return: List of Content objects
                text = tool_res["content"][0]["text"]
                inner = json.loads(text)
                episodes = inner.get("episodes", [])
        except Exception as e:
            logger.error(f"Failed to parse episodes from memory response: {e}")
            return

        if not episodes:
            return
            
        logger.info(f"Consolidating {len(episodes)} episodes")
        
        for ep in episodes:
            request_id = ep["request_id"]
            messages = ep["messages"]
            logger.info(f"Episode {request_id} RAW Messages: {messages} (Type: {type(messages)})")
            if isinstance(messages, str):
                try: messages = json.loads(messages)
                except: pass
            
            # 2. Extract facts using LLM
            # We use a cheaper model for this background task
            logger.info(f"Episode {request_id} Messages: {messages}")
            extraction_prompt = (
                "Extract key facts from the following conversation as a JSON array of objects with "
                "'entity', 'relation', 'target', and 'context' fields. "
                "Only extract meaningful, long-term facts. If no facts are found, return an empty array [].\n\n"
                "Conversation:\n" + json.dumps(messages, indent=2)
            )
            
            client = await state.get_http_client()
            url = f"{state.gateway_base}/v1/chat/completions"
            
            # Using configured summarization model
            payload = {
                OBJ_MODEL: state.summarization_model or "ollama:mistral:latest",
                "messages": [{"role": "user", "content": extraction_prompt}],
                "response_format": {"type": "json_object"}
            }
            
            try:
                resp = await client.post(url, json=payload, timeout=60.0)
                if resp.status_code == 200:
                    data = resp.json()
                    content = data["choices"][0]["message"]["content"]
                    try:
                        fact_data = json.loads(content)
                        facts = fact_data.get("facts", []) if isinstance(fact_data, dict) else fact_data
                        
                        # 3. Store facts
                        if isinstance(facts, list):
                            for fact in facts:
                                if all(k in fact for k in ["entity", "relation", "target"]):
                                    await tool_mcp_proxy(state, "project-memory", "store_fact", {
                                        "entity": fact["entity"],
                                        "relation": fact["relation"],
                                        "target": fact["target"],
                                        "context": fact.get("context", f"Extracted from {request_id}")
                                    })
                                    
                        # 4. Mark consolidated
                        await tool_mcp_proxy(state, "project-memory", "mark_episode_consolidated", {"request_id": request_id})
                        logger.info(f"Consolidated episode {request_id}")
                    except Exception as e:
                        logger.error(f"Failed to parse extraction result for {request_id}: {e}")
            except Exception as e:
                logger.error(f"Failed to call extension model for {request_id}: {e}")
                
    except Exception as e:
        logger.error(f"Memory consolidation task error: {e}")

async def memory_backup_task(state: AgentState):
    """
    Periodically triggers a full SQL export of the database.
    """
    logger.info("Starting scheduled memory backup")
    try:
        from agent_runner.tools.mcp import tool_mcp_proxy
        res = await tool_mcp_proxy(state, "project-memory", "trigger_backup", {})
        if res.get("ok"):
            logger.info(f"Memory backup successful: {res.get('result', {}).get('message')}")
        else:
            logger.error(f"Memory backup failed: {res.get('error')}")
    except Exception as e:
        logger.error(f"Memory backup task error: {e}")

async def optimize_memory_task(state: AgentState):
    """
    Runs integrity checks and optimization on the database.
    """
    logger.debug("Starting scheduled memory optimization")
    try:
        from agent_runner.tools.mcp import tool_mcp_proxy
        res = await tool_mcp_proxy(state, "project-memory", "optimize_memory", {})
        if res.get("ok"):
            logger.debug("Memory optimization/check complete")
        else:
            logger.error(f"Memory optimization failed: {res.get('error')}")
    except Exception as e:
        logger.error(f"Memory optimization task error: {e}")
