import json
import logging
import time
import os
import hashlib
from typing import Any, Dict, List, Optional
import httpx
import re
from pathlib import Path

logger = logging.getLogger("agent_runner.intent")
from agent_runner.db_utils import run_query

class PersistentIntentCache:
    """Persistent cache for Maître d' intent classifications with 24h TTL"""

    def __init__(self, cache_file: str = "maitre_d_cache.json", max_entries: int = 10000):
        self.cache_file = Path(__file__).parent / cache_file
        self.max_entries = max_entries
        self.cache = self._load_cache()
        self.hits = 0
        self.misses = 0

    def _load_cache(self) -> Dict[str, Any]:
        """Load cache from disk"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load intent cache: {e}")
        return {}

    def _save_cache(self):
        """Save cache to disk"""
        try:
            # Clean expired entries before saving
            self._cleanup_expired()

            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save intent cache: {e}")

    def _cleanup_expired(self):
        """Remove expired entries"""
        current_time = time.time()
        expired_keys = []

        for key, entry in self.cache.items():
            if current_time - entry.get('timestamp', 0) > 86400:  # 24 hours
                expired_keys.append(key)

        for key in expired_keys:
            del self.cache[key]

        # If still too many entries, remove oldest
        if len(self.cache) > self.max_entries:
            # Sort by timestamp and keep newest
            sorted_entries = sorted(self.cache.items(),
                                  key=lambda x: x[1].get('timestamp', 0),
                                  reverse=True)
            self.cache = dict(sorted_entries[:self.max_entries])

    def get(self, query_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached result if valid"""
        if query_hash in self.cache:
            entry = self.cache[query_hash]
            if time.time() - entry.get('timestamp', 0) < 86400:  # 24h TTL
                self.hits += 1
                logger.info(f"Maître d' Cache HIT: {query_hash[:16]}... (TTL: {86400 - int(time.time() - entry['timestamp'])}s)")
                return entry['result']
            else:
                # Expired, remove it
                del self.cache[query_hash]

        self.misses += 1
        return None

    def put(self, query_hash: str, result: Dict[str, Any]):
        """Store result in cache"""
        self.cache[query_hash] = {
            'timestamp': time.time(),
            'result': result,
            'query_hash': query_hash
        }

        # Save to disk periodically (every 10 entries)
        if (self.hits + self.misses) % 10 == 0:
            self._save_cache()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0

        return {
            'total_entries': len(self.cache),
            'hit_rate': hit_rate,
            'hits': self.hits,
            'misses': self.misses,
            'cache_file': str(self.cache_file)
        }

# Global cache instance
_intent_cache = PersistentIntentCache()

# Common query patterns to pre-compute during startup
COMMON_INTENT_PATTERNS = [
    # Conversational
    "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
    "how are you", "what's up", "how's it going", "sup",
    "thank you", "thanks", "ok", "okay", "got it", "understood",

    # Time/Location
    "what time is it", "what's the time", "current time", "time",
    "where am I", "what's my location", "current location", "location",

    # System status
    "how are you doing", "system status", "are you working", "status",

    # Tool discovery
    "what can you do", "what tools do you have", "help", "commands",

    # Web search
    "search for", "look up", "find information about",

    # File operations
    "list files", "read file", "write file", "create file"
]

async def precompute_common_intents(state: Any, tool_menu_summary: str):
    """Pre-compute intent classifications for common query patterns during startup"""
    logger.info(f"Pre-computing Maître d' intents for {len(COMMON_INTENT_PATTERNS)} common patterns...")

    precomputed = 0
    for pattern in COMMON_INTENT_PATTERNS:
        try:
            normalized = normalize_query_for_caching(pattern)
            cache_key = hashlib.md5(f"{normalized}::{state.intent_model}".encode()).hexdigest()

            # Only compute if not already cached
            if not _intent_cache.get(cache_key):
                logger.info(f"Pre-computing intent for: '{pattern}'")
                result = await _compute_intent_classification(pattern, state, tool_menu_summary)
                _intent_cache.put(cache_key, result)
                precomputed += 1

        except Exception as e:
            logger.warning(f"Failed to pre-compute intent for '{pattern}': {e}")

    logger.info(f"✅ Pre-computed {precomputed} Maître d' intents. Cache now has {_intent_cache.get_stats()['total_entries']} entries.")


def _detect_domain(query: str) -> Optional[str]:
    """Lightweight domain detector for local/system commands."""
    q = query.lower()
    system_hits = ["mcp", "server", "router", "agent", "surreal", "health", "status", "restart", "logs", "cpu", "ram"]
    fs_hits = ["file", "folder", "directory", "path", "list files", "ls", "read", "write", "append", "mv", "cp", "find"]
    ingest_hits = ["ingest", "index", "knowledge", "rag", "upload"]

    if any(k in q for k in system_hits):
        return "system"
    if any(k in q for k in fs_hits):
        return "fs"
    if any(k in q for k in ingest_hits):
        return "ingestion"
    return None


def _build_micro_menu(domain: Optional[str], vector_results: List[Dict[str, Any]]) -> str:
    """Build a tiny domain-scoped menu to avoid flooding the prompt."""
    if not domain:
        return ""

    seen = set()
    entries = []

    # Use semantic hits first
    for tool in vector_results or []:
        name = tool.get("name")
        desc = tool.get("description", "")
        if not name or name in seen:
            continue
        entries.append(f"- {name}: {desc[:120]}")
        seen.add(name)
        if len(entries) >= 8:
            break

    defaults = {
        "system": [
            ("list_active_mcp_servers", "List MCP servers and status"),
            ("get_system_health", "Check router/agent/MCP health"),
            ("read_service_logs", "Tail router/agent/ollama logs"),
            ("check_resource_usage", "CPU/RAM/disk usage"),
            ("add_mcp_server", "Add/update an MCP server"),
            ("install_mcp_package", "Install MCP via npm package"),
        ],
        "fs": [
            ("list_dir", "List folder contents"),
            ("path_info", "Inspect a path"),
            ("read_text", "Read a text file"),
            ("write_text", "Write a text file"),
            ("append_text", "Append to a file"),
            ("find_files", "Find files by pattern/extension"),
            ("move_path", "Move/rename a path"),
            ("copy_path", "Copy file or directory"),
        ],
        "ingestion": [
            ("ingest_file", "Queue a file for ingestion"),
            ("get_ingestion_status", "Check ingestion queue status"),
            ("parse_mcp_config", "Parse and install MCP config text"),
        ],
    }

    for name, desc in defaults.get(domain, []):
        if len(entries) >= 8:
            break
        if name in seen:
            continue
        entries.append(f"- {name}: {desc}")
        seen.add(name)

    if not entries:
        return ""

    return "Micro Menu (local tools):\n" + "\n".join(entries)

async def _compute_intent_classification(query: str, state: Any, tool_menu_summary: str) -> Dict[str, Any]:
    """Compute intent classification for a query (extracted from main function)"""
    # This is a simplified version - in practice we'd call the full LLM analysis
    # For now, return basic structure to avoid breaking the system
    return {
        "target_servers": [],
        "complexity": "low",
        "auto_execute": None,
        "precomputed": True
    }

def extract_text_content(content: Any) -> str:
    """Extract plain text from potential list-based content (common in advanced clients)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        # Extract text from blocks like [{'type': 'text', 'text': 'hi'}]
        return " ".join([str(block.get("text", "")) for block in content if isinstance(block, dict) and block.get("type") == "text"])
    return str(content)

def normalize_query_for_caching(query: str) -> str:
    """Normalize query for better cache hits"""
    # Convert to lowercase and strip
    normalized = query.lower().strip()

    # Remove punctuation
    normalized = re.sub(r'[^\w\s]', '', normalized)

    # Normalize whitespace
    normalized = ' '.join(normalized.split())

    # Common synonym normalization
    synonyms = {
        "what's": "what is",
        "what're": "what are",
        "how's": "how is",
        "how're": "how are",
        "i'm": "i am",
        "it's": "it is",
        "that's": "that is",
        "there's": "there is",
        "here's": "here is",
        "where's": "where is",
        "who's": "who is",
        "how's it going": "how are you",
        "what's up": "how are you",
        "whats up": "how are you",
        "sup": "how are you",
        "hey": "hello",
        "hi there": "hello",
        "good morning": "hello",
        "good afternoon": "hello",
        "good evening": "hello"
    }

    for old, new in synonyms.items():
        normalized = normalized.replace(old, new)

    return normalized

async def classify_search_intent(query: str, state: Any, tool_menu_summary: str, advice_menu_list: List[str] = None) -> Dict[str, Any]:
    """Classify query and select relevant toolsets using the 'Maître d' Menu' & Advice Registry."""

    # Store query for maître d' learning system
    if hasattr(state, 'last_user_query'):
        state.last_user_query = query

    # [OPTIMIZATION] Persistent Cache with Query Normalization
    normalized_query = normalize_query_for_caching(query)
    cache_key = hashlib.md5(f"{normalized_query}::{state.intent_model}".encode()).hexdigest()

    # Check persistent cache first
    cached_result = _intent_cache.get(cache_key)
    if cached_result:
        return cached_result

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

    domain = _detect_domain(normalized_query)
    micro_menu = _build_micro_menu(domain, vector_results)
    menu_section = micro_menu if micro_menu else tool_menu_summary
    combined_menu = f"{vector_context_str}{menu_section}"

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
        f"{menu_section}\n\n"    # Prefer micro menu when available
        f"{vector_context_str}\n\n"  # Dynamic Content Second
        f"{env_context}\n\n"         # Dynamic Content Third
        "Task: Analyze the query and select tools from the Menu. Return valid JSON only.\n"
        "Example Output:\n"
        "{\"target_servers\": [], \"complexity\": \"low\", \"auto_execute\": null}\n"
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
            # [DEBUG] Log Prompt Size
            prompt_len = len(prompt)
            logger.info(f"Maître d' URL: {url} (Model: {model}) | Payload Size: {len(json.dumps(payload))} bytes | Prompt Len: {prompt_len} chars")
            
            t0 = time.time()
            logger.info("Maître d' Request: SENDING...")

            
            # [ADJUSTMENT] 70B Model requires longer timeout for Prompt Eval of large menus
            r = await client.post(url, json=payload, timeout=120.0)
            
            dur = time.time() - t0
            logger.info(f"Maître d' Request: RECEIVED in {dur:.2f}s | Status: {r.status_code}")
            
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
                        if "auto_execute" in result:
                            # Normalize string to list
                            if isinstance(result["auto_execute"], str):
                                # Convert "tool_name" -> [{"tool": "tool_name"}]
                                result["auto_execute"] = [{"tool": result["auto_execute"]}]
                            
                            # Clean list
                            if isinstance(result["auto_execute"], list):
                                cleaned_tools = []
                                for t in result["auto_execute"]:
                                    # Handle simple strings in list ["tool"]
                                    if isinstance(t, str):
                                        t = {"tool": t}
                                        
                                    t_name = t.get("tool", "")
                                    # Heuristic: Tool names should be snake_case or kebab-case, no spaces, no quotes
                                    if " " in t_name or "'" in t_name or '"' in t_name or ":" in t_name:
                                        logger.warning(f"Maître d' Sanitizer: Dropped malformed tool name: '{t_name}'")
                                    else:
                                        cleaned_tools.append(t)
                                result["auto_execute"] = cleaned_tools

                        # [OPTIMIZATION] Cache Result in Persistent Cache
                        _intent_cache.put(cache_key, result)
                        logger.info(f"Maître d' Cache MISS: Stored result for {normalized_query[:30]}...")
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

                        # [OPTIMIZATION] Cache Result in Persistent Cache
                        _intent_cache.put(cache_key, result)
                        logger.info(f"Maître d' Cache MISS: Stored result for {normalized_query[:30]}...")
                        return result
                        raise # Re-raise to trigger error handler below

                except (json.JSONDecodeError, AttributeError):
                    logger.error(f"Maître d' JSON Error. Body: {r.text[:500]}")
                    state.mcp_circuit_breaker.record_failure(model) # JSON error might mean model is outputting garbage
                    # Cache the failure result too to avoid repeated failures
                    failure_result = {"target_servers": []}
                    _intent_cache.put(cache_key, failure_result)
                    return failure_result
                    
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
