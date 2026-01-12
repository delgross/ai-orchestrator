import logging
import json
import fcntl
import os
import contextlib
import time
from agent_runner.state import AgentState
from common.constants import OBJ_MODEL
from common.sovereign import get_sovereign_model

logger = logging.getLogger("agent_runner.memory_tasks")

@contextlib.contextmanager
def memory_lock(state: AgentState):
    """
    File-based mutex to ensure atomic memory operations.
    Prevents Backup from running during Consolidation (and vice-versa).
    """
    from pathlib import Path
    lock_path = Path(state.agent_fs_root) / "memory.lock"
    # Ensure lock file exists
    if not lock_path.exists():
        lock_path.touch()
        
    f = open(lock_path, "r+")
    try:
        # Try non-blocking first to log status
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            logger.info(f"Waiting for memory lock ({lock_path})...")
            # Blocking acquisition
            fcntl.flock(f, fcntl.LOCK_EX)
            
        logger.debug("Acquired memory lock")
        yield
    finally:
        fcntl.flock(f, fcntl.LOCK_UN)
        f.close()
        logger.debug("Released memory lock")

async def memory_consolidation_task(state: AgentState):
    """
    Periodically fetches unconsolidated episodes and extracts facts.
    """
    logger.info("Starting memory consolidation cycle")
    try:
        with memory_lock(state):
            from agent_runner.tools.mcp import tool_mcp_proxy
            
            # 1. Get unconsolidated episodes
        res = await tool_mcp_proxy(state, "project-memory", "get_unconsolidated_episodes", {"limit": 5})
        if not res.get("ok"):
            logger.error(f"Failed to get episodes: {res}")
            return
        
        # Parse MCP Tool Result to get episodes
        episodes = []
        try:
            tool_res = res.get("result", {})
            logger.info(f"DEBUG: Memory Tool Response keys: {tool_res.keys()}")
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
        
        # 2. Extract facts using Parallel Execution
        # We use a semaphore to limit concurrency to avoid rate limits
        sem = asyncio.Semaphore(10) # 10 concurrent requests
        
        async def process_episode(ep):
            async with sem:
                request_id = ep["request_id"]
                messages = ep["messages"]
                
                if isinstance(messages, str):
                    try: messages = json.loads(messages)
                    except: pass
                
                # Check for empty messages
                if not messages: return

                # Optimization: Skip very short meaningless episodes (e.g. just "hi")
                # Simple heuristic: if total content length < 10 chars, skip
                total_len = sum(len(str(m.get("content",""))) for m in messages)
                if total_len < 10:
                    logger.debug(f"Skipping episode {request_id} (too short: {total_len} chars)")
                    # Still mark as consolidated so we don't re-process
                    await tool_mcp_proxy(state, "project-memory", "mark_episode_consolidated", {"request_id": request_id})
                    return

                logger.debug(f"Extracting facts from episode {request_id}")
                extraction_prompt = (
                    "Extract key facts from the following conversation as a JSON array of objects with "
                    "'entity', 'relation', 'target', and 'context' fields. "
                    "Only extract meaningful, long-term facts. If no facts are found, return an empty array [].\n\n"
                    "Conversation:\n" + json.dumps(messages, indent=2)
                )
                
                try:
                    client = await state.get_http_client()
                    url = f"{state.gateway_base}/v1/chat/completions"
                    
                    payload = {
                        # [SOVEREIGN] Use centralized model for summarization
                        OBJ_MODEL: get_sovereign_model("summarizer", "ollama:mistral:latest"),
                        "messages": [{"role": "user", "content": extraction_prompt}],
                        "response_format": {"type": "json_object"}
                    }

                    resp = await client.post(url, json=payload, timeout=60.0)
                    if resp.status_code == 200:
                        data = resp.json()
                        content = data["choices"][0]["message"]["content"]
                        try:
                            # Handle potential non-JSON output wrappers
                            if "```json" in content:
                                content = content.split("```json")[1].split("```")[0]
                            elif "```" in content:
                                content = content.split("```")[1].split("```")[0]
                                
                            fact_data = json.loads(content)
                            facts = fact_data.get("facts", []) if isinstance(fact_data, dict) else fact_data
                            
                            if isinstance(facts, list) and facts:
                                count = 0
                                for fact in facts:
                                    if all(k in fact for k in ["entity", "relation", "target"]):
                                        await tool_mcp_proxy(state, "project-memory", "store_fact", {
                                            "entity": fact["entity"],
                                            "relation": fact["relation"],
                                            "target": fact["target"],
                                            "context": fact.get("context", f"Extracted from {request_id}")
                                        })
                                        count += 1
                                logger.info(f"Episode {request_id}: Extracted {count} facts")
                            else:
                                logger.debug(f"Episode {request_id}: No facts found")
                                
                        except Exception as e:
                            logger.warning(f"Failed to parse extraction result for {request_id}: {e}")
                    else:
                        logger.warning(f"Model error for {request_id}: {resp.status_code} - {resp.text}")

                except Exception as e:
                    logger.error(f"Failed to process episode {request_id}: {e}")
                
                # Always mark consolidated on success or non-retryable error to progress queue
                try:
                    await tool_mcp_proxy(state, "project-memory", "mark_episode_consolidated", {"request_id": request_id})
                except Exception as e:
                    logger.error(f"Failed to mark episode {request_id} consolidated: {e}")

        # Execute parallel batch
        import asyncio
        await asyncio.gather(*(process_episode(ep) for ep in episodes))
        logger.info(f"Consolidation cycle complete. Processed {len(episodes)} episodes.")

    except Exception as e:
        logger.error(f"Memory consolidation task error: {e}")

async def memory_backup_task(state: AgentState):
    """
    Periodically triggers a full SQL export of the database.
    """
    logger.info("Starting scheduled memory backup")
    try:
        with memory_lock(state):
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
        with memory_lock(state):
            from agent_runner.tools.mcp import tool_mcp_proxy
            res = await tool_mcp_proxy(state, "project-memory", "optimize_memory", {})
            if res.get("ok"):
                logger.debug("Memory optimization/check complete")
            else:
                logger.error(f"Memory optimization failed: {res.get('error')}")
    except Exception as e:
        logger.error(f"Memory optimization task error: {e}")

async def memory_audit_task(state: AgentState):
    """
    Reflective task: Periodic review of known facts.
    Cross-references existing facts with the deep knowledge base (RAG) to update confidence.
    """
    logger.info("Starting memory audit cycle")
    try:
        with memory_lock(state):
            from agent_runner.tools.mcp import tool_mcp_proxy
            from agent_runner.engine import AgentEngine
            
            # 1. Fetch facts that aren't yet 'Ground Truth' (confidence < 0.9)
            # We fetch a small batch to avoid overloading
            res = await tool_mcp_proxy(state, "project-memory", "query_facts", {"limit": 10})
            if not res.get("ok"): return
        
        facts = []
        try:
            tool_res = res.get("result", {})
            if "facts" in tool_res:
                facts = tool_res["facts"]
            elif "content" in tool_res:
                text = tool_res["content"][0]["text"]
                facts = json.loads(text).get("facts", [])
        except: return
        
        if not facts: return
        
        engine = AgentEngine(state)
        
        for fact in facts:
            fact_id = fact.get("id")
            entity = fact.get("entity")
            relation = fact.get("relation")
            target = fact.get("target")
            current_conf = fact.get("confidence", 0.5)
            
            # Skip ground truth
            if current_conf >= 0.95: continue
            
            # 2. Cross-reference with RAG
            query = f"Is it true that {entity} {relation} {target}?"
            rag_res = await engine.tool_knowledge_search(state, query)
            
            if rag_res.get("ok") and rag_res.get("context_found"):
                # Use LLM to judge the alignment
                verification_prompt = (
                    "Context from documents:\n" + rag_res["context_found"] + "\n\n"
                    f"Proposition: {entity} {relation} {target}\n\n"
                    "Based ON THE CONTEXT ONLY, is this proposition:\n"
                    "1. SUPPORTED (Found direct evidence)\n"
                    "2. CONTRADICTED (Found conflicting information)\n"
                    "3. UNKNOWN (Not mentioned)\n\n"
                    "Return ONLY a JSON object: {'judgment': 'SUPPORTED'|'CONTRADICTED'|'UNKNOWN', 'reasoning': '...'}"
                )
                
                client = await state.get_http_client()
                url = f"{state.gateway_base}/v1/chat/completions"
                # UPGRADE: Use Sovereign Auditor (High-End/H100)
                payload = {
                    "model": get_sovereign_model("auditor", "openai:gpt-4o"),
                    "messages": [{"role": "user", "content": verification_prompt}],
                    "response_format": {"type": "json_object"}
                }
                
                try:
                    v_resp = await client.post(url, json=payload, timeout=30.0)
                    if v_resp.status_code == 200:
                        v_data = v_resp.json()
                        judgment_data = json.loads(v_data["choices"][0]["message"]["content"])
                        judgment = judgment_data.get("judgment")
                        
                        new_conf = current_conf
                        if judgment == "SUPPORTED":
                            new_conf = min(0.9, current_conf + 0.1) # Boost
                            logger.info(f"AUDIT: Fact '{entity} {relation}' SUPPORTED by RAG. New confidence: {new_conf:.2f}")
                        elif judgment == "CONTRADICTED":
                            new_conf = max(0.1, current_conf - 0.3) # Heavy Penalty
                            logger.warning(f"AUDIT: Fact '{entity} {relation}' CONTRADICTED by RAG. New confidence: {new_conf:.2f}")
                        
                        # Apply update if changed
                        if new_conf != current_conf:
                            # We can use store_fact to update (it uses upsert logic)
                            await tool_mcp_proxy(state, "project-memory", "store_fact", {
                                "entity": entity,
                                "relation": relation,
                                "target": target,
                                "context": fact.get("context", ""),
                                "confidence": new_conf
                            })
                except Exception as e:
                    logger.error(f"Audit verification failed for fact {fact_id}: {e}")
                    
    except Exception as e:
        logger.error(f"Memory audit task error: {e}")
