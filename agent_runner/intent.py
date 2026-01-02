import json
import logging
import time
from typing import Any, Dict, List
import httpx
import re

logger = logging.getLogger("agent_runner.intent")

def extract_text_content(content: Any) -> str:
    """Extract plain text from potential list-based content (common in advanced clients)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        # Extract text from blocks like [{'type': 'text', 'text': 'hi'}]
        return " ".join([str(block.get("text", "")) for block in content if isinstance(block, dict) and block.get("type") == "text"])
    return str(content)

async def classify_search_intent(query: str, state: Any, tool_menu_summary: str) -> Dict[str, Any]:
    """Classify query and select relevant toolsets using the 'Maître d' Menu'."""
    from agent_runner.feedback import get_suggested_servers
    
    if not tool_menu_summary:
        # Fallback if discovery hasn't run
        return {"target_servers": [], "notes": "No menu available"}

    # [FEATURE-9] Learning Loop: Inject suggestions from history
    suggestions_str = ""
    try:
        suggestions = await get_suggested_servers(query)
        if suggestions:
            # We limit to top 3 to avoid bias
            suggestions_str = f"Recall: User usage history suggests these servers are relevant: {', '.join(suggestions[:3])}\n"
    except Exception:
        pass

    prompt = (
        "SYSTEM DIRECTIVE: YOU ARE A JSON GENERATOR. OUTPUT ONLY JSON. NO EXPLANATION.\n"
        f"User Query: '{query}'\n\n"
        "Menu:\n"
        f"{tool_menu_summary}\n\n"
        f"{suggestions_str}"
        "Task: Return the list of servers required.\n"
        "Constraint 1: Core tools (Time) are pre-loaded. Do NOT select them.\n"
        "Constraint 2: IF the user refers to past conversations, specific facts, personal details, or implies context (e.g. 'it', 'that'), YOU MUST SELECT 'project-memory'.\n"
        "Constraint 3: If 'fetch', 'browse', 'weather' are needed, select them.\n\n"
        "Example Output:\n"
        "{\"target_servers\": [\"tavily-search\"]}\n"
        "{\"target_servers\": []}\n\n"
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
                "response_format": {"type": "json_object"}
            }
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
                        return json.loads(content)
                    except json.JSONDecodeError:
                        # 2. Try Regex Extraction
                        match = re.search(r"(\{.*\"target_servers\".*\})", content, re.DOTALL)
                        if match:
                            return json.loads(match.group(1))
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

    # Use the Agent Model (fast) to rewrite
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
    for m in messages[-3:]:
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
        # Using agent_model (likely gpt-4o-mini) for speed
        response = await call_gateway_fn(
            messages=prompt_msgs,
            model=state.agent_model, 
            tools=None
        )
        rewritten = response["choices"][0]["message"]["content"].strip()
        # Clean quotes
        if rewritten.startswith('"') and rewritten.endswith('"'):
            rewritten = rewritten[1:-1]
        dur = (time.time() - t0) * 1000
        logger.info(f"Query Refinement: '{last_user_content[:50]}...' -> '{rewritten}' ({dur:.2f}ms)")
        return rewritten
    except Exception as e:
        logger.warning(f"Query refinement failed: {e}. Falling back to raw content.")
        return last_user_content
