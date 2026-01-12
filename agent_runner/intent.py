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

    # [FEATURE-9] Learning Loop: Inject suggestions from history
    suggestions_str = ""
    try:
        suggestions = await get_suggested_servers(query, state=state)
        if suggestions:
            # We limit to top 3 to avoid bias
            suggestions_str = f"Recall: User usage history suggests these servers are relevant: {', '.join(suggestions[:3])}\n"
    except Exception as e:
        logger.debug(f"Maître d' suggestion retrieval failed: {e}")
        
    # [FEATURE-ADVICE] Advice Menu
    advice_str = ""
    if advice_menu_list:
        advice_str = (
            "Available Advice Topics:\n"
            f"- {', '.join(advice_menu_list)}\n\n"
        )

    prompt = (
        "SYSTEM DIRECTIVE: YOU ARE A JSON GENERATOR. OUTPUT ONLY JSON. NO EXPLANATION.\n"
        f"User Query: '{query}'\n\n"
        "Menu:\n"
        f"{tool_menu_summary}\n\n"
        f"{advice_str}"
        f"{suggestions_str}"
        "Task: Return the list of servers and advice topics required.\n"
        "Constraint 1: Core tools (Time) are pre-loaded. Do NOT select them.\n"
        "Constraint 3: If 'fetch', 'browse', 'weather' are needed, select them.\n"
        "Constraint 9: [WEB SEARCH] If user asks for current news, headlines, recent events, latest information, today's news, or Google/Bing news, select 'tavily-search'.\n"
        "Constraint 10: [WEB SEARCH] If user asks for real-time information, current events, breaking news, or time-sensitive data, select 'tavily-search'.\n"
        "Constraint 4: [SYSTEM TOOLS] If user needs to read/write/list files, select 'filesystem'.\n"
        "Constraint 5: [SYSTEM TOOLS] If user needs to run commands, check system health, or manage config, select 'system' and 'admin'.\n"
        "Constraint 5.5: [SYSTEM INTROSPECTION] If user asks about internal system configuration, model assignments, how the system works, or technical architecture ('What models are running?', 'How does it work?', 'Show me the configuration'), select 'system' and 'admin'.\n"
        "Constraint 11: [MEMORY] If user asks about previous conversations, stored information, preferences, what was discussed before, or wants to recall/remember something ('What have we talked about?', 'Do you remember?', 'What are my preferences?'), select 'memory'.\n"
        "Constraint 6: [ADVICE] If the query relates to an Available Advice Topic, include it in 'advice_topics'.\n"
        "Constraint 7: [LOCAL ACTION] If user asks for 'help' (commands), 'system prompt' (instructions), 'restart', or 'emojis', set 'system_action' to 'help', 'prompt', 'restart', or 'emoji'.\n"
        "Constraint 8: [LAYER CONTROL] If user asks to enable/disable layers (e.g. 'disable emoji layer'), set 'system_action' to 'enable_emoji', 'disable_emoji', 'enable_chat', etc.\n\n"
        "Example Output:\n"
        "{\"target_servers\": [\"tavily-search\"], \"advice_topics\": [], \"system_action\": null}  // For: 'What are today's news headlines?'\n"
        "{\"target_servers\": [\"tavily-search\"], \"advice_topics\": [], \"system_action\": null}  // For: 'Latest breaking news'\n"
        "{\"target_servers\": [\"tavily-search\"], \"advice_topics\": [], \"system_action\": null}  // For: 'What happened recently in politics?'\n"
        "{\"target_servers\": [\"memory\"], \"advice_topics\": [], \"system_action\": null}  // For: 'What have we talked about before?'\n"
        "{\"target_servers\": [\"memory\"], \"advice_topics\": [], \"system_action\": null}  // For: 'Do you remember my preferences?'\n"
        "{\"target_servers\": [], \"advice_topics\": [], \"system_action\": \"prompt\"}\n"
        "{\"target_servers\": [], \"advice_topics\": [], \"system_action\": \"disable_emoji\"}\n\n"
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
                "options": {"num_ctx": 32768}  # [FIX] Match Resident Model Context
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
            
            r = await client.post(url, json=payload, timeout=25.0)
            
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
            options={"num_ctx": 2048} # Match preloaded context to prevent reloading!
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
