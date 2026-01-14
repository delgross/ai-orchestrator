import json
import logging
import time
from typing import Any, Dict, List
import httpx
import re

logger = logging.getLogger("agent_runner.intent")
from agent_runner.db_utils import run_query

_intent_cache = {}

def extract_text_content(content: Any) -> str:
    """Extract plain text from potential list-based content (common in advanced clients)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        # Extract text from blocks like [{'type': 'text', 'text': 'hi'}]
        return " ".join([str(block.get("text", "")) for block in content if isinstance(block, dict) and block.get("type") == "text"])
    return str(content)

async def classify_search_intent(query: str, state: Any, tool_menu_summary: str, advice_menu_list: List[str] = None) -> Dict[str, Any]:
    """Classify query and select relevant toolsets using the 'Maître d' Menu' & Advice Registry."""
    
    # Store query for maître d' learning system
    if hasattr(state, 'last_user_query'):
        state.last_user_query = query

    # [OPTIMIZATION] RAM Cache to prevent Double-Calling Maître d' (Nexus + ToolSelector)
    # We cache intent for 5 seconds to cover the request lifecycle.
    cache_key = f"{query}::{state.intent_model}"
    global _intent_cache
    if cache_key in _intent_cache:
        timestamp, cached_result = _intent_cache[cache_key]
        if time.time() - timestamp < 5.0:
            logger.info(f"Maître d' Cache HIT: Reusing decision_keys: {list(cached_result.keys())}")
            return cached_result
    
    # Prune Cache (Simple)
    if len(_intent_cache) > 100:
        _intent_cache.clear()

    if not tool_menu_summary:
        # Fallback if discovery hasn't run
        return {"target_servers": [], "notes": "No menu available"}

    from agent_runner.feedback import get_suggested_servers

    # [FEATURE-VEHICLE] Semantic Tool Search (Vector Router)
    # Replaces static constraint patching with dynamic retrieval
    vector_results = []
    vector_context_str = ""
    try:
        if hasattr(state, "vector_store") and state.vector_store:
            # We search for potentially relevant tools
            # "limit=3" ensures we only fetch high-signal tools
            vector_results = await state.vector_store.search_tools(query, limit=5)
            if vector_results:
                vector_context_str = "Relevant Tools Found via Search:\n"
                for tool in vector_results:
                    vector_context_str += f"- {tool['name']}: {tool['description']}\n"
                vector_context_str += "\n"
                logger.info(f"Vector Router found tools: {[t['name'] for t in vector_results]}")
    except Exception as e:
        logger.warning(f"Vector search failed: {e}")

    # [FEATURE-9] Learning Loop: Inject suggestions from history
    suggestions_str = ""
    # try:
    #     suggestions = await get_suggested_servers(query, state=state)
    #     if suggestions:
    #         # We limit to top 3 to avoid bias
    #         suggestions_str = f"Recall: User usage history suggests these servers are relevant: {', '.join(suggestions[:3])}\n"
    # except Exception as e:
    #     logger.debug(f"Maître d' suggestion retrieval failed: {e}")
        
    # [FEATURE-ADVICE] Advice Menu
    advice_str = ""
    # if advice_menu_list:
    #     advice_str = (
    #         "Available Advice Topics:\n"
    #         f"- {', '.join(advice_menu_list)}\n\n"
    #     )
    
    # We prepend dynamic vector results to the static menu
    # This allows the Maître d' to see relevant tools that might not be in the static summary
    combined_menu = f"{vector_context_str}{tool_menu_summary}"

    # [UNIVERSAL CONTEXT] Inject Time/Location so Maître d' makes context-aware decisions
    import datetime
    try:
        current_time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M %Z")
    except:
        current_time_str = str(datetime.datetime.now())
        
    location_str = "Unknown"
    if hasattr(state, "location") and state.location:
        location_str = f"{state.location.get('city', 'Unknown')}, {state.location.get('region', '')}"

    env_context = f"Current Time: {current_time_str}\nCurrent Location: {location_str}"

    prompt = (
        "Menu (Available Tools):\n"
        f"{tool_menu_summary}\n\n"   # [OPTIMIZATION] Static Content FIRST (Prefix Cache)
        f"{vector_context_str}\n\n"  # Dynamic Content Second
        f"{env_context}\n\n"         # Dynamic Content Third
        "Task: Analyze the query and select tools from the Menu. Return valid JSON only.\n"
        "Example Output:\n"
        "{\"target_servers\": [], \"complexity\": \"low\", \"auto_execute\": [{\"tool\": \"get_current_time\", \"args\": {}}]}\n"
        "{\"target_servers\": [\"tavily-search\"], \"complexity\": \"high\", \"auto_execute\": null}\n\n"
        f"User Query: '{query}'\n"
        "YOUR RESPONSE (JSON ONLY):"
    )

    try:
        # Circuit Breaker Check
        model = state.intent_model
        if not state.mcp_circuit_breaker.is_allowed(model):
            logger.warning(f"Maître d' Short-Circuited: Model '{model}' is broken.")
            return {"target_servers": []}

        # Helper for explicit fast call
        headers = {}
        if getattr(state, "router_auth_token", None):
            headers["Authorization"] = f"Bearer {state.router_auth_token}"

        async with httpx.AsyncClient(headers=headers) as client:
            payload = {
                "model": model, 
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "response_format": {"type": "json_object"},
                "options": {"num_ctx": 32768}  # [FIX] Unified 32k Context (User Requirement)
            }
            
            # [Optimization] Direct Lane for Local Models
            import os
            if model.startswith("ollama:"):
                base = os.getenv("OLLAMA_BASE", "http://127.0.0.1:11434").rstrip("/")
                url = f"{base}/v1/chat/completions"
                # Strip prefix for raw Ollama execution
                payload["model"] = model.replace("ollama:", "", 1)
            else:
                url = f"{state.gateway_base}/v1/chat/completions"
            logger.info(f"Maître d' URL: {url} (Model: {model})")
            
            # [ADJUSTMENT] 70B Model requires longer timeout for Prompt Eval of large menus
            r = await client.post(url, json=payload, timeout=120.0)
            
            if r.status_code == 200:
                try:
                    data = r.json()
                    content = data["choices"][0]["message"]["content"]
                    logger.info(f"Maître d' Decision: {content}")
                    
                    # Record Success
                    state.mcp_circuit_breaker.record_success(model)
                    
                    # Robust JSON Extraction (Handle "Here is the JSON: {...}")
                    try:
                        # 1. Try pure JSON
                        result = json.loads(content)
                        # [FIX] Normalize target_servers (Llama 3.1 returns dicts)
                        if "target_servers" in result:
                            result["target_servers"] = [
                                s.get("name", s) if isinstance(s, dict) else s 
                                for s in result.get("target_servers", [])
                            ]
                        
                        # [SANITIZER] Filter Malformed Tool Names (e.g. "Server 'time'...")
                        if "auto_execute" in result and isinstance(result["auto_execute"], list):
                            cleaned_tools = []
                            for t in result["auto_execute"]:
                                t_name = t.get("tool", "")
                                # Heuristic: Tool names should be snake_case or kebab-case, no spaces, no quotes
                                if " " in t_name or "'" in t_name or '"' in t_name or ":" in t_name:
                                    logger.warning(f"Maître d' Sanitizer: Dropped malformed tool name: '{t_name}'")
                                else:
                                    cleaned_tools.append(t)
                            result["auto_execute"] = cleaned_tools
                        
                        # [OPTIMIZATION] Cache Result
                        _intent_cache[cache_key] = (time.time(), result)
                        return result
                    except json.JSONDecodeError:
                        # 2. Try Regex Extraction
                        match = re.search(r"(\{.*\"target_servers\".*\})", content, re.DOTALL)
                        if match:
                            result = json.loads(match.group(1))
                            # [FIX] Normalize target_servers
                            if "target_servers" in result:
                                result["target_servers"] = [
                                    s.get("name", s) if isinstance(s, dict) else s 
                                    for s in result.get("target_servers", [])
                                ]
                            
                        # [SANITIZER] Filter Malformed Tool Names (e.g. "Server 'time'...")
                        if "auto_execute" in result and isinstance(result["auto_execute"], list):
                            cleaned_tools = []
                            for t in result["auto_execute"]:
                                t_name = t.get("tool", "")
                                # Heuristic: Tool names should be snake_case or kebab-case, no spaces, no quotes
                                if " " in t_name or "'" in t_name or '"' in t_name or ":" in t_name:
                                    logger.warning(f"Maître d' Sanitizer: Dropped malformed tool name: '{t_name}'")
                                else:
                                    cleaned_tools.append(t)
                            result["auto_execute"] = cleaned_tools

                        # [OPTIMIZATION] Cache Result
                        _intent_cache[cache_key] = (time.time(), result)
                        return result
                        raise # Re-raise to trigger error handler below

                except (json.JSONDecodeError, AttributeError):
                    logger.error(f"Maître d' JSON Error. Body: {r.text[:500]}")
                    state.mcp_circuit_breaker.record_failure(model) # JSON error might mean model is outputting garbage
                    return {"target_servers": []}
                    
            elif r.status_code == 429:
                logger.warning("Maître d' Overloaded (429). Bypassing intent classification.")
                # We don't trip breaker for 429 usually, but could.
                return {"target_servers": []} 
            else:
                 logger.warning(f"Maître d' HTTP {r.status_code}: {r.text}")
                 state.mcp_circuit_breaker.record_failure(model)
                 
    except Exception as e:
        logger.warning(f"Intent classification failed: {e}")
        state.mcp_circuit_breaker.record_failure(state.intent_model)
    
    # Safe Fallback
    return {"target_servers": []}

async def generate_search_query(messages: List[Dict[str, Any]], state: Any, call_gateway_fn: Any) -> str:
    """Use LLM to rewrite the latest user message into a standalone search query."""
    if messages:
        logger.info(f"DEBUG: Internal Query Gen. History={len(messages)}. Last Role={messages[-1].get('role')}")
    
    # Find the last user message
    last_user_msg = None
    for m in reversed(messages):
        if m.get("role") == "user":
            last_user_msg = m
            break
    
    if not last_user_msg:
        return ""

    last_user_content = extract_text_content(last_user_msg.get("content"))

    # [OPTIMIZATION] DISABLED Refinement (User Request: Formula 1 Speed)
    # Refinement was adding 14s latency. We skip it entirely.
    if True: # Force Skip
         logger.info(f"Query Refinement: DISABLED (Formula 1 Mode). Using raw input.")
         return last_user_content

    # Proceed to LLM Refinement below...
    
    sys_prompt = (
        "You are a Database Search Query Generator. "
        "Convert the LAST user message into a specific keyword search query for a vector database. "
        "Resolve pronouns based on context. "
        "Do NOT answer the question. Do NOT be polite. "
        "Output ONLY the query string."
    )
    
    # Reduced context for rewriting
    # Extract text from last 3 messages to avoid passing huge JSON blobs
    context_text = []
    # Optimization: Only use last 1 message context for 1B model speed
    for m in messages[-2:]:
        role = m.get("role")
        text = extract_text_content(m.get("content"))
        context_text.append(f"{role}: {text}")
    
    user_prompt = f"Context:\n{chr(10).join(context_text)}\n\nGenerate Search Query for the last user message:"
    
    prompt_msgs = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    try:
        # We call the gateway without tools
        t0 = time.time()
        # Use configurable query_refinement_model 
        response = await call_gateway_fn(
            messages=prompt_msgs,
            model=state.query_refinement_model, 
            tools=[], # [FIX] Empty list prevents injecting 50+ tools into 1B model!
            options={"num_ctx": 32768} # [USER] Expanded Context to 32k
        )
        
        rewritten = response["choices"][0]["message"]["content"].strip()
        if rewritten.startswith('"') and rewritten.endswith('"'):
            rewritten = rewritten[1:-1]
        
        latency = (time.time() - t0) * 1000
        logger.info(f"Query Refinement: '{last_user_content[:50]}...' -> '{rewritten}' ({latency:.2f}ms)")
        return rewritten

    except Exception as e:
        logger.warning(f"Query refinement failed: {e}. Falling back to raw content.")
        return last_user_content
