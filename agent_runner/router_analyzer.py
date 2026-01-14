"""
Router Model Analyzer - Intelligent query analysis for routing decisions.

Uses a small, fast model (3B) to analyze queries and make intelligent routing decisions:
- Tool selection (filter tools by relevance)
- Model selection (route to best model for task)

- Context estimation (accurate token counting)
- Query classification (intent, complexity, domain)
"""

import asyncio
import json
import logging
import math
import os
import re
import threading
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import hashlib
import time

logger = logging.getLogger(__name__)

# Import unified tracking for categorization analytics
try:
    from common.unified_tracking import track_event, EventCategory, EventSeverity
except ImportError:
    # Fallback if unified_tracking not available
    def track_event(*args, **kwargs):
        pass
    class MockEventCategory:
        SYSTEM = 'system'
    class MockEventSeverity:
        INFO = 'info'
        DEBUG = 'debug'
        MEDIUM = 'medium'
        HIGH = 'high'
        CRITICAL = 'critical'
    EventCategory = MockEventCategory()
    EventSeverity = MockEventSeverity()

# Router model configuration
ROUTER_MODEL = os.getenv("ROUTER_MODEL", "ollama:qwen2.5:7b-instruct")  # Upgraded 7B model for better routing quality
ROUTER_ENABLED = os.getenv("ROUTER_ENABLED", "true").lower() == "true"
ROUTER_CACHE_TTL = float(os.getenv("ROUTER_CACHE_TTL", "300.0"))  # 5 minutes cache
ROUTER_TIMEOUT = float(os.getenv("ROUTER_TIMEOUT", "15.0"))  # 15 second timeout for analysis
ROUTER_MAX_RETRIES = int(os.getenv("ROUTER_MAX_RETRIES", "2"))  # Max retries for transient failures

# Circuit breaker for router model
_router_circuit_breaker: Dict[str, Any] = {
    "failures": 0,
    "last_failure": 0.0,
    "half_open": False,
    "lock": threading.Lock(),
}
ROUTER_CIRCUIT_BREAKER_THRESHOLD = 5  # Disable after 5 failures
ROUTER_CIRCUIT_BREAKER_RESET_TIME = 60.0  # Reset after 60 seconds

# Thread-safe LRU cache for router analyses
# NOTE: Cache invalidation framework available in agent_runner/cache_helpers.py
# For now, using in-memory cache with TTL. Future: Integrate with DB timestamp validation.
_router_cache: OrderedDict[str, tuple[float, 'RouterAnalysis']] = OrderedDict()
_cache_lock = threading.Lock()
_cache_max_size = 100

# Cached tool category map (built once)
_tool_category_map: Optional[Dict[str, str]] = None
_category_map_lock = threading.Lock()

# Valid tool categories
VALID_CATEGORIES = {
    "web_search", "filesystem", "code", "browser", "memory",
    "scraping", "automation", "http", "weather", "document", "ollama"
}

# Category synonyms/aliases for normalization
CATEGORY_SYNONYMS = {
    "web_search": ["search", "web", "internet", "research"],
    "filesystem": ["file", "files", "directory", "dir", "fs"],
    "code": ["programming", "script", "command", "execute"],
    "browser": ["web", "page", "navigate", "automation"],
    "memory": ["fact", "knowledge", "store", "recall"],
    "scraping": ["scrape", "extract", "crawl", "parse"],
    "automation": ["automate", "script", "workflow"],
    "http": ["api", "request", "fetch", "call"],
    "weather": ["forecast", "temperature", "climate"],
    "document": ["convert", "transform", "export"],
    "ollama": ["model", "llm", "ai"],
}

# Valid tool categories
VALID_CATEGORIES = {
    "web_search", "filesystem", "code", "browser", "memory",
    "scraping", "automation", "http", "weather", "document", "ollama"
}

# Category synonyms/aliases for normalization
CATEGORY_SYNONYMS = {
    "web_search": ["search", "web", "internet", "research"],
    "filesystem": ["file", "files", "directory", "dir", "fs"],
    "code": ["programming", "script", "command", "execute"],
    "browser": ["web", "page", "navigate", "automation"],
    "memory": ["fact", "knowledge", "store", "recall"],
    "scraping": ["scrape", "extract", "crawl", "parse"],
    "automation": ["automate", "script", "workflow"],
    "http": ["api", "request", "fetch", "call"],
    "weather": ["forecast", "temperature", "climate"],
    "document": ["convert", "transform", "export"],
    "ollama": ["model", "llm", "ai"],
}

# Semantic paraphrasing examples for categories
TOOL_CATEGORY_EXAMPLES = {
    "web_search": ["find", "search", "who is", "latest news", "current price of", "lookup", "research", "internet search"],
    "filesystem": ["read", "write", "list", "save", "delete", "file", "folder", "path", "directory"],
    "code": ["run", "execute", "python", "script", "thinking", "sequential", "logic", "debug"],
    "browser": ["navigate", "click", "scrape", "screenshot", "form", "web page", "browser"],
    "memory": ["remember", "recall", "store", "fact", "base", "semantic"],
    "scraping": ["extract", "parse", "crawl", "structured data"],
    "automation": ["workflow", "macos", "shortcut", "automate"],
    "http": ["api", "request", "endpoint", "webhook"],
    "weather": ["forecast", "temperature", "rain", "sun"],
    "document": ["pdf", "markdown", "convert", "transform"],
    "ollama": ["models", "pull", "list models", "embeddings"]
}

# Negative constraint examples to prevent misclassification
NEGATIVE_CONSTRAINT_EXAMPLES = [
    {"query": "read file.txt", "wrong_category": "web_search", "correct_category": "filesystem", "reason": "Query is about local files, not internet search"},
    {"query": "search for python tutorials", "wrong_category": "code", "correct_category": "web_search", "reason": "Query is a search for information, not code execution"},
    {"query": "save this to my memory", "wrong_category": "filesystem", "correct_category": "memory", "reason": "Query is about long-term episodic memory, not local files"},
    {"query": "run a python script", "wrong_category": "automation", "correct_category": "code", "reason": "Explicit code execution should use the code category"},
    {"query": "what is the weather", "wrong_category": "web_search", "correct_category": "weather", "reason": "Specific weather category exists"},
]


@dataclass
class RouterAnalysis:
    """Structured analysis from router model."""
    # Query classification
    complexity: str  # simple, medium, complex, very_complex
    query_type: str  # coding, research, automation, analysis, creative, other
    domain: str  # technical, business, creative, etc.
    
    # Tool selection
    tool_categories: List[str]  # web_search, filesystem, code, browser, etc.
    recommended_tools: List[str]  # Specific tool names if available
    
    # Model selection
    recommended_model: Optional[str]  # Best model for this query
    can_use_local: bool  # Whether local model is sufficient
    estimated_cost: float  # Estimated cost if using cloud model
    

    
    # Context estimation
    estimated_input_tokens: int
    estimated_output_tokens: int
    optimal_context_window: Optional[int]  # Recommended context size
    
    # Query validation
    is_ambiguous: bool
    requires_clarification: bool
    clarification_questions: List[str]
    
    # Additional metadata
    confidence: float  # 0.0 to 1.0
    reasoning: Optional[str]  # Router's reasoning (for debugging)


def _check_circuit_breaker() -> bool:
    """Check if router circuit breaker is open."""
    with _router_circuit_breaker["lock"]:
        now = time.time()
        failures = _router_circuit_breaker["failures"]
        last_failure = _router_circuit_breaker["last_failure"]
        
        # Reset if enough time has passed
        if failures >= ROUTER_CIRCUIT_BREAKER_THRESHOLD:
            if now - last_failure > ROUTER_CIRCUIT_BREAKER_RESET_TIME:
                # Try half-open state
                _router_circuit_breaker["failures"] = 0
                _router_circuit_breaker["half_open"] = True
                logger.info("Router circuit breaker: entering half-open state")
                return True
            return False  # Still open
        
        return True  # Closed (normal operation)


def _record_router_success() -> None:
    """Record successful router call."""
    with _router_circuit_breaker["lock"]:
        _router_circuit_breaker["failures"] = 0
        _router_circuit_breaker["half_open"] = False


def _record_router_failure() -> None:
    """Record failed router call."""
    with _router_circuit_breaker["lock"]:
        _router_circuit_breaker["failures"] += 1
        _router_circuit_breaker["last_failure"] = time.time()
        if _router_circuit_breaker["failures"] >= ROUTER_CIRCUIT_BREAKER_THRESHOLD:
            logger.warning(f"Router circuit breaker: OPEN (after {_router_circuit_breaker['failures']} failures)")


async def _call_router_model(
    prompt: str,
    gateway_base: str,
    http_client: Any,
    timeout: float = ROUTER_TIMEOUT,
    retries: int = ROUTER_MAX_RETRIES
) -> tuple[str, Optional[float]]:
    """
    Call the router model via gateway with retry logic and logprobs support.
    
    Returns:
        tuple: (response_content, confidence_from_logprobs)
        - response_content: The text response from the model
        - confidence_from_logprobs: Confidence score from logprobs (0.0-1.0), or None if unavailable
    """
    # Check circuit breaker
    if not _check_circuit_breaker():
        raise Exception("Router circuit breaker is OPEN")
    
    
    # [PATCH] Use auth token from env
    auth_token = os.getenv("ROUTER_AUTH_TOKEN")
    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    url = f"{gateway_base}/v1/chat/completions"
    payload = {
        "model": ROUTER_MODEL,
        "messages": [
            {"role": "system", "content": "You are a query analysis router. Analyze queries and return structured JSON responses."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.0,  # Deterministic for routing
        "max_tokens": 1000,  # Router responses should be concise
        "logprobs": True,  # Request logprobs for true confidence scores
        "top_logprobs": 1,  # Get top 1 probability for first token
    }
    
    last_error = None
    for attempt in range(retries + 1):
        try:
            start_time = time.time()
            resp = await asyncio.wait_for(
                http_client.post(url, json=payload, headers=headers),
                timeout=timeout
            )
            resp.raise_for_status()
            data = resp.json()
            choice = data.get("choices", [{}])[0]
            content = choice.get("message", {}).get("content", "")
            
            # Extract logprobs for confidence scoring (Judge Model approach)
            confidence_from_logprobs = None
            try:
                logprobs = choice.get("logprobs")
                if logprobs:
                    # Try different logprob formats (varies by API)
                    content_tokens = logprobs.get("content", [])
                    if not content_tokens:
                        # Some APIs return tokens directly
                        content_tokens = logprobs.get("tokens", [])
                    
                    if content_tokens and len(content_tokens) > 0:
                        # Get first token's logprob (most indicative of model's confidence)
                        first_token = content_tokens[0]
                        
                        # Handle different token formats
                        if isinstance(first_token, dict):
                            logprob = first_token.get("logprob")
                        elif isinstance(first_token, (list, tuple)) and len(first_token) > 1:
                            logprob = first_token[1]  # Some formats: [token, logprob]
                        else:
                            logprob = None
                        
                        if logprob is not None:
                            # Convert logprob to probability (logprob is log base e)
                            # Probability = exp(logprob)
                            # Note: logprobs are typically negative, so we normalize
                            try:
                                # For confidence, we want to use the probability of the first token
                                # Higher probability = model is more confident in its response
                                probability = math.exp(logprob)
                                
                                # Normalize: logprobs are typically in range [-inf, 0]
                                # We'll use a sigmoid-like normalization for better confidence scores
                                # For very negative logprobs, confidence should be low
                                # For less negative (closer to 0), confidence should be higher
                                # Simple approach: use probability directly, but clamp to [0, 1]
                                # More sophisticated: use softmax or sigmoid normalization
                                confidence_from_logprobs = max(0.0, min(1.0, probability))
                                
                                logger.debug(f"Extracted confidence from logprobs: {confidence_from_logprobs:.3f} (logprob: {logprob:.3f})")
                            except (ValueError, OverflowError) as e:
                                logger.debug(f"Could not convert logprob to probability: {e}")
            except Exception as e:
                # Logprobs extraction failed, but that's okay - we'll use JSON confidence
                logger.debug(f"Could not extract logprobs (may not be supported by this model/API): {e}")
            
            elapsed = time.time() - start_time
            logger.debug(f"Router model call succeeded in {elapsed:.2f}s")
            
            # Record success
            _record_router_success()
            return content, confidence_from_logprobs
        except asyncio.TimeoutError:
            last_error = f"Timeout after {timeout}s"
            if attempt < retries:
                logger.debug(f"Router call timeout (attempt {attempt + 1}/{retries + 1}), retrying...")
                from agent_runner.constants import SLEEP_BRIEF_BACKOFF_BASE
                await asyncio.sleep(SLEEP_BRIEF_BACKOFF_BASE * (attempt + 1))  # Brief backoff
        except Exception as e:
            last_error = str(e)
            # Don't retry on 4xx errors (client errors)
            if hasattr(e, 'response') and hasattr(e.response, 'status_code'):
                if 400 <= e.response.status_code < 500:
                    break
            if attempt < retries:
                logger.debug(f"Router call failed (attempt {attempt + 1}/{retries + 1}): {e}, retrying...")
                from agent_runner.constants import SLEEP_BRIEF_BACKOFF_BASE
                await asyncio.sleep(SLEEP_BRIEF_BACKOFF_BASE * (attempt + 1))  # Brief backoff
    
    # All retries failed
    _record_router_failure()
    logger.warning(f"Router model call failed after {retries + 1} attempts: {last_error}")
    raise Exception(f"Router model call failed: {last_error}")


async def _call_router_model_fallback(
    prompt: str,
    gateway_base: str,
    http_client: Any,
    timeout: float = ROUTER_TIMEOUT,
    retries: int = ROUTER_MAX_RETRIES
) -> str:
    """
    Fallback router model call without logprobs (for compatibility).
    Returns only the response content.
    """
    content, _ = await _call_router_model(prompt, gateway_base, http_client, timeout, retries)
    return content


def _extract_json_from_response(response: str) -> Optional[Dict[str, Any]]:
    """Extract JSON from router response, handling various formats."""
    if not response or not isinstance(response, str):
        return None
    
    response = response.strip()
    
    # Try to find JSON object in response
    # Handle markdown code blocks
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        # Try to find JSON object directly
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
        else:
            json_str = response
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        # Try to fix common issues
        json_str = json_str.replace("'", '"')  # Replace single quotes
        json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas
        json_str = re.sub(r',\s*]', ']', json_str)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None


def _validate_router_analysis(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize router analysis data."""
    # Validate complexity
    valid_complexities = ["simple", "medium", "complex", "very_complex"]
    complexity = data.get("complexity", "medium")
    if complexity not in valid_complexities:
        logger.warning(f"Invalid complexity '{complexity}', defaulting to 'medium'")
        complexity = "medium"
    
    # Validate query_type
    valid_query_types = ["coding", "research", "automation", "analysis", "creative", "other"]
    query_type = data.get("query_type", "other")
    if query_type not in valid_query_types:
        logger.warning(f"Invalid query_type '{query_type}', defaulting to 'other'")
        query_type = "other"
    
    # Validate confidence (0.0 to 1.0)
    confidence = data.get("confidence", 0.5)
    if not isinstance(confidence, (int, float)) or confidence < 0.0 or confidence > 1.0:
        logger.warning(f"Invalid confidence '{confidence}', defaulting to 0.5")
        confidence = 0.5
    
    # Ensure lists are lists
    tool_categories = data.get("tool_categories", [])
    if not isinstance(tool_categories, list):
        tool_categories = []
    
    recommended_tools = data.get("recommended_tools", [])
    if not isinstance(recommended_tools, list):
        recommended_tools = []
    
    # Ensure token counts are non-negative integers
    estimated_input_tokens = max(0, int(data.get("estimated_input_tokens", 0)))
    estimated_output_tokens = max(0, int(data.get("estimated_output_tokens", 0)))
    
    # Validate optimal_context_window
    optimal_context_window = data.get("optimal_context_window")
    if optimal_context_window is not None:
        try:
            optimal_context_window = int(optimal_context_window)
            if optimal_context_window < 0:
                optimal_context_window = None
        except (ValueError, TypeError):
            optimal_context_window = None
    
    # Provide defaults for simplified prompt (missing advanced fields)
    return {
        "complexity": complexity,
        "query_type": query_type,
        "domain": data.get("domain", "general"),
        "tool_categories": tool_categories,
        "recommended_tools": [],  # Simplified prompt doesn't ask for this
        "recommended_model": None,  # Simplified prompt doesn't ask for this
        "can_use_local": False,  # DISABLED: Always treat as requiring main agent (70B) to prevent 8B downgrade
        "estimated_cost": 0.0,  # Simplified prompt doesn't estimate costs

        "estimated_input_tokens": 0,  # Simplified prompt doesn't estimate tokens
        "estimated_output_tokens": 0,  # Simplified prompt doesn't estimate tokens
        "optimal_context_window": None,  # Simplified prompt doesn't optimize context
        "is_ambiguous": False,  # Simplified prompt doesn't detect ambiguity
        "requires_clarification": False,  # Simplified prompt doesn't handle clarification
        "clarification_questions": [],  # Simplified prompt doesn't provide questions
        "confidence": confidence,
        "reasoning": data.get("reasoning", ""),
    }


def _parse_router_response(response: str) -> RouterAnalysis:
    """Parse router model response into RouterAnalysis with validation."""
    try:
        data = _extract_json_from_response(response)
        if data is None:
            raise ValueError("Could not extract JSON from response")
        
        validated_data = _validate_router_analysis(data)
        
        return RouterAnalysis(**validated_data)
    except Exception as e:
        logger.warning(f"Failed to parse router response: {e}")
        if response:
            logger.debug(f"Router response content (first 200 chars): {response[:200]}")
        # Return safe defaults
        return RouterAnalysis(
            complexity="medium",
            query_type="other",
            domain="general",
            tool_categories=[],
            recommended_tools=[],
            recommended_model=None,
            can_use_local=True,
            estimated_cost=0.0,

            estimated_input_tokens=0,
            estimated_output_tokens=0,
            optimal_context_window=None,
            is_ambiguous=False,
            requires_clarification=False,
            clarification_questions=[],
            confidence=0.3,
            reasoning=f"Parse error: {e}",
        )


def _create_cache_key(
    query: str,
    messages: List[Dict[str, Any]],
    tool_count: int = 0,
    model_count: int = 0
) -> str:
    """Create intelligent cache key using semantic similarity."""
    # Extract core query intent (normalize for better cache hits)
    query_text = query.lower().strip()
    if messages:
        user_msgs = [m.get("content", "").lower().strip() for m in messages if m.get("role") == "user"]
        if user_msgs:
            query_text = user_msgs[0]

    # Normalize query by removing common variations
    # This allows similar queries to share cache entries
    normalized = _normalize_query_for_cache(query_text)

    # Include context (tool availability affects routing decisions)
    key_data = f"{normalized}:t{tool_count}:m{model_count}"
    return hashlib.md5(key_data.encode()).hexdigest()

def _normalize_query_for_cache(query: str) -> str:
    """Normalize query text for better cache hit rates."""
    import re

    # Remove punctuation and extra whitespace
    normalized = re.sub(r'[^\w\s]', ' ', query)
    normalized = ' '.join(normalized.split())

    # Extract key intent words (remove stop words)
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}

    words = [w for w in normalized.split() if w not in stop_words]

    # Take first 5-7 significant words (enough to capture intent without being too specific)
    intent_words = words[:7]

    return ' '.join(intent_words)


async def _get_cached_analysis(cache_key: str, memory_server: Optional[Any] = None) -> Optional['RouterAnalysis']:
    """
    Get cached analysis from database (source of truth) with in-memory fallback.
    Database is checked first, in-memory cache is performance optimization.
    """
    # 1. Check database first (source of truth)
    if memory_server:
        try:
            from agent_runner.db_utils import run_query_with_memory
            query = """
            SELECT analysis_json, created_at, expires_at 
            FROM router_analysis_cache 
            WHERE cache_key = $key 
            AND (expires_at IS NONE OR expires_at > time::now())
            LIMIT 1;
            """
            results = await run_query_with_memory(memory_server, query, {"key": cache_key})
            if results and len(results) > 0:
                row = results[0]
                analysis_json = row.get("analysis_json")
                if analysis_json:
                    try:
                        analysis_dict = json.loads(analysis_json)
                        # Reconstruct RouterAnalysis from dict
                        analysis = RouterAnalysis(**analysis_dict)
                        # Update in-memory cache for fast access
                        with _cache_lock:
                            _router_cache[cache_key] = (time.time(), analysis)
                            _router_cache.move_to_end(cache_key)
                        logger.debug(f"Router cache hit from database: {cache_key[:8]}")
                        return analysis
                    except Exception as e:
                        logger.warning(f"Failed to parse cached analysis from DB: {e}")
        except Exception as e:
            logger.debug(f"Database cache lookup failed, using in-memory: {e}")
    
    # 2. Fallback to in-memory cache (performance optimization)
    with _cache_lock:
        if cache_key in _router_cache:
            cached_time, cached_analysis = _router_cache[cache_key]
            if time.time() - cached_time < ROUTER_CACHE_TTL:
                # Move to end (LRU)
                _router_cache.move_to_end(cache_key)
                return cached_analysis
            else:
                # Cache expired
                del _router_cache[cache_key]
    return None


async def _set_cached_analysis(cache_key: str, analysis: 'RouterAnalysis', memory_server: Optional[Any] = None) -> None:
    """
    Store cached analysis in database (source of truth) and update in-memory cache.
    Database is primary, in-memory is performance optimization.
    """
    # 1. Store in database (source of truth)
    if memory_server:
        try:
            from agent_runner.db_utils import run_query_with_memory
            analysis_dict = {
                "complexity": analysis.complexity,
                "query_type": analysis.query_type,
                "domain": analysis.domain,
                "tool_categories": analysis.tool_categories,
                "recommended_tools": analysis.recommended_tools,
                "recommended_model": analysis.recommended_model,
                "can_use_local": analysis.can_use_local,
                "estimated_cost": analysis.estimated_cost,
                "estimated_input_tokens": analysis.estimated_input_tokens,
                "estimated_output_tokens": analysis.estimated_output_tokens,
                "optimal_context_window": analysis.optimal_context_window,
                "is_ambiguous": analysis.is_ambiguous,
                "requires_clarification": analysis.requires_clarification,
                "clarification_questions": analysis.clarification_questions,
                "confidence": analysis.confidence,
                "reasoning": analysis.reasoning,
            }
            analysis_json = json.dumps(analysis_dict)
            expires_at = time.time() + ROUTER_CACHE_TTL
            
            query = """
            UPSERT type::thing('router_analysis_cache', $key)
            SET cache_key = $key,
                analysis_json = $json,
                created_at = time::now(),
                expires_at = time::from_unix($expires);
            """
            await run_query_with_memory(memory_server, query, {
                "key": cache_key,
                "json": analysis_json,
                "expires": expires_at
            })
            logger.debug(f"Router cache stored in database: {cache_key[:8]}")
        except Exception as e:
            logger.warning(f"Failed to store router cache in DB: {e}")
    
    # 2. Update in-memory cache (performance optimization)
    with _cache_lock:
        _router_cache[cache_key] = (time.time(), analysis)
        _router_cache.move_to_end(cache_key)
        
        # Evict oldest if over limit
        while len(_router_cache) > _cache_max_size:
            _router_cache.popitem(last=False)  # Remove oldest


async def analyze_query(
    query: str,
    messages: List[Dict[str, Any]],
    gateway_base: str,
    http_client: Any,
    available_tools: Optional[List[Dict[str, Any]]] = None,
    available_models: Optional[List[str]] = None,
    memory_server: Optional[Any] = None,
    use_cache: bool = True,
    circuit_breaker_state: Optional[Dict[str, Dict[str, Any]]] = None
) -> RouterAnalysis:
    """
    Analyze a query using the router model.
    
    Args:
        query: The user query
        messages: Full conversation messages
        gateway_base: Gateway base URL
        http_client: HTTP client for making requests
        available_tools: List of available tools (for filtering)
        available_models: List of available models (for recommendations)

        use_cache: Whether to use cached results
    
    Returns:
        RouterAnalysis with routing recommendations
    """
    if not ROUTER_ENABLED:
        # Return neutral analysis if router disabled
        return RouterAnalysis(
            complexity="medium",
            query_type="other",
            domain="general",
            tool_categories=[],
            recommended_tools=[],
            recommended_model=None,
            can_use_local=True,
            estimated_cost=0.0,

            estimated_input_tokens=0,
            estimated_output_tokens=0,
            optimal_context_window=None,
            is_ambiguous=False,
            requires_clarification=False,
            clarification_questions=[],
            confidence=0.0,
            reasoning="Router disabled",
        )
    
    # Check cache
    if use_cache:
        tool_count = len(available_tools) if available_tools else 0
        model_count = len(available_models) if available_models else 0
        cache_key = _create_cache_key(query, messages, tool_count, model_count)
        cached_analysis = await _get_cached_analysis(cache_key, memory_server)
        if cached_analysis:
            logger.debug("Using cached router analysis for query")
            return cached_analysis
    
    # Build analysis prompt
    user_query = query
    if messages:
        user_msgs = [m.get("content", "") for m in messages if m.get("role") == "user"]
        if user_msgs:
            user_query = user_msgs[-1]  # Use most recent user message
    
    # Get tool names for context
    tool_names = []
    if available_tools:
        for tool in available_tools:
            tool_name = tool.get("function", {}).get("name", "")
            if tool_name:
                tool_names.append(tool_name)
    
    # Build circuit breaker status for router context
    disabled_servers = []
    if circuit_breaker_state:
        now = time.time()
        for server_name, cb_state in circuit_breaker_state.items():
            state = cb_state.get("state", "closed")
            disabled_until = cb_state.get("disabled_until", 0.0)
            if state == "open" and disabled_until > now:
                disabled_servers.append(server_name)
    
    circuit_breaker_info = ""
    if disabled_servers:
        circuit_breaker_info = f"\n\n⚠️ IMPORTANT: The following MCP servers are currently disabled (circuit breaker open): {', '.join(disabled_servers)}. Do NOT recommend tools from these servers."
    
    # Build semantic paraphrasing examples for available categories
    available_categories = set()
    if available_tools:
        tool_category_map = _build_tool_category_map()
        for tool in available_tools:
            tool_name = tool.get("function", {}).get("name", "")
            category = tool_category_map.get(tool_name)
            if category:
                available_categories.add(category)
    
    # Build category examples section
    category_examples_text = ""
    if available_categories:
        examples_list = []
        for cat in sorted(available_categories):
            if cat in TOOL_CATEGORY_EXAMPLES:
                examples = TOOL_CATEGORY_EXAMPLES[cat]
                examples_list.append(f"  - {cat}: {', '.join(examples[:8])}")
        if examples_list:
            category_examples_text = "\n\nTool Category Examples (semantic paraphrasing):\n" + "\n".join(examples_list)
    
    # Build negative constraint examples section
    negative_examples_text = ""
    if NEGATIVE_CONSTRAINT_EXAMPLES:
        negative_list = []
        for ex in NEGATIVE_CONSTRAINT_EXAMPLES[:8]:  # Show top 8 examples
            negative_list.append(f"  - Query: '{ex['query']}' → NOT {ex['wrong_category']} (use {ex['correct_category']} instead: {ex['reason']})")
        if negative_list:
            negative_examples_text = "\n\n⚠️ Important: Avoid misclassification. Examples of what NOT to do:\n" + "\n".join(negative_list)
    
    # Optimized shorter prompt for faster inference
    prompt = f"""Analyze this query and return JSON routing recommendations.

Query: {user_query}

Available tools: {', '.join(tool_names[:10]) if tool_names else 'Various tools available'}

Return JSON:
{{
  "complexity": "simple|medium|complex|very_complex",
  "query_type": "coding|research|automation|analysis|creative|other",
  "domain": "technical|business|creative|general",
  "tool_categories": ["filesystem", "web_search", "code", "system"],
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation"
}}

Guidelines: Simple=local models, Complex=cloud models. Match tools to intent."""
    
    try:
        start_time = time.time()
        response, confidence_from_logprobs = await _call_router_model(prompt, gateway_base, http_client)
        elapsed = time.time() - start_time
        analysis = _parse_router_response(response)
        
        # Store original JSON confidence before override
        original_json_confidence = analysis.confidence
        
        # Override confidence with logprobs if available (more accurate)
        if confidence_from_logprobs is not None:
            logger.debug(f"Using logprobs confidence ({confidence_from_logprobs:.3f}) instead of JSON confidence ({analysis.confidence:.3f})")
            analysis.confidence = confidence_from_logprobs
        
        logger.debug(f"Router analysis completed in {elapsed:.2f}s")
        
        # Cache the result
        if use_cache:
            tool_count = len(available_tools) if available_tools else 0
            model_count = len(available_models) if available_models else 0
            cache_key = _create_cache_key(query, messages, tool_count, model_count)
            await _set_cached_analysis(cache_key, analysis, memory_server)
        
        logger.info(
            "router_analysis",
            extra={
                "complexity": analysis.complexity,
                "query_type": analysis.query_type,
                "tool_categories": analysis.tool_categories,
                "recommended_model": analysis.recommended_model,
                "confidence": analysis.confidence,
                "estimated_input_tokens": analysis.estimated_input_tokens,
                "estimated_output_tokens": analysis.estimated_output_tokens,
            }
        )
        
        # Track router analysis for categorization analytics
        track_event(
            event="router_analysis_complete",
            severity=EventSeverity.INFO,
            category=EventCategory.SYSTEM,
            message=f"Router analysis completed for query type '{analysis.query_type}'",
            metadata={
                "query_type": analysis.query_type,
                "complexity": analysis.complexity,
                "domain": analysis.domain,
                "tool_categories": analysis.tool_categories,
                "recommended_tools_count": len(analysis.recommended_tools),
                "recommended_tools": analysis.recommended_tools[:10],  # Sample
                "confidence": analysis.confidence,
                "confidence_from_logprobs": confidence_from_logprobs is not None,
                "original_json_confidence": original_json_confidence,
                "confidence_delta": abs(original_json_confidence - analysis.confidence) if confidence_from_logprobs is not None else 0.0,
                "confidence_bucket": _bucket_confidence(analysis.confidence),
                "recommended_model": analysis.recommended_model,
                "can_use_local": analysis.can_use_local,
                "is_ambiguous": analysis.is_ambiguous,
                "requires_clarification": analysis.requires_clarification,
                "elapsed_seconds": elapsed,
            }
        )
        
        # Track low confidence events for analysis
        if analysis.confidence < 0.5:
            track_event(
                event="router_low_confidence",
                severity=EventSeverity.MEDIUM,
                category=EventCategory.SYSTEM,
                message=f"Router returned low confidence ({analysis.confidence:.3f}) for query type '{analysis.query_type}'",
                metadata={
                    "confidence": analysis.confidence,
                    "query_type": analysis.query_type,
                    "complexity": analysis.complexity,
                    "domain": analysis.domain,
                    "is_ambiguous": analysis.is_ambiguous,
                    "requires_clarification": analysis.requires_clarification,
                    "confidence_from_logprobs": confidence_from_logprobs is not None,
                    "query_sample": query[:200] if query else "",  # Sample for analysis
                }
            )
        
        return analysis
    except Exception as e:
        logger.warning(f"Router analysis failed: {e}, using fallback")
        # Return safe fallback
        return RouterAnalysis(
            complexity="medium",
            query_type="other",
            domain="general",
            tool_categories=[],
            recommended_tools=[],
            recommended_model=None,
            can_use_local=True,
            estimated_cost=0.0,

            estimated_input_tokens=0,
            estimated_output_tokens=0,
            optimal_context_window=None,
            is_ambiguous=False,
            requires_clarification=False,
            clarification_questions=[],
            confidence=0.0,
            reasoning=f"Router error: {e}",
        )


def _extract_tool_description(tool: Dict[str, Any]) -> str:
    """Extract tool description from tool definition."""
    func = tool.get("function", {})
    description = func.get("description", "")
    name = func.get("name", "")
    return f"{name} {description}".strip()


def _categorize_tool_by_pattern(tool_name: str, tool_description: str = "") -> Optional[str]:
    """
    Automatically categorize tool based on name and description patterns.
    
    This provides automatic categorization for tools not in the hardcoded map,
    improving scalability and reducing manual work.
    """
    tool_lower = tool_name.lower()
    desc_lower = tool_description.lower()
    combined_text = f"{tool_lower} {desc_lower}"
    
    # Pattern-based categorization (order matters - more specific first)
    patterns = {
        "web_search": [
            r"web_search", 
            r"brave_search", r"google.*search", r"search.*web", r"lookup.*web",
            r"find.*information", r"research.*web"
        ],
        "filesystem": [
            r"read.*file", r"write.*file", r"list.*dir", r"path.*info",
            r"create.*file", r"delete.*file", r"copy.*file", r"move.*file",
            r"find.*file", r"watch.*path", r"make_dir", r"remove_file",
            r"remove_dir", r"append_text", r"batch_operations", r"query_static_resources"
        ],
        "code": [
            r"execute.*command", r"run.*script", r"sequential.*thinking", r"thinking",
            r"debug", r"refactor", r"compile", r"test.*code"
        ],
        "browser": [
            r"browser.*navigate", r"browser.*click", r"browser.*type", r"browser.*screenshot",
            r"browser.*snapshot", r"browser.*evaluate", r"playwright", r"automate.*web",
            r"interact.*page", r"web.*automation"
        ],
        "memory": [
            r"store.*fact", r"query.*fact", r"semantic.*search", r"project_memory",
            r"remember", r"recall", r"knowledge.*base", r"delete.*fact", r"check.*health.*memory"
        ],
        "scraping": [
            r"scrape", r"extract.*structured.*data", r"scrapezy",
            r"parse.*html", r"crawl.*web", r"extract.*data"
        ],
        "weather": [
            r"weather", r"forecast", r"temperature", r"climate", r"get_weather"
        ],
        "http": [
            r"http.*request", r"api.*call", r"fetch.*url", r"post.*endpoint", r"get.*endpoint"
        ],
        "automation": [
            r"automate", r"automator", r"execute.*script", r"workflow", r"task.*automation"
        ],
        "document": [
            r"convert.*document", r"pandoc", r"transform.*file", r"export.*document"
        ],
        "ollama": [
            r"ollama", r"list.*model", r"pull.*model", r"delete.*model", r"show.*model",
            r"generate.*embeddings", r"manage.*model"
        ]
    }
    
    for category, pattern_list in patterns.items():
        for pattern in pattern_list:
            if re.search(pattern, combined_text, re.IGNORECASE):
                return category
    
    return None


def _bucket_confidence(confidence: float) -> str:
    """Bucket confidence into categories for analytics."""
    if confidence >= 0.8:
        return "high"
    elif confidence >= 0.5:
        return "medium"
    elif confidence >= 0.3:
        return "low"
    else:
        return "very_low"


def _normalize_category(category: str) -> str:
    """Normalize category name using synonyms."""
    category_lower = category.lower()
    
    # Check if it's already a valid category
    if category_lower in VALID_CATEGORIES:
        return category_lower
    
    # Check synonyms
    for valid_cat, synonyms in CATEGORY_SYNONYMS.items():
        if category_lower in synonyms or category_lower == valid_cat:
            return valid_cat
    
    return category_lower  # Return as-is if no match


def _validate_categories(categories: List[str]) -> List[str]:
    """Validate and filter out invalid categories."""
    if not categories:
        return []
    
    valid = []
    invalid = []
    
    for cat in categories:
        normalized = _normalize_category(cat)
        if normalized in VALID_CATEGORIES:
            if normalized not in valid:  # Avoid duplicates
                valid.append(normalized)
        else:
            invalid.append(cat)
    
    if invalid:
        logger.debug(f"Router returned invalid categories: {invalid}, ignoring them")
        # Track invalid categories for analysis
        track_event(
            event="router_invalid_categories",
            severity=EventSeverity.DEBUG,
            category=EventCategory.SYSTEM,
            message=f"Router returned {len(invalid)} invalid categories",
            metadata={
                "invalid_categories": invalid,
                "valid_categories": valid,
                "total_requested": len(categories),
            }
        )
    
    return valid


def _get_tool_category(tool_name: str, tool_description: str = "") -> Optional[str]:
    """
    Get tool category with automatic fallback.
    
    Strategy:
    1. Check hardcoded map (most reliable)
    2. Try pattern-based categorization
    3. Try MCP server name pattern
    4. Return None if no match
    
    Tracks categorization method for analytics.
    """
    categorization_method = None
    category = None
    
    # First, check hardcoded map (most reliable)
    tool_category_map = _build_tool_category_map()
    if tool_name in tool_category_map:
        category = tool_category_map[tool_name]
        categorization_method = "hardcoded_map"
    else:
        # Second, try pattern-based categorization
        category = _categorize_tool_by_pattern(tool_name, tool_description)
        if category:
            categorization_method = "pattern_match"
        else:
            # Third, try MCP server name pattern
            if tool_name.startswith("mcp__"):
                parts = tool_name.split("__")
                if len(parts) >= 2:
                    server_name = parts[1].lower()
                    server_to_category = {
                        "exa": "web_search",
                        "tavily_search": "web_search",
                        "perplexity": "web_search",
                        "brave_search": "web_search",
                        "playwright": "browser",
                        "project_memory": "memory",

                        "scrapezy": "scraping",
                        "macos_automator": "automation",
                        "ollama": "ollama",
                        "mcp_pandoc": "document",
                        "weather": "weather",
                    }
                    if server_name in server_to_category:
                        category = server_to_category[server_name]
                        categorization_method = "server_name"
    
    # Track categorization decision for analytics
    track_event(
        event="tool_categorization",
        severity=EventSeverity.DEBUG,
        category=EventCategory.SYSTEM,
        message=f"Tool '{tool_name}' categorized as '{category or 'uncategorized'}'",
        metadata={
            "tool_name": tool_name,
            "category": category,
            "categorization_method": categorization_method or "none",
            "has_description": bool(tool_description),
            "description_length": len(tool_description) if tool_description else 0,
            "is_mcp_tool": tool_name.startswith("mcp__"),
        }
    )
    
    return category


def _build_tool_category_map() -> Dict[str, str]:
    """Build comprehensive tool name to category mapping (cached)."""
    global _tool_category_map
    
    if _tool_category_map is not None:
        return _tool_category_map
    
    with _category_map_lock:
        # Double-check after acquiring lock
        if _tool_category_map is not None:
            return _tool_category_map
        
        _tool_category_map = {
        # Web search tools

        "mcp__brave_search__brave_search": "web_search",
        # Filesystem tools
        "read_text": "filesystem",
        "write_text": "filesystem",
        "list_dir": "filesystem",
        "path_info": "filesystem",
        # Code tools
        "execute_command": "code",
        "mcp__thinking__sequentialthinking": "code",
        # Browser tools
        "mcp__playwright__browser_navigate": "browser",
        "mcp__playwright__browser_click": "browser",
        "mcp__playwright__browser_type": "browser",
        "mcp__playwright__browser_take_screenshot": "browser",
        "mcp__playwright__browser_snapshot": "browser",
        "mcp__playwright__browser_evaluate": "browser",
        # Memory tools
        "mcp__project_memory__query_facts": "memory",
        "mcp__project_memory__store_fact": "memory",
        "mcp__project_memory__semantic_search": "memory",
        "mcp__project_memory__delete_fact": "memory",
        "mcp__project_memory__check_health": "memory",
        # Scraping tools

        "mcp__scrapezy__extract_structured_data": "scraping",
        # Automation tools
        "mcp__macos_automator__execute_script": "automation",
        # HTTP tools
        "http_request": "http",
        # Ollama management tools
        "mcp__ollama__list_models": "ollama",
        "mcp__ollama__pull_model": "ollama",
        "mcp__ollama__delete_model": "ollama",
        "mcp__ollama__show_model": "ollama",
        "mcp__ollama__generate_embeddings": "ollama",
        # Document tools
        "mcp__mcp_pandoc__convert": "document",
        # Weather tools
        "mcp__weather__get_weather": "weather",
        }
        return _tool_category_map


def filter_tools_by_categories(
    all_tools: List[Dict[str, Any]],
    categories: List[str],
    recommended_tools: List[str]
) -> List[Dict[str, Any]]:
    """
    Filter tools based on router analysis with improved categorization and fallback.
    
    Args:
        all_tools: All available tools
        categories: Tool categories to include (will be validated)
        recommended_tools: Specific tool names to include
    
    Returns:
        Filtered list of tools (guaranteed non-empty, falls back if needed)
    """
    # Validate categories first
    categories = _validate_categories(categories)
    
    if not categories and not recommended_tools:
        # No filtering requested, return all
        return all_tools
    
    filtered = []
    uncategorized = []
    
    for tool in all_tools:
        tool_name = tool.get("function", {}).get("name", "")
        tool_description = _extract_tool_description(tool)
        
        # Always include if specifically recommended
        if tool_name in recommended_tools:
            filtered.append(tool)
            continue
        
        # Get category (with automatic fallback)
        tool_category = _get_tool_category(tool_name, tool_description)
        
        if tool_category and tool_category in categories:
            filtered.append(tool)
        elif not tool_category:
            # Track uncategorized tools for potential fallback
            uncategorized.append(tool)
    
    # If we have uncategorized tools and no filtered tools, include some uncategorized
    # (fallback to prevent over-filtering)
    if not filtered and uncategorized:
        logger.debug(
            f"No tools matched categories {categories}, including {min(len(uncategorized), 10)} uncategorized tools as fallback"
        )
        # Track uncategorized tools for analysis
        track_event(
            event="uncategorized_tools_fallback",
            severity=EventSeverity.INFO,
            category=EventCategory.SYSTEM,
            message=f"Used {len(uncategorized)} uncategorized tools as fallback",
            metadata={
                "uncategorized_count": len(uncategorized),
                "requested_categories": categories,
                "uncategorized_tools": [t.get("function", {}).get("name", "") for t in uncategorized[:10]],
            }
        )
        filtered = uncategorized[:10]  # Limit fallback to prevent too many tools
    elif uncategorized:
        # Track uncategorized tools even when we have matches (for analysis)
        track_event(
            event="uncategorized_tools_detected",
            severity=EventSeverity.DEBUG,
            category=EventCategory.SYSTEM,
            message=f"Found {len(uncategorized)} uncategorized tools",
            metadata={
                "uncategorized_count": len(uncategorized),
                "filtered_count": len(filtered),
                "requested_categories": categories,
                "uncategorized_tools": [t.get("function", {}).get("name", "") for t in uncategorized[:20]],  # Sample
            }
        )
    
    # Final fallback: if still empty, return all (safety net)
    if not filtered:
        logger.warning("Router tool filtering resulted in empty list, using all tools as final fallback")
        return all_tools
    
    logger.debug(f"Router filtered {len(all_tools)} tools to {len(filtered)} based on categories: {categories}")
    return filtered


def filter_tools_by_router_analysis(
    all_tools: List[Dict[str, Any]],
    router_analysis: RouterAnalysis,
    mode: str = "moderate",
    min_confidence: float = 0.7,
    max_tools_aggressive: int = 5,
    max_tools_moderate: int = 15
) -> List[Dict[str, Any]]:
    """
    Enhanced tool filtering based on router analysis with confidence-based strategies.
    
    This function provides zero-latency filtering by reusing the existing router analysis.
    No additional LLM calls are made - filtering is purely synchronous list operations.
    
    Strategy:
    1. Aggressive mode (high confidence + specific recommendations):
       - Use ONLY recommended_tools if confidence >= min_confidence
       - Limit to max_tools_aggressive
    2. Moderate mode (category-based):
       - Use category-based filtering
       - Limit to max_tools_moderate
    3. Fallback:
       - Use all tools if no recommendations or low confidence
    
    Args:
        all_tools: All available tools
        router_analysis: Router analysis result (already computed, cached)
        mode: Filtering mode - "aggressive" | "moderate" | "disabled"
        min_confidence: Minimum confidence for aggressive filtering (0.0-1.0)
        max_tools_aggressive: Maximum tools in aggressive mode
        max_tools_moderate: Maximum tools in moderate mode
    
    Returns:
        Filtered list of tools (guaranteed non-empty, falls back to all_tools if needed)
    """
    if mode == "disabled":
        return all_tools
    
    original_count = len(all_tools)
    
    # Strategy 1: Aggressive filtering (high confidence + specific recommendations)
    if (mode == "aggressive" and 
        router_analysis.confidence >= min_confidence and 
        router_analysis.recommended_tools):
        
        # Filter to only recommended tools
        filtered = []
        for tool in all_tools:
            tool_name = tool.get("function", {}).get("name", "")
            if tool_name in router_analysis.recommended_tools:
                filtered.append(tool)
        
        # Also include mcp_proxy if any MCP tools are recommended (needed for MCP calls)
        has_mcp_tool = any(
            name.startswith("mcp__") or name == "mcp_proxy"
            for name in router_analysis.recommended_tools
        )
        if has_mcp_tool:
            for tool in all_tools:
                if tool.get("function", {}).get("name") == "mcp_proxy":
                    if tool not in filtered:
                        filtered.append(tool)
                    break
        
        # Limit to max_tools_aggressive
        if len(filtered) > max_tools_aggressive:
            # Prioritize recommended tools, then add mcp_proxy if needed
            filtered = filtered[:max_tools_aggressive]
        
        if filtered:
            reduction = (1 - len(filtered) / original_count) * 100
            logger.info(
                "router_aggressive_filtering",
                extra={
                    "mode": "aggressive",
                    "confidence": router_analysis.confidence,
                    "tools_before": original_count,
                    "tools_after": len(filtered),
                    "reduction_pct": reduction,
                    "recommended_tools": router_analysis.recommended_tools,
                }
            )
            # Track confidence-based filtering decision
            track_event(
                event="router_confidence_decision",
                severity=EventSeverity.DEBUG,
                category=EventCategory.SYSTEM,
                message=f"Aggressive filtering used with confidence {router_analysis.confidence:.3f}",
                metadata={
                    "confidence": router_analysis.confidence,
                    "filtering_mode": "aggressive",
                    "min_confidence_threshold": min_confidence,
                    "used_aggressive": True,
                    "tools_before": original_count,
                    "tools_after": len(filtered),
                    "reduction_pct": reduction,
                }
            )
            return filtered
    
    # Strategy 2: Moderate filtering (category-based)
    if router_analysis.tool_categories or router_analysis.recommended_tools:
        filtered = filter_tools_by_categories(
            all_tools,
            router_analysis.tool_categories,
            router_analysis.recommended_tools
        )
        
        # Limit to max_tools_moderate in moderate mode
        if mode == "moderate" and len(filtered) > max_tools_moderate:
            # Prioritize recommended tools first
            recommended_filtered = [
                t for t in filtered 
                if t.get("function", {}).get("name") in router_analysis.recommended_tools
            ]
            other_filtered = [
                t for t in filtered 
                if t.get("function", {}).get("name") not in router_analysis.recommended_tools
            ]
            # Take recommended tools + fill rest from categories
            filtered = recommended_filtered + other_filtered[:max_tools_moderate - len(recommended_filtered)]
        
        if filtered and len(filtered) < original_count:
            reduction = (1 - len(filtered) / original_count) * 100
            logger.info(
                "router_moderate_filtering",
                extra={
                    "mode": "moderate",
                    "confidence": router_analysis.confidence,
                    "tools_before": original_count,
                    "tools_after": len(filtered),
                    "reduction_pct": reduction,
                    "categories": router_analysis.tool_categories,
                }
            )
            # Track confidence-based filtering decision
            track_event(
                event="router_confidence_decision",
                severity=EventSeverity.DEBUG,
                category=EventCategory.SYSTEM,
                message=f"Moderate filtering used with confidence {router_analysis.confidence:.3f}",
                metadata={
                    "confidence": router_analysis.confidence,
                    "filtering_mode": "moderate",
                    "min_confidence_threshold": min_confidence,
                    "used_aggressive": False,
                    "tools_before": original_count,
                    "tools_after": len(filtered),
                    "reduction_pct": reduction,
                }
            )
        return filtered
    
    # Strategy 3: Fallback (use all tools)
    logger.debug("Router filtering: no recommendations, using all tools")
    return all_tools





def get_model_from_analysis(
    analysis: RouterAnalysis,
    default_model: str,
    local_models: List[str],
    cloud_models: List[str]
) -> str:
    """Get recommended model from router analysis with validation."""
    if analysis.recommended_model:
        # Validate recommended model is available
        all_models = local_models + cloud_models
        if analysis.recommended_model in all_models:
            return analysis.recommended_model
        logger.warning(f"Router recommended model '{analysis.recommended_model}' not available, using fallback")
    
    # Use router's recommendation logic
    if analysis.can_use_local and local_models:
        # Prefer Qwen 3 30B for medium complexity, mistral for simple
        if analysis.complexity in ["medium", "complex"] and "ollama:qwen3:30b" in local_models:
            return "ollama:qwen3:30b"
        return local_models[0]  # Use first available local model
    
    if analysis.complexity in ["complex", "very_complex"] and cloud_models:
        # Use first available cloud model for complex queries (Grok-3/GPT-4o)
        return cloud_models[0]
    
    return default_model

