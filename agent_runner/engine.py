import logging
import os
import time
import json
import asyncio
import re
from typing import Dict, List, Any, Optional, Tuple, AsyncGenerator
from fastapi import HTTPException

from agent_runner.state import AgentState
from common.constants import OBJ_MODEL, ROLE_SYSTEM, ROLE_TOOL
from common.unified_tracking import track_event, EventSeverity, EventCategory
import agent_runner.intent as intent
from agent_runner.executor import ToolExecutor
from common.notifications import notify_critical
from common.budget import get_budget_tracker
from common.constants import (
    OBJ_MODEL, ROLE_SYSTEM, ROLE_TOOL,
    DEFAULT_FALLBACK_MODEL, DEFAULT_CONTEXT_PRUNE_LIMIT
)
from common.message_utils import extract_text_content, get_message_text
from agent_runner.prompts import get_healer_prompt, get_base_system_instructions, get_service_alerts
from agent_runner.memory_server import MemoryServer
from agent_runner.nexus import Nexus
from agent_runner.hallucination_detector import HallucinationDetector, DetectorConfig
from agent_runner.knowledge_base import KnowledgeBase
from agent_runner.memory_client import DirectMemoryClient
import math

logger = logging.getLogger("agent_runner")
STREAM_DEBUG_ENABLED = os.getenv("STREAM_DEBUG", "").lower() in ("1", "true", "yes")


def _redact_preview(text: Any) -> str:
    """Redact long token-ish strings to avoid leaking secrets in stream logs."""
    if text is None:
        return ""
    preview = str(text)
    # Replace any long token-like spans (e.g., API keys) with placeholders
    preview = re.sub(r"[A-Za-z0-9]{16,}", "***", preview)
    return preview[:80]

class AgentEngine:
    def __init__(self, state: AgentState, memory_client=None):
        self.state = state
        self.executor = ToolExecutor(state)
        self.memory = MemoryServer(state)
        # Use injected memory client for context operations, fallback to direct memory server
        self.memory_client = memory_client or DirectMemoryClient(self.memory)
        self.nexus = Nexus(state, self)

        # Ensure conversation cache exists before any async init runs
        self._conversation_cache = {}
        self._conversation_cache_size = 10  # Cache up to 10 conversations
        self._initialized = False

        # Initialize hallucination detection system
        detector_config = DetectorConfig(
            enabled=self.state.hallucination_detection_enabled,
            fact_check_enabled=True,
            math_verification_enabled=True,
            temporal_check_enabled=True,
            learning_enabled=True,
            feedback_collection_enabled=True
        )

    async def async_initialize(self):
        """Async initialization for components that require event loop."""
        if getattr(self, "_initialized", False):
            return

        # Executor may not provide async initialization in all builds
        if hasattr(self.executor, "async_initialize"):
            await self.executor.async_initialize()

        # Initialize hallucination detection system
        detector_config = DetectorConfig(
            enabled=self.state.hallucination_detection_enabled,
            fact_check_enabled=True,
            math_verification_enabled=True,
            temporal_check_enabled=True,
            learning_enabled=True,
            feedback_collection_enabled=True
        )
        logger.info(f"Initializing hallucination detector with config: enabled={detector_config.enabled}")
        self.hallucination_detector = HallucinationDetector(self.state, detector_config)
        self.knowledge_base = KnowledgeBase(self.state)
        logger.info("Hallucination detection system initialized successfully")

        # PHASE 3: Initialize conversation cache for performance gains
        # Cache full prompt constructions per conversation to avoid regeneration
        self._conversation_cache = {}
        self._conversation_cache_size = 10  # Cache up to 10 conversations
        logger.info("Conversation cache initialized for Phase 3 optimization")

        # QUALITY MITIGATION: Initialize tool result processor and metrics tracker
        from agent_runner.tool_result_processor import ToolResultProcessor, QualityTier
        from agent_runner.quality_metrics_tracker import QualityMetricsTracker

        self.tool_result_processor = ToolResultProcessor()
        self.quality_metrics_tracker = QualityMetricsTracker()
        self.quality_overrides = {}  # Temporary quality overrides per conversation
        logger.info("Tool result processor and quality metrics tracker initialized")

        # PHASE 4: Initialize memory query cache and optimizer for context retrieval optimization
        from agent_runner.memory_cache import MemoryQueryCache
        from agent_runner.memory_query_optimizer import MemoryQueryOptimizer

        self.memory_cache = MemoryQueryCache(
            max_cache_size=500,  # Cache up to 500 different memory queries
            default_ttl=600,     # 10 minute default TTL
            enable_metrics=True
        )

        self.memory_optimizer = MemoryQueryOptimizer(
            max_batch_size=10,   # Batch up to 10 similar queries
            max_wait_time=0.1,   # Wait up to 100ms for batch completion
            enable_metrics=True
        )
        logger.info("Memory query cache and optimizer initialized for Phase 4 optimization")

        # PHASE 3: Initialize prefix cache manager for conversation-level prompt caching
        from agent_runner.prefix_cache import PrefixCacheManager

        self.prefix_cache = PrefixCacheManager(
            max_cache_size=50,    # Cache up to 50 different prompt prefixes
            ttl_seconds=1800,     # 30 minute TTL for cached prefixes
            lru_cleanup_threshold=40  # Cleanup when cache reaches 40 entries
        )
        logger.info("Prefix cache manager initialized for Phase 3 optimization")

        self._initialized = True

    def _resolve_model_endpoint(self, model: str) -> Tuple[str, str]:
        """
        Smart Routing Mechanism:
        - If model is LOCAL (ollama:*), bypass Router and talk to Ollama directly (Port 11434).
          This fixes streaming chunks (avoids double-hop buffering) and reduces latency.
        - If model is REMOTE (openai:*, etc), use Router (Port 5455).
          This preserves governance, rate limiting, and API key management.
        """
        if model.startswith("ollama:"):
            # Direct Lane (Employee Path)
            ollama_base = os.getenv("OLLAMA_BASE", "http://127.0.0.1:11434").rstrip("/")
            # Strip prefix for raw Ollama execution
            return f"{ollama_base}/v1/chat/completions", model.replace("ollama:", "", 1)
        elif model.startswith("local:"):
             # Direct Lane (Generic Local)
             ollama_base = os.getenv("OLLAMA_BASE", "http://127.0.0.1:11434").rstrip("/")
             return f"{ollama_base}/v1/chat/completions", model.replace("local:", "", 1)
        
        # Governance Lane (Visitor Path) - Via Router
        return f"{self.state.gateway_base}/v1/chat/completions", model

    def _protected_agent_stream(self, messages: List[Dict[str, Any]], request_id: Optional[str] = None):
        """
        Protected stream access for Nexus Regulator ONLY.
        """
        return self.agent_stream(messages, request_id=request_id)

    def _check_rate_limits(self, request_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Check if the request is allowed based on rate limits.
        Uses the shared BudgetTracker from common.budget.
        """
        try:
            tracker = get_budget_tracker()
            # Check if we have budget for a minimal request
            if not tracker.check_budget(0.0):
                return {
                    "allowed": False,
                    "error": "Daily Budget Exceeded. Requests paused."
                }
            return {"allowed": True}
        except Exception as e:
            logger.warning(f"Rate limit check failed (swallowed by fail-open policy): {e}")
            
            # [PHASE 4] Robustness: configurable fail-open
            # Default to True (Fail Open) to keep system running unless strictly locked down.
            security_conf = self.state.config.get("security", {})
            fail_open = security_conf.get("fail_open_on_budget_error", True)
            
            if fail_open:
                logger.warning("Budget System Error: FAILING OPEN (Request Allowed).")
                return {"allowed": True}
            else:
                logger.critical("Budget System Error: FAILING CLOSED (Request Blocked).")
                return {
                    "allowed": False, 
                    "error": "Budget Monitor Unavailable (Strict Security Mode)"
                }

    # --- Delegate Methods to Executor ---
    
    async def discover_mcp_tools(self):
        """Delegate discovery to executor."""
        await self.executor.discover_mcp_tools()

    async def get_all_tools(self, messages: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """Delegate tool gathering to executor."""
        return await self.executor.get_all_tools(messages)

    async def execute_tool_call(self, tool_call: Dict[str, Any], request_id: Optional[str] = None) -> Dict[str, Any]:
        """Delegate execution to executor."""
        return await self.executor.execute_tool_call(tool_call, request_id)

    # --- Delegate Methods to Intent ---

    def _extract_text_content(self, content: Any) -> str:
        return intent.extract_text_content(content)

    async def _generate_search_query(self, messages: List[Dict[str, Any]]) -> str:
        return await intent.generate_search_query(messages, self.state, self.call_gateway_with_tools)

    async def _classify_search_intent(self, query: str) -> Dict[str, Any]:
        return await intent.classify_search_intent(query, self.state, self.executor.get_core_menu())

    async def call_gateway_with_tools(self, messages: List[Dict[str, Any]], model: Optional[str] = None, tools: Optional[List[Dict[str, Any]]] = None, **kwargs) -> Dict[str, Any]:
        target_model = model or self.state.agent_model
        
        
        # Universal Offline Fallback Logic
        if not self.state.internet_available:
            # Check if target model is remote. 
            # We treat 'ollama:' and 'local:' as safe. Everything else (openai:, gpt-, claude-, etc.) is suspect.
            is_safe_local = self.state.is_local_model(target_model)
            
            if not is_safe_local:
                fallback = self.state.fallback_model or DEFAULT_FALLBACK_MODEL
                if target_model != fallback:
                    logger.warning(f"OFFLINE MODE: Intercepting remote model '{target_model}'. Switching to fallback '{fallback}'.")
                    target_model = fallback

        # Prepare candidates: [Requested Model, Fallback Model]
        # We try the requested model first. If it fails or is circuit-broken, we try the fallback.
        candidates = []
        if target_model:
            candidates.append(target_model)
        
        fallback = self.state.fallback_model or DEFAULT_FALLBACK_MODEL
        if self.state.fallback_enabled and fallback not in candidates:
            candidates.append(fallback)
            
        last_error: Any = None
        
        
        headers = {}
        if self.state.router_auth_token:
            headers["Authorization"] = f"Bearer {self.state.router_auth_token}"

        client = await self.state.get_http_client()
        url = f"{self.state.gateway_base}/v1/chat/completions"

        for attempt_model in candidates:
            # 1. Smart Routing
            url, final_model = self._resolve_model_endpoint(attempt_model)

            # 2. Circuit Breaker Check
            if not self.state.mcp_circuit_breaker.is_allowed(attempt_model):
                breaker_status = self.state.mcp_circuit_breaker.get_breaker(attempt_model)
                from common.logging_utils import log_structured
                log_structured("circuit_break",
                              service=attempt_model,
                              state=breaker_status.state.value,
                              failures=breaker_status.failures,
                              threshold=breaker_status.threshold,
                              action="Wait for auto-recovery or restart services")
                last_error = f"Model '{attempt_model}' is circuit broken"
                continue
                
            # 2. Prepare Payload
            # [FIX] Distinguish between None (default tools) and [] (no tools)
            active_tools = tools if tools is not None else self.executor.tool_definitions
            payload = {
                OBJ_MODEL: final_model,
                "messages": messages,
                "tools": active_tools,
                "tool_choice": "auto",
                "stream": False,
            }

            # [PATCH] Merge kwargs (keep_alive)
            payload.update(kwargs)

            # [Optimization] Inject Context Window Limit
            # Smart Context Sizing: Allocate VRAM where it matters (Brain) and save it elsewhere.
            # Smart Context Sizing: Allocate VRAM where it matters (Brain) and save it elsewhere.
            CONTEXT_WINDOW_MAP = {
                "llama3.3:70b": 32768,      # Brain (Deep Context)
                "ollama:llama3.3:70b": 32768, # Brain (Deep Context - Prefix Variant)
                "qwen2.5:32b": 32768,        # 32k Unified
                "ollama:qwen2.5:32b": 32768,
                "llama3.1:latest": 32768,    # 32k Unified
                "ollama:llama3.1:latest": 32768,
                "llama3.2:latest": 32768,    # 32k Unified
                "ollama:llama3.2:latest": 32768,
                "llama3.2-vision:latest": 32768, # 32k Unified
                "ollama:llama3.2-vision:latest": 32768,
                "qwen2.5:7b-instruct": 32768, # 32k Unified
                "ollama:qwen2.5:7b-instruct": 32768,
            }

            # Determine target context: Use Map -> Fallback to Env -> Default 32k
            target_ctx = CONTEXT_WINDOW_MAP.get(final_model, int(os.getenv("OLLAMA_NUM_CTX", "32768")))

            if "options" not in payload:
                payload["options"] = {"num_ctx": target_ctx}
            elif "num_ctx" not in payload["options"]:
                payload["options"]["num_ctx"] = target_ctx
            
            # [COST-AUDIT] Log estimated token usage (Low CPU estimation)
            try:
                # Basic string length heuristic is sufficient for logging
                est_msg_tok = sum(len(str(m)) for m in messages) // 4
                est_tool_tok = sum(len(str(t)) for t in (tools or self.executor.tool_definitions)) // 4
                logger.info(f"[COST-AUDIT] Model: {attempt_model} | Context Limit: {target_ctx} | Est Load: ~{est_msg_tok + est_tool_tok} toks")
            except Exception as e:
                logger.debug(f"Cost audit logging failed: {e}")
            
            try:
                # 3. Attempt Call
                resp = await client.post(url, json=payload, headers=headers, timeout=self.state.http_timeout)
                resp.raise_for_status()
                data = resp.json()
                
                # 4. Success -> Record and Return
                self.state.mcp_circuit_breaker.record_success(attempt_model)
                
                # If we fell back, note it in the response (optional, but helpful for debugging/context)
                if attempt_model != target_model:
                     logger.info(f"Successfully recovered using fallback model: {attempt_model}")
                     
                return data
                
            except Exception as e:
                # 5. Failure -> Record
                if "429" in str(e):
                    # Proactive Budget Alert (Monitor Stream)
                    notify_critical(
                        title="Model Call Rejection",
                        message=f"Model '{attempt_model}' rejected call (429). Check Budget or Rate Limits.",
                        source="AgentEngine"
                    )
                
                from common.logging_utils import log_error_with_context
                log_error_with_context(
                    e, f"Model API call to {attempt_model}",
                    context={"model": attempt_model, "service": "model_api", "endpoint": self._resolve_model_endpoint(attempt_model)[0]},
                    logger_instance=logger
                )
                self.state.mcp_circuit_breaker.record_failure(attempt_model)
                last_error = str(e)
                # Continue to next candidate (fallback)

        # If we get here, all candidates failed
        from common.logging_utils import log_error_with_context
        critical_error = Exception(f"All model attempts failed. Last error: {last_error}")
        log_error_with_context(
            critical_error, "All model API calls failed",
            context={"models_attempted": candidates, "circuit_breaker_status": "checked"},
            logger_instance=logger
        )
        raise HTTPException(status_code=500, detail=f"All models failed. Last error: {str(last_error)}")



    async def _load_registry_cache(self):
        """Load permanent memory files into RAM cache."""
        try:
            registry_dir = os.path.join(self.state.agent_fs_root, "data", "permanent")
            if not os.path.exists(registry_dir):
                return ""
            
            cache_str = ""
            # Recursive Walk for Nested Project Contexts
            for root, dirs, files in os.walk(registry_dir):
                for f in files:
                    if f.endswith(".md"):
                        path = os.path.join(root, f)
                        # Relative path for the header (e.g. "antigravity/todo.md")
                        rel_path = os.path.relpath(path, registry_dir)
                        try:
                            with open(path, "r") as fh:
                                content = fh.read().strip()
                                # Header format: [Project/Filename]
                                cache_str += f"\n--- INTERNAL REGISTRY: [{rel_path}] ---\n{content}\n"
                        except Exception as read_err:
                             logger.error(f"Failed to read registry file {rel_path}: {read_err}")
            
            self.registry_cache = cache_str
            return cache_str
        except Exception as e:
            logger.error(f"Registry load error: {e}")
            return ""

    async def _get_static_prompt(self) -> str:
        """Get the static portion of the system prompt (Role, Tone, Registry)."""
        # JIT Load Registry if empty (Startup)
        if not hasattr(self, "registry_cache") or self.registry_cache is None:
            await self._load_registry_cache()

        # Build the base instructions based on internet availability
        env_instructions = get_base_system_instructions(self.state.internet_available)

        # [MEMORY REGISTRY INJECTION]
        if hasattr(self, "registry_cache") and self.registry_cache:
            env_instructions += f"\n\n### PERMANENT MEMORY REGISTRY (Always Available)\n{self.registry_cache}\n"

        # [CUSTOM PROMPT SYSTEM]
        # Check if a custom template is defined in sovereign.yaml
        custom_template = self.state.config.get("prompts", {}).get("system_template")
        
        # Base Prompt (STATIC PREFIX for Caching)
        # We start with static role definition to ensure the first ~1k tokens match every request.
        prompt = (
            "Role & tone:\n"
            "- Be professional, succinct, and conversational.\n"
            "- Use direct language. No fluff, no hype, no long disclaimers.\n"
            "\n"
            "Truthfulness & accuracy:\n"
            "- Do not invent facts, quotes, numbers, names, timelines, citations, or capabilities.\n"
            "- If uncertain, say so briefly and either (a) ask the minimum questions, or (b) offer a best-effort answer clearly labeled as an assumption.\n"
            "- When it matters, separate: (1) Known, (2) Inferred, (3) Uncertain.\n"
            "\n"
            "User-specific vs public facts:\n"
            "- For user-specific questions ('my...', 'what I said...', personal files/settings): rely on the conversation context and user-provided info. Do not web-browse for private/user-specific facts unless the user explicitly asks.\n"
            "- For public factual questions: use web verification only when needed (see Verified mode).\n"
            "\n"
            "Verified mode (enter when any of these apply):\n"
            "- The user asks for: 'latest/current/today/this week', news, prices, laws/regulations, schedules, product specs, leadership/office-holders, statistics, medical/safety guidance, or anything where being wrong is costly.\n"
            "- Or you are not confident in the answer from general knowledge.\n"
            "\n"
            "Verified mode rules:\n"
            "- Ask 1–3 clarifying questions only if required to verify correctly.\n"
            "- Verify with current reputable sources when available; cite 3–5 key sources and tie each major claim to evidence.\n"
            "- If you cannot verify, say what is missing and provide the safest/most conservative answer.\n"
            "\n"
            "Default output (non-Verified mode):\n"
            "- Answer directly in short paragraphs or 3–8 bullets.\n"
            "- No mandatory sections; keep it natural.\n"
            "\n"
            "Verified mode output:\n"
            "- Answer (bullets)\n"
            "- Evidence/Sources (links/citations tied to key claims)\n"
            "- Unknowns/Assumptions (brief)\n"
            "- Next steps (optional, brief)\n"
            "\n"
            "Tooling behavior:\n"
            "- Use available tools when verification is needed. Do not narrate tool usage ('I will use...'); just incorporate results.\n"
            "- Prefer primary/reputable sources for verification.\n"
            "\n"
            "Privacy & security:\n"
            "- Do not request or reveal secrets. Redact credentials/PII if present.\n"
        )
        return env_instructions + "\n" + prompt

    async def _get_dynamic_context(self, user_messages: Optional[List[Dict[str, Any]]] = None, skip_refinement: bool = False) -> str:
        """Get the dynamic portion of context (Time, Location, Search, Files)."""
        import datetime
        current_time_str = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            current_tz = time.tzname[0]
        except:
            current_tz = "Local"

        memory_facts = ""
        memory_status_msg = ""
        arch_ctx = ""
        
        if user_messages:
            try:
                # Use LLM to generate a context-aware search query
                # [PHASE 14] BYPASS: Skip expensive query refinement for local/periodic tasks
                # [PHASE 14] BYPASS: Skip expensive query refinement for local/periodic tasks
                # [OPTIMIZATION] MAÎTRE D' RETIREMENT: Always skip query refinement (7B) to prevent Model Swap.
                # The 70B agent is smart enough to use raw queries anyway.
                if True: # skip_refinement:
                    search_query = "" # user_messages[-1].get("content") 
                    # If we really need search, the Agent will call the 'search_web' tool explicitly.
                    # We don't need to "search memory" on every turn via LLM.
                else:
                    search_query = await self._generate_search_query(user_messages)
                
                # [FEATURE-11] Context Rehydration (Startup Awareness)
                # Use memory client abstraction for performance (direct calls) or isolation (MCP proxy)

                # Parallelize architecture facts and search queries
                parallel_tasks = [self._get_architecture_context()]

                # Add search if we have a query
                if search_query:
                    # PHASE 4: Use memory cache and optimizer for semantic search queries
                    async def optimized_semantic_search():
                        # First try cache
                        cached_result = await self.memory_cache.query_facts_cached(
                            kb_id="project_memory",
                            query=search_query,
                            limit=10
                        )
                        if cached_result:
                            return cached_result

                        # If not cached, use optimizer for potential batching
                        query_spec = {"query": search_query, "limit": 10, "kb_id": "project_memory"}
                        results = await self.memory_optimizer.optimize_semantic_search([query_spec])
                        return results[0] if results else []

                    parallel_tasks.append(optimized_semantic_search())

                # Execute in parallel
                results = await asyncio.gather(*parallel_tasks, return_exceptions=True)

                # Process architecture context (always first result)
                arch_result = results[0]
                if isinstance(arch_result, Exception):
                    logger.warning(f"Failed to hydrate architecture context: {arch_result}")
                    arch_ctx = ""
                else:
                    arch_ctx = arch_result

                # Process search result (second result if search_query exists)
                if search_query and len(results) > 1:
                    search_result = results[1]
                    if isinstance(search_result, Exception):
                        logger.warning(f"Failed to perform semantic search: {search_result}")
                        search_result = None
                    # Continue with existing search processing logic...
                    facts_data = []

                    # Extract facts from search result content
                    for content_item in search_result.content:
                        if content_item.get("type") == "text":
                            try:
                                inner_res = json.loads(content_item.get("text", "{}"))
                                facts_data.extend(inner_res.get("facts", []))
                            except:
                                pass

                    if facts_data:
                        log_facts = [f"{f.get('entity')} {f.get('relation')} {f.get('target')}" for f in facts_data]
                        logger.info(f"Memory Hit: Found {len(facts_data)} facts")
                        fact_strings = [f"- {s}" for s in log_facts]
                        memory_facts = (
                            "\n### BACKGROUND INFORMATION (Memory Context)\n"
                            "The following facts may or may not be relevant to the current conversation.\n"
                            "If a fact is useful for answering the specific question, incorporate it naturally.\n"
                            "If a fact is irrelevant, IGNORE it completely.\n\n"
                            + "\n".join(fact_strings)
                        )
                    else:
                        memory_status_msg = f"\nSYSTEM ALERT: Memory search returned no facts for query."
            except Exception as e:
                logger.warning(f"Context injection failed during prompt construction: {e}")
                memory_status_msg = f"\nSYSTEM ALERT: Long-term memory retrieval failed ({str(e)}). Context injection skipped."

        # Check for service outages via circuit breaker
        open_breakers = [name for name, b in self.state.mcp_circuit_breaker.get_status().items() if b["state"] == "open"]
        service_alerts = get_service_alerts(open_breakers, memory_status_msg)

        # Files Context
        upload_dir = os.path.join(self.state.agent_fs_root, "uploads")
        files_info = ""
        if os.path.exists(upload_dir):
            try:
                files = [f for f in os.listdir(upload_dir) if not f.startswith('.')]
                if files:
                    files.sort(key=lambda x: os.path.getmtime(os.path.join(upload_dir, x)), reverse=True)
                    file_summaries = []
                    for f in files[:10]:
                        file_summaries.append(f"- {f}")
                    
                    if file_summaries:
                        files_info = (
                            "\n### UPLOADED FILES & KNOWLEDGE BASES (Deep Context):\n"
                            "The following files were uploaded and are ready for deep processing.\n"
                            "1. TO READ RAW TEXT: Use 'read_text(path=\"uploads/{FILENAME}\")'.\n"
                            "2. TO SEARCH DEEP MEANING (RAG): Use 'search(query=\"...\")'.\n"
                            "\nRecent Uploads:\n"
                            + "\n".join(file_summaries)
                        )
            except Exception as e:
                logger.warning(f"Failed to list uploads for prompt: {e}")

        # Location Context
        location_str = "Granville, OH"
        if self.state.location and self.state.location.get("city") != "Unknown":
            loc = self.state.location
            location_str = f"{loc.get('city')}, {loc.get('region')}, {loc.get('country')}"

        context_appendix = []
        
        # Dynamic Header (Moved to Footer)
        dynamic_header = (
            f"Context:\n"
            f"- Now: {current_time_str} {current_tz}\n"
            f"- Location: {location_str} (do not assume)\n"
            "- Locale: en-US; units: imperial; currency: USD\n"
        )
        context_appendix.append(f"\n[CURRENT CONTEXT]\n{dynamic_header}")

        if service_alerts:
             context_appendix.append(f"\n[SYSTEM ALERTS]\n{service_alerts}")
        if memory_facts:
             context_appendix.append(f"\n[MEMORY CONTEXT]\n{memory_facts}")
        if arch_ctx:
             context_appendix.append(f"\n[SYSTEM ARCHITECTURE]\n{arch_ctx}")
        if files_info:
             context_appendix.append(f"\n[AVAILABLE FILES]\n{files_info}")
             
        return "\n\n" + "\n".join(context_appendix)

    async def get_system_prompt(self, user_messages: Optional[List[Dict[str, Any]]] = None, skip_refinement: bool = False, include_dynamic: bool = True) -> str:
        """Construct the system prompt. If include_dynamic=True, appends time/context (Legacy/Admin support)."""
        static_part = await self._get_static_prompt()
        if include_dynamic:
            dynamic_part = await self._get_dynamic_context(user_messages, skip_refinement)
            return static_part + dynamic_part
        return static_part

    def _apply_quality_tier_override(self, quality_tier: Optional[Any]) -> Optional[Any]:
        """Apply quality tier override for this request. Returns original tier for restoration."""
        if not quality_tier or not hasattr(self.state, "set_quality_tier"):
            return None

        try:
            from agent_runner.quality_tiers import QualityTier
            tier_enum = quality_tier if not isinstance(quality_tier, str) else QualityTier[quality_tier.upper()]

            original_tier = self.state.quality_tier
            self.state._request_quality_tier = tier_enum  # Set request-scoped override
            return original_tier
        except Exception as e:
            logger.warning(f"Failed to apply quality tier '{quality_tier}': {e}")
            return None

    async def _process_slash_commands(self, user_messages: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """Process slash commands and return (processed_messages, immediate_response)."""
        try:
            from agent_runner.services.slash_commands import SlashCommandProcessor
            processor = SlashCommandProcessor(self.state)
            processed_messages, immediate_resp = await processor.process_messages(user_messages)
            return processed_messages, immediate_resp
        except ImportError:
            return user_messages, None  # Optional dependency
        except Exception as e:
            logger.warning(f"Slash command processing failed: {e}")
            return user_messages, None

    async def _prepare_tools_for_model(self, tools: Optional[List[Dict[str, Any]]], user_messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare and filter tools for the model."""
        active_tools = tools or await self.get_all_tools(user_messages)

        # [SAFETY CLAMP] Limit excessive tools
        if len(active_tools) > self.state.max_tool_count:
            logger.warning(f"Tool Count {len(active_tools)} exceeds limit. Truncating to {self.state.max_tool_count}.")
            active_tools = active_tools[:self.state.max_tool_count]

        logger.info(f"Active Tools passed to Model: {[t['function']['name'] for t in active_tools]}")
        return active_tools

    def _prepare_conversation_context(self, user_messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prune context and validate message flow to prevent protocol violations."""
        PRUNE_LIMIT = self.state.context_prune_limit or DEFAULT_CONTEXT_PRUNE_LIMIT
        if len(user_messages) > PRUNE_LIMIT:
            original_len = len(user_messages)
            user_messages = user_messages[-PRUNE_LIMIT:]

            # Sanity Check: Don't start with a 'tool' outcome as it violates OpenAI protocol
            # (A tool message must be preceded by a tool_call)
            while user_messages and user_messages[0].get("role") == "tool":
                user_messages.pop(0)

            logger.info(f"Context Pruned: {original_len} -> {len(user_messages)} messages")

        return user_messages

    def _select_active_model(self, requested_model: Optional[str]) -> str:
        """Select appropriate model based on internet availability and preferences."""
        active_model = requested_model or self.state.agent_model

        # Context Awareness: Adjust model if offline
        if not self.state.internet_available and active_model.startswith("openai:"):
            fallback = self.state.fallback_model or DEFAULT_FALLBACK_MODEL
            logger.warning(f"Internet offline: Diverting from Cloud model to Local Fallback ({fallback})")
            active_model = fallback

        return active_model

    async def _construct_message_sequence_parallel(self, user_messages: List[Dict[str, Any]], skip_refinement: bool) -> Tuple[List[Dict[str, Any]], str]:
        """Construct the complete message sequence with parallel context loading."""
        # Load static prompt and dynamic context in parallel
        tasks = [
            self.get_system_prompt(user_messages, skip_refinement=skip_refinement, include_dynamic=False),
            self._get_dynamic_context(user_messages, skip_refinement=skip_refinement)
        ]

        static_system_prompt, dynamic_context = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle any exceptions that occurred
        if isinstance(static_system_prompt, Exception):
            logger.warning(f"Failed to get system prompt: {static_system_prompt}")
            static_system_prompt = "You are a helpful AI assistant."

        if isinstance(dynamic_context, Exception):
            logger.warning(f"Failed to get dynamic context: {dynamic_context}")
            dynamic_context = ""

        # Construct Messages
        messages = [{"role": ROLE_SYSTEM, "content": static_system_prompt}]

        # Clone user messages to avoid mutating the input list
        import copy
        processed_user_messages = copy.deepcopy(user_messages)

        # Inject Dynamic Context into the LAST User Message
        if processed_user_messages and processed_user_messages[-1].get("role") == "user":
            processed_user_messages[-1]["content"] += dynamic_context

        messages += processed_user_messages
        return messages, static_system_prompt

    async def _construct_message_sequence(self, user_messages: List[Dict[str, Any]], skip_refinement: bool) -> Tuple[List[Dict[str, Any]], str]:
        """Construct the complete message sequence with system prompts and dynamic context."""
        # Use parallel version for better performance
        return await self._construct_message_sequence_parallel(user_messages, skip_refinement)

    async def _construct_message_sequence_with_prefix_cache(self, user_messages: List[Dict[str, Any]],
                                                         conversation_state, conversation_id: str, skip_refinement: bool) -> Tuple[List[Dict[str, Any]], str, str]:
        """
        Construct message sequence using prefix caching for massive performance gains.

        PHASE 3: Separate static prefix (cached) from dynamic conversation (incremental).

        Returns:
            (messages, cache_identifier, dynamic_diff)
        """
        # PHASE 3: Build static prefix for caching
        static_prefix = await self._build_static_prefix(user_messages, skip_refinement)

        # Get cache identifier (creates cache if needed)
        cache_identifier, is_new_cache = await self.prefix_cache.get_or_create_cache(
            static_prefix, conversation_id
        )

        # Build dynamic conversation diff
        dynamic_diff = await self._build_dynamic_conversation_diff(user_messages, conversation_state, skip_refinement)

        # For cached prefixes, we only send the dynamic diff
        # The prefix is referenced by cache_identifier
        messages = []

        # Add user messages with dynamic context injected
        import copy
        processed_user_messages = copy.deepcopy(user_messages)

        # Inject dynamic context into the LAST user message
        if processed_user_messages and processed_user_messages[-1].get("role") == "user":
            processed_user_messages[-1]["content"] += dynamic_diff

        messages += processed_user_messages

        # Log cache performance
        cache_status = "NEW_CACHE" if is_new_cache else "CACHE_HIT"
        logger.info(f"PHASE 3: {cache_status} - Using cache {cache_identifier}")

        return messages, cache_identifier, dynamic_diff

    async def _build_static_prefix(self, user_messages: List[Dict[str, Any]], skip_refinement: bool) -> str:
        """Build the static prefix that gets cached (PHASE 3)"""
        prefix_parts = []

        # 1. System instructions (static)
        static_system = await self._get_static_prompt()
        prefix_parts.append(f"[SYSTEM PROMPT - STATIC/CACHED]\n{static_system}")

        # 2. Available tools (changes when tools change, but cached per combination)
        # Note: In a full implementation, this would be included in the cache key
        # For now, we'll focus on the core system prompt caching

        # 3. Architecture context (stable from Phase 1)
        try:
            arch_context = await self._get_architecture_context()
            if arch_context:
                prefix_parts.append(f"[ARCHITECTURE CONTEXT - STATIC/CACHED]\n{arch_context}")
        except Exception as e:
            logger.debug(f"Architecture context not available for prefix: {e}")

        return "\n\n".join(prefix_parts)

    async def _build_dynamic_conversation_diff(self, user_messages: List[Dict[str, Any]],
                                             conversation_state, skip_refinement: bool) -> str:
        """Build the dynamic conversation diff sent incrementally (PHASE 3)"""
        dynamic_parts = []

        # Current context (from Phase 1 stabilization)
        current_time_str = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            current_tz = time.tzname[0]
        except:
            current_tz = "Local"

        location_str = "Granville, OH"
        if self.state.location and self.state.location.get("city") != "Unknown":
            loc = self.state.location
            location_str = f"{loc.get('city')}, {loc.get('region')}, {loc.get('country')}"

        context_header = (
            f"Context:\n"
            f"- Now: {current_time_str} {current_tz}\n"
            f"- Location: {location_str} (do not assume)\n"
            "- Locale: en-US; units: imperial; currency: USD\n"
        )
        dynamic_parts.append(f"\n[CURRENT CONTEXT - DYNAMIC]\n{context_header}")

        # Service alerts (can change but usually stable)
        open_breakers = [name for name, b in self.state.mcp_circuit_breaker.get_status().items() if b["state"] == "open"]
        service_alerts = get_service_alerts(open_breakers, "")
        if service_alerts:
            dynamic_parts.append(f"\n[SYSTEM ALERTS - DYNAMIC]\n{service_alerts}")

        # Conversation state summary (from Phase 2)
        conversation_summary = conversation_state.get_compressed_prompt_addition()
        dynamic_parts.append(f"\n{conversation_summary}")

        return "\n\n".join(dynamic_parts)

    async def _construct_message_sequence_compressed(self, user_messages: List[Dict[str, Any]],
                                                   conversation_state, skip_refinement: bool) -> Tuple[List[Dict[str, Any]], str]:
        """Construct message sequence using compressed conversation state (legacy method)"""
        # Use the new prefix caching method
        messages, cache_identifier, dynamic_diff = await self._construct_message_sequence_with_prefix_cache(
            user_messages, conversation_state, "legacy-conversation", skip_refinement
        )

        # For backward compatibility, return messages and a combined "system prompt"
        # In practice, this would be handled by the caller using the cache_identifier
        return messages, f"[CACHED_PREFIX:{cache_identifier}]\n{dynamic_diff}"

    async def _get_dynamic_context_compressed(self, user_messages: Optional[List[Dict[str, Any]]],
                                            conversation_state, skip_refinement: bool) -> str:
        """Get dynamic context using compressed conversation state"""
        import datetime
        current_time_str = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            current_tz = time.tzname[0]
        except:
            current_tz = "Local"

        # Use conversation state's compressed context instead of full memory search
        compressed_context = conversation_state.get_compressed_prompt_addition()

        # Still get architecture context (stable)
        arch_ctx = await self._get_architecture_context()

        # Location Context (stable)
        location_str = "Granville, OH"
        if self.state.location and self.state.location.get("city") != "Unknown":
            loc = self.state.location
            location_str = f"{loc.get('city')}, {loc.get('region')}, {loc.get('country')}"

        context_appendix = []

        # Current Context (stable)
        dynamic_header = (
            f"Context:\n"
            f"- Now: {current_time_str} {current_tz}\n"
            f"- Location: {location_str} (do not assume)\n"
            "- Locale: en-US; units: imperial; currency: USD\n"
        )
        context_appendix.append(f"\n[CURRENT CONTEXT]\n{dynamic_header}")

        # Service alerts (can change but usually stable)
        open_breakers = [name for name, b in self.state.mcp_circuit_breaker.get_status().items() if b["state"] == "open"]
        service_alerts = get_service_alerts(open_breakers, "")
        if service_alerts:
            context_appendix.append(f"\n[SYSTEM ALERTS]\n{service_alerts}")

        # Add compressed conversation state
        context_appendix.append(f"\n{compressed_context}")

        # Architecture context (stable)
        if arch_ctx:
            context_appendix.append(f"\n[SYSTEM ARCHITECTURE]\n{arch_ctx}")

        return "\n\n" + "\n".join(context_appendix)

    async def _process_tool_calls_with_state_tracking(self, tool_calls: List[Dict[str, Any]],
                                                    conversation_state, tool_tracker, request_id: str) -> List[Dict[str, Any]]:
        """Process tool calls while tracking conversation state and return tool messages for the LLM."""

        # PHASE 5: Parallel Tool Execution - Execute independent tools concurrently
        # Filter out tools that should be avoided based on failure history
        valid_tool_calls = []
        skipped_tools = []

        for tool_call in tool_calls:
            tool_name = tool_call["function"]["name"]

            # Check if tool should be avoided based on history
            should_avoid, reason = conversation_state.should_avoid_tool(tool_name)
            if should_avoid:
                logger.warning(f"⚠️ Avoiding tool '{tool_name}' based on failure history: {reason}")
                # Record this as a "skipped" execution
                conversation_state.record_tool_execution(
                    tool_name=tool_name,
                    success=False,
                    error_message=f"Skipped due to failure history: {reason}"
                )
                skipped_tools.append((tool_call, reason))
                continue

            valid_tool_calls.append(tool_call)

        tool_messages: List[Dict[str, Any]] = []

        # Execute valid tool calls in parallel
        if valid_tool_calls:
            logger.info(f"🔄 Executing {len(valid_tool_calls)} tools in parallel")
            parallel_tasks = []

            for tool_call in valid_tool_calls:
                task = self._execute_single_tool_with_processing(
                    tool_call, conversation_state, tool_tracker, request_id
                )
                parallel_tasks.append(task)

            # Execute all tools concurrently
            parallel_results = await asyncio.gather(*parallel_tasks, return_exceptions=True)

            # Process results and add to conversation state
            for i, result in enumerate(parallel_results):
                tool_call = valid_tool_calls[i]
                tool_name = tool_call["function"]["name"]

                if isinstance(result, Exception):
                    # Handle async execution errors
                    error_msg = f"Tool execution failed: {str(result)}"
                    logger.error(f"❌ Tool '{tool_name}' failed: {error_msg}")

                    conversation_state.record_tool_execution(
                        tool_name=tool_name,
                        success=False,
                        error_message=error_msg
                    )

                    tool_tracker.record_tool_execution(tool_name, False, 0)

                    error_message_payload = {
                        "role": "tool",
                        "tool_call_id": tool_call.get("id", f"call_{tool_name}"),
                        "name": tool_name,
                        "content": f"Error: {error_msg}"
                    }
                    conversation_state.add_essential_message(error_message_payload)
                    tool_messages.append(error_message_payload)
                else:
                    # Success - result already processed by the helper method
                    processed_result, tool_message = result
                    tool_messages.append(tool_message)
                    logger.info(f"✅ Tool '{tool_name}' completed successfully")

        # Handle skipped tools (add minimal messages to conversation)
        for tool_call, reason in skipped_tools:
            tool_name = tool_call["function"]["name"]
            skipped_message = {
                "role": "tool",
                "tool_call_id": tool_call.get("id", f"call_{tool_name}"),
                "name": tool_name,
                "content": f"Skipped: {reason}"
            }
            conversation_state.add_essential_message(skipped_message)
            tool_messages.append(skipped_message)

        return tool_messages

    async def _execute_single_tool_with_processing(self, tool_call: Dict[str, Any],
                                                 conversation_state, tool_tracker, request_id: str):
        """Execute a single tool with full processing and state tracking."""
        tool_name = tool_call["function"]["name"]
        tool_args = tool_call["function"].get("arguments", "{}")

        tool_start_time = time.time()
        try:
            # Execute the tool via unified executor API
            result = await self.execute_tool_call(tool_call, request_id=request_id)

            execution_time = time.time() - tool_start_time
            success = True
            if isinstance(result, dict):
                if "ok" in result:
                    success = bool(result.get("ok"))
                elif "error" in result:
                    success = False

            # QUALITY MITIGATION: Process tool result with intelligent truncation
            raw_result_str = ""
            if success and isinstance(result, dict):
                if "result" in result:
                    raw_result_str = str(result["result"])
                elif "message" in result:
                    raw_result_str = str(result["message"])
            elif not success:
                raw_result_str = result.get("error", "Unknown error") if isinstance(result, dict) else str(result)

            # Apply quality-aware processing
            conversation_id = f"conv-{int(time.time())}"  # Use timestamp for now
            quality_tier = self._get_quality_tier_for_tool(tool_name, conversation_id)

            # Track processing time for quality metrics
            processing_start = time.time()
            processed_result, processing_metadata = await self.tool_result_processor.process_tool_result(
                tool_name=tool_name,
                raw_result=raw_result_str,
                quality_tier=quality_tier,
                force_full=self._should_force_full_result(tool_name, raw_result_str, conversation_state),
                conversation_context={"current_task": conversation_state.current_task}
            )
            processing_time = time.time() - processing_start

            # Record quality metrics
            self.quality_metrics_tracker.record_quality_event(
                tool_name=tool_name,
                processing_metadata=processing_metadata,
                original_length=len(raw_result_str),
                processed_length=len(processed_result),
                quality_tier=quality_tier.value,
                processing_time=processing_time
            )

            # Use processed result for conversation state
            result_summary = processed_result if success else f"Error: {processed_result}"

            # Log quality processing metrics
            logger.debug(f"Tool result processed: {tool_name} - {processing_metadata} ({processing_time:.3f}s)")

            conversation_state.record_tool_execution(
                tool_name=tool_name,
                success=success,
                result_summary=result_summary
            )

            # Record in global tool tracker
            tool_tracker.record_tool_execution(tool_name, success, execution_time)

            # Create tool result message (but don't add to growing message history)
            content = ""
            if success:
                if isinstance(result, dict) and "result" in result:
                    content = json.dumps(result["result"])
                else:
                    content = json.dumps(result)
            else:
                error_str = result.get("error", str(result)) if isinstance(result, dict) else str(result)
                content = json.dumps({"ok": False, "error": error_str})

            tool_message = {
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": content
            }

            # Add to essential messages for context (limited retention)
            conversation_state.add_essential_message(tool_message)

            logger.info(f"✅ Tool '{tool_name}' executed successfully in {execution_time:.2f}s (quality processed in {processing_time:.2f}s)")

            return processed_result, tool_message

        except Exception as e:
            execution_time = time.time() - tool_start_time
            error_msg = f"Tool execution failed: {str(e)}"

            # Record failure in both trackers
            conversation_state.record_tool_execution(
                tool_name=tool_name,
                success=False,
                error_message=error_msg
            )
            tool_tracker.record_tool_execution(tool_name, False, execution_time)

            logger.error(f"❌ Tool '{tool_name}' failed after {execution_time:.2f}s: {error_msg}")

            error_message_payload = {
                "role": "tool",
                "tool_call_id": tool_call.get("id", f"call_{tool_name}"),
                "name": tool_name,
                "content": f"Error: {error_msg}"
            }
            conversation_state.add_essential_message(error_message_payload)

            return f"Error: {error_msg}", error_message_payload

    def _get_quality_tier_for_tool(self, tool_name: str, conversation_id: str) -> 'QualityTier':
        """Determine quality tier for tool result processing"""
        from agent_runner.tool_result_processor import QualityTier

        # Check for temporary overrides
        if conversation_id in self.quality_overrides:
            override = self.quality_overrides[conversation_id]
            if override.get("expires", 0) > time.time():
                return QualityTier(override["tier"])
            else:
                # Override expired, remove it
                del self.quality_overrides[conversation_id]

        # Default quality tier (can be made configurable)
        return QualityTier.MEDIUM

    def _should_force_full_result(self, tool_name: str, result: str, conversation_state) -> bool:
        """Determine if tool result should be retained in full"""
        # Check for user-requested full results
        conversation_id = getattr(conversation_state, 'conversation_id', 'unknown')
        if conversation_id in self.quality_overrides:
            override = self.quality_overrides[conversation_id]
            if override.get("force_full", False) and override.get("expires", 0) > time.time():
                return True

        # Let the tool result processor decide based on its policies
        return False

    def handle_quality_command(self, command: str, conversation_id: str) -> Optional[str]:
        """Handle user quality control commands"""
        command = command.lower().strip()

        if "full result" in command or "full results" in command:
            self.quality_overrides[conversation_id] = {
                "tier": "max",
                "force_full": True,
                "expires": time.time() + 60,  # 1 minute
                "reason": "user_requested_full"
            }
            return "✅ Full result mode enabled for next request"

        elif "detailed mode" in command:
            self.quality_overrides[conversation_id] = {
                "tier": "high",
                "expires": time.time() + 300,  # 5 minutes
                "reason": "user_requested_detailed"
            }
            return "✅ Detailed mode enabled for next 5 minutes"

        elif "quality mode" in command or "high quality" in command:
            self.quality_overrides[conversation_id] = {
                "tier": "high",
                "expires": time.time() + 1800,  # 30 minutes
                "reason": "user_requested_quality"
            }
            return "✅ High quality mode enabled for next 30 minutes"

        elif "reset quality" in command or "normal mode" in command:
            if conversation_id in self.quality_overrides:
                del self.quality_overrides[conversation_id]
            return "✅ Quality settings reset to normal"

        return None

    def get_quality_metrics(self) -> Dict[str, Any]:
        """Get comprehensive quality processing metrics"""
        base_metrics = {}

        if hasattr(self, 'tool_result_processor'):
            base_metrics.update(self.tool_result_processor.get_quality_metrics())

        if hasattr(self, 'quality_metrics_tracker'):
            base_metrics["quality_tracking"] = self.quality_metrics_tracker.get_quality_report()

        return base_metrics

    def start_ab_test(self, test_name: str, variants: List[Dict[str, Any]]):
        """Start an A/B test for quality improvement strategies"""
        if hasattr(self, 'quality_metrics_tracker'):
            self.quality_metrics_tracker.start_ab_test(test_name, variants)
            logger.info(f"Started A/B test: {test_name}")

    def get_ab_test_results(self, test_name: str) -> Optional[Dict[str, Any]]:
        """Get results for an A/B test"""
        if hasattr(self, 'quality_metrics_tracker'):
            return self.quality_metrics_tracker.get_ab_test_results(test_name)
        return None

    def record_user_feedback(self, event_index: int, quality_score: int):
        """Record user feedback on quality processing"""
        if hasattr(self, 'quality_metrics_tracker'):
            self.quality_metrics_tracker.record_user_feedback(event_index, quality_score)
            logger.info(f"User feedback recorded: event {event_index}, score {quality_score}")

    async def _get_architecture_context(self) -> str:
        """Get architecture context facts in parallel-friendly format with caching."""
        try:
            # PHASE 4: Use memory cache for architecture facts (changes infrequently)
            arch_facts = await self.memory_cache.query_facts_cached(
                kb_id="system_architecture",
                query="",  # No specific query for architecture
                limit=50
            )
            if arch_facts:
                fact_lines = [f"- {f.entity} {f.relation} {f.target}" for f in arch_facts]
                return (
                    "\n### SELF-AWARENESS (Internal Architecture)\n"
                    "You are aware of your own internal components. Do not hallucinate external tools.\n"
                    + "\n".join(fact_lines) + "\n"
                )
        except Exception as e:
            logger.warning(f"Failed to hydrate architecture context: {e}")
        return ""

    async def _process_response_hallucinations(self, message: Dict[str, Any], active_model: str) -> bool:
        """
        Process hallucinations in model response and return whether to continue the loop.

        Returns True if we should continue the tool loop, False if we should break.
        """
        # Check for hallucinated tool calls in content
        if message.get("content"):
            content_str = extract_text_content(message["content"]).strip()
            if (content_str.startswith("{") and "name" in content_str and "parameters" in content_str) or \
               (content_str.startswith("[") and "name" in content_str):
                logger.warning(f"[TOOL_LOOP] ⚠️  DETECTED HALLUCINATED TOOL CALL IN CONTENT: {content_str}")

        # [VERIFICATION CHEAT CODE] - Hallucination Converter
        # Llama 3 often outputs raw text (hallucination) instead of JSON tool calls.
        # We detect the trigger in the TEXT content and force it into a Tool Call.
        if not message.get("tool_calls"):
            logger.info(f"[TOOL_LOOP] No structured tool_calls found, checking for hallucinations in content")

            # Check if the content contains tool call JSON
            content = extract_text_content(message.get("content", "")).strip()
            if content:
                # Try to parse the entire content as JSON first
                if content.startswith("{") and content.endswith("}"):
                    try:
                        parsed_content = json.loads(content)
                        if isinstance(parsed_content, dict) and "name" in parsed_content and "parameters" in parsed_content:
                            logger.warning(f"[TOOL_LOOP] DETECTED HALLUCINATED TOOL CALL JSON: {parsed_content}")

                            # Instead of converting to tool calls (which would cause another loop iteration),
                            # clean up the response and let the finalizer handle it
                            message["content"] = "[Tool call detected but not properly formatted. Please rephrase your request or use available tools.]"
                            logger.info(f"[TOOL_LOOP] CLEANED UP HALLUCINATED TOOL CALL CONTENT")
                            return False  # Don't continue - let finalizer handle it

                    except json.JSONDecodeError:
                        pass  # Not valid JSON, continue with other checks

                # Pattern 2: function_name(parameters) style
                import re
                func_match = re.search(r'(\w+)\s*\(\s*([^)]*)\s*\)', content)
                if func_match:
                    func_name = func_match.group(1)
                    func_args = func_match.group(2)
                    logger.warning(f"[TOOL_LOOP] DETECTED FUNCTION CALL PATTERN: {func_name}({func_args})")

                    # Convert to proper tool call format
                    hallucinated_tool_call = {
                        "id": f"hallucinated_{int(time.time()*1000)}",
                        "type": "function",
                        "function": {
                            "name": func_name,
                            "arguments": f'{{"args": "{func_args}"}}'
                        }
                    }

                    message["tool_calls"] = [hallucinated_tool_call]
                    message["content"] = content.replace(func_match.group(0), "").strip()
                    logger.info(f"[TOOL_LOOP] CONVERTED FUNCTION PATTERN TO TOOL CALL: {func_name}")
                    return True  # Continue with the converted tool call

        # [LATENCY OPTIMIZATION] Adaptive Logic: Skip Finalizer for Smart Models
        is_smart_model = self.state.is_high_tier_model(active_model)
        if is_smart_model:
            logger.info(f"⚡ Adaptive Logic: Skipping Finalizer for High-Tier Model ({active_model})")
            return False  # Don't continue - treat as final response

        # Check for Finalizer Handover (Only if NOT smart model)
        elif self.state.finalizer_enabled and self.state.finalizer_model and self.state.finalizer_model != active_model:
            # Circuit Breaker Check
            finalizer_model_id = self.state.finalizer_model
            is_cb_allowed = self.state.mcp_circuit_breaker.is_allowed(finalizer_model_id)

            if is_cb_allowed:
                logger.info(f"Finalizer Handover: {active_model} -> {finalizer_model_id}")
                return await self._handover_to_finalizer(message, messages, active_model, finalizer_model_id)

        return False  # Default: don't continue

    async def _handover_to_finalizer(self, message: Dict[str, Any], messages: List[Dict[str, Any]], active_model: str, finalizer_model_id: str) -> bool:
        """Handle handover to finalizer model. Returns True if should continue loop."""
        # Preserve Worker's draft in case both Finalizer and Fallback fail
        worker_draft = messages.pop() if messages else None

        try:
            # 1. Attempt Finalizer
            final_res = await self.call_gateway_with_tools(messages, finalizer_model_id, [])
            response = final_res
            message = response["choices"][0]["message"]
            messages.append(message)

            # Success: Record it
            self.state.mcp_circuit_breaker.record_success(finalizer_model_id)
            return False  # Don't continue - finalizer succeeded

        except Exception as e:
            logger.error(f"Finalizer execution failed: {e}")
            # Failure: Record it
            self.state.mcp_circuit_breaker.record_failure(finalizer_model_id)

            # 2. Attempt Fallback - restore worker draft and continue without finalizer
            await self._handle_fallback(messages, worker_draft)
            return False  # Don't continue - fallback handled

    async def _handle_fallback(self, messages: List[Dict[str, Any]], worker_draft: Optional[Dict[str, Any]]):
        """Handle fallback when finalizer fails - restore worker draft."""
        if worker_draft:
            messages.append(worker_draft)
            logger.info("Fallback: Restored worker draft after finalizer failure")

    async def agent_loop(self, user_messages: List[Dict[str, Any]], model: Optional[str] = None, tools: Optional[List[Dict[str, Any]]] = None, request_id: Optional[str] = None, skip_refinement: bool = False, quality_tier: Optional[Any] = None) -> Dict[str, Any]:
        logger.info(f"🔍 Agent loop started: {len(user_messages)} messages, model={model}, request_id={request_id}")

        # Lazy-initialize heavy subsystems on first use to ensure caches exist
        if not getattr(self, "_initialized", False):
            await self.async_initialize()

        # Apply quality tier override
        original_tier = self._apply_quality_tier_override(quality_tier)

        # Process slash commands
        user_messages, immediate_resp = await self._process_slash_commands(user_messages)
        if immediate_resp:
            logger.info("Slash Command Intercepted. Returning immediate response.")
            return {
                "id": f"slash-{int(time.time())}",
                "object": "chat.completion",
                "created": int(time.time()),
                "choices": [{
                    "index": 0,
                    "message": immediate_resp,
                    "finish_reason": "stop"
                }],
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            }

        # Create conversation ID for tracking (needed for quality commands)
        conversation_id = request_id or f"conv-{int(time.time())}"

        # QUALITY CONTROL: Check for user quality commands
        if user_messages and user_messages[-1].get("role") == "user":
            user_message = user_messages[-1].get("content", "")
            quality_response = self.handle_quality_command(user_message, conversation_id)
            if quality_response:
                logger.info(f"Quality command processed: {user_message}")
                return {
                    "id": f"quality-{int(time.time())}",
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "choices": [{
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": quality_response
                        },
                        "finish_reason": "stop"
                    }],
                    "usage": {"prompt_tokens": len(user_message.split()), "completion_tokens": len(quality_response.split()), "total_tokens": 0}
                }

        # PHASE 2: Initialize conversation state compression
        from agent_runner.conversation_state import ConversationState, TaskStatus
        from agent_runner.tool_state_tracker import ToolStateTracker

        # Initialize compressed conversation state
        conversation_state = ConversationState(conversation_id=conversation_id)

        # Initialize tool state tracker (shared across conversations)
        if not hasattr(self, 'tool_state_tracker'):
            self.tool_state_tracker = ToolStateTracker()
        tool_tracker = self.tool_state_tracker

        # Extract initial task from user query
        if user_messages:
            last_user_msg = user_messages[-1].get("content", "")
            conversation_state.update_task(f"Processing: {last_user_msg[:50]}...")
            conversation_state.add_essential_message(user_messages[-1])  # Keep the initial query

        # Context management: pruning, model selection, message construction
        user_messages = self._prepare_conversation_context(user_messages)
        active_model = self._select_active_model(model)

        # PHASE 3: Intelligent conversation caching for performance gains
        cache_key = f"conv_{conversation_id}_prompt_{len(user_messages)}"

        # Defensive init in case async_initialize hasn't run yet
        if not hasattr(self, "_conversation_cache"):
            self._conversation_cache = {}
            self._conversation_cache_size = 10

        if cache_key in self._conversation_cache:
            # PHASE 3 CACHE HIT: Reuse cached prompt construction
            messages, cached_static_prompt, hit_count = self._conversation_cache[cache_key]
            self._conversation_cache[cache_key] = (messages, cached_static_prompt, hit_count + 1)

            # Log performance gain
            token_estimate = sum(len(str(m.get("content", ""))) for m in messages) // 4
            logger.info(f"PHASE 3: 💾 Cache hit for {conversation_id} (hit #{hit_count + 1}, ~{token_estimate} tokens saved)")

        else:
            # PHASE 3 CACHE MISS: Construct and cache messages
            messages, cached_static_prompt = await self._construct_message_sequence_compressed(
                user_messages, conversation_state, skip_refinement
            )

            # Add to cache with hit counter
            self._conversation_cache[cache_key] = (messages.copy(), cached_static_prompt, 0)

            # Maintain cache size limit (LRU eviction)
            if len(self._conversation_cache) > self._conversation_cache_size:
                # Remove oldest entry (lowest hit count, or random if tie)
                oldest_key = min(self._conversation_cache.keys(),
                               key=lambda k: self._conversation_cache[k][2])
                del self._conversation_cache[oldest_key]
                logger.debug(f"PHASE 3: Cache eviction - removed {oldest_key}")

            token_estimate = sum(len(str(m.get("content", ""))) for m in messages) // 4
            logger.info(f"PHASE 3: 📝 Cache miss - constructed and cached prompt (~{token_estimate} tokens) for {conversation_id}")

        steps = 0
        force_exit_after_tools = False  # Hybrid: break after first tool round to hand off to finalizer
        active_tools = await self._prepare_tools_for_model(tools, user_messages)

        # Track loop intelligence for smart exits
        consecutive_no_tools = 0
        recent_responses = []
        loop_start_time = time.time()

        while steps < self.state.max_tool_steps:
            steps += 1
            logger.info(f"[TOOL_LOOP] Step {steps}/{self.state.max_tool_steps}: Calling {active_model} with {len(active_tools)} tools")
            logger.info(f"[TOOL_LOOP] Active tools: {[t['function']['name'] for t in active_tools]}")

            loop_start = time.time()
            # Use cached messages from Phase 3 conversation-level caching
            try:
                response = await self.call_gateway_with_tools(messages, active_model, active_tools)
                loop_duration = time.time() - loop_start

                # Validate response structure
                if not response or "choices" not in response or not response["choices"]:
                    raise ValueError("Invalid response structure from model")

            except Exception as e:
                logger.error(f"[TOOL_LOOP] Model call failed: {e}")
                # Fallback: Try calling without tools (direct model response)
                try:
                    logger.info(f"[TOOL_LOOP] Attempting fallback without tools")
                    response = await self.call_gateway_with_tools(messages, active_model, [])
                    loop_duration = time.time() - loop_start
                except Exception as fallback_e:
                    logger.error(f"[TOOL_LOOP] Fallback also failed: {fallback_e}")
                    # Final fallback: Create a basic error response
                    response = {
                        "choices": [{
                            "message": {
                                "role": "assistant",
                                "content": f"I apologize, but I'm currently unable to process this request due to a technical issue. Please try again later or rephrase your question."
                            },
                            "finish_reason": "stop"
                        }],
                        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
                    }
                    loop_duration = time.time() - loop_start

            # Alert on slow operations
            if loop_duration > 5.0:
                from common.logging_utils import log_structured
                log_structured("performance_alert",
                              operation=f"tool_loop_step_{steps}",
                              duration=loop_duration,
                              threshold=5.0,
                              action="Check model load, network latency, or tool complexity",
                              model=active_model,
                              tools=len(active_tools))

            choice = response["choices"][0]
            message = choice["message"]

            logger.info(f"[TOOL_LOOP] Raw response message: role={message.get('role')}, content_length={len(message.get('content', ''))}, tool_calls={len(message.get('tool_calls', []))}")

            # Log content preview and check for hallucinations
            if message.get("content"):
                content_preview = message["content"][:200] + "..." if len(message["content"]) > 200 else message["content"]
                logger.info(f"[TOOL_LOOP] Content preview: {content_preview}")

            if message.get("tool_calls"):
                logger.info(f"[TOOL_LOOP] Structured tool calls found: {len(message['tool_calls'])}")
                for tc in message["tool_calls"]:
                    logger.info(f"[TOOL_LOOP] Tool call: {tc['function']['name']} with args: {tc['function']['arguments']}")

            # PHASE 2: Track conversation state instead of growing message history
            conversation_state.add_essential_message(message)  # Keep essential AI responses

            # Process tool calls if present and capture messages to feed back to the model
            if message.get("tool_calls"):
                tool_messages = await self._process_tool_calls_with_state_tracking(
                    message["tool_calls"], conversation_state, tool_tracker, request_id
                )
                # Preserve the assistant's tool_call message and the tool results for the next round
                messages.append(message)
                messages.extend(tool_messages)
                if tool_messages:
                    force_exit_after_tools = True  # Avoid multiple full-model passes; finalizer will handle synthesis
                consecutive_no_tools = 0  # Reset counter when tools are used
            else:
                # Keep the assistant reply in the running context even when no tools are used
                messages.append(message)
                consecutive_no_tools += 1  # Increment when no tools used

            # Track recent responses for stability detection
            recent_responses.append(message.get("content", ""))
            if len(recent_responses) > 3:
                recent_responses.pop(0)

            # 🎯 PHASE 1: INTELLIGENT LOOP EXIT CONDITIONS
            logger.info(f"🎯 Checking exit conditions: step={steps}, no_tools={consecutive_no_tools}, responses={len(recent_responses)}")

            # 1. No-Tool Usage Exit (exit after 2+ iterations with no tools)
            if consecutive_no_tools >= 2 and steps >= 2:
                logger.info(f"🎯 SMART EXIT: No tools used in {consecutive_no_tools} consecutive iterations")
                break

            # 2. Response Stability Exit (exit when responses become similar)
            if len(recent_responses) >= 3 and steps >= 3:
                similarity = self._calculate_response_similarity(recent_responses)
                logger.info(f"🎯 Similarity check: {similarity:.2f} for {len(recent_responses)} responses")
                if similarity > 0.8:  # High similarity indicates stabilization
                    logger.info(f"🎯 SMART EXIT: Response stabilized (similarity: {similarity:.2f})")
                    break

            # 3. Completion Signal Exit (exit when LLM indicates completion)
            if self._response_indicates_completion(message):
                logger.info("🎯 SMART EXIT: Response indicates query completion")
                break

            # 4. Performance Timeout Exit (emergency exit for very slow queries)
            total_loop_time = time.time() - loop_start_time
            if total_loop_time > 30 and steps >= 3:  # 30 seconds total, minimum 3 steps
                logger.warning(f"🎯 TIMEOUT EXIT: Loop running too long ({total_loop_time:.1f}s), forcing exit")
                break

            # PHASE 4: Log exit decision metrics for optimization
            if steps % 5 == 0 or consecutive_no_tools > 0:  # Periodic logging
                logger.info(f"🔄 Loop Status: Step {steps}, No-tools: {consecutive_no_tools}, "
                          f"Responses: {len(recent_responses)}, Time: {total_loop_time:.1f}s")

            # Process hallucinations and determine if we should continue
            should_continue = await self._process_response_hallucinations(message, active_model)
            if should_continue:
                continue

            # Hybrid exit: once tools have run, break to hand off to finalizer (or return) without extra model passes
            if force_exit_after_tools:
                break

                
                # Store episode before returning final answer
                if request_id:
                    try:
                        logger.info(f"Storing request {request_id} with {len(messages)} messages")
                        # Sanitize messages to simple JSON types (Dicts) explicitly
                        safe_messages = json.loads(json.dumps(messages, default=str))
                        # PHASE 4: Cache episode retrieval for future queries
                        await self.memory_client.store_episode(request_id, safe_messages)
                        # Invalidate cache for this request to ensure fresh data on next retrieval
                        self.memory_cache.invalidate_by_request(request_id)
                    except Exception as e:
                        logger.warning(f"Failed to store episode for request {request_id}: {e}")

                # ===== PHASE 5: LOOP COMPLETION ANALYSIS =====
        # Log final loop statistics for optimization
        total_loop_time = time.time() - loop_start_time
        logger.info(f"🎯 LOOP COMPLETE: {steps} iterations in {total_loop_time:.2f}s "
                  f"(avg: {total_loop_time/steps:.2f}s per iteration)")

        # ===== HALLUCINATION DETECTION =====
        # Analyze the final response for hallucinations before returning
        try:
            logger.info("HALLUCINATION_CHECK: Starting detection on final response")
            final_message = response["choices"][0]["message"]

            # If the model returned an empty message, fall back to the last non-empty assistant/tool reply
            if not final_message.get("content"):
                fallback_content = None
                for prior_msg in reversed(messages):
                    if prior_msg.get("role") == "assistant" and prior_msg.get("content"):
                        fallback_content = prior_msg.get("content")
                        break
                    if not fallback_content and prior_msg.get("role") == "tool" and prior_msg.get("content"):
                        fallback_content = prior_msg.get("content")
                if fallback_content:
                    final_message["content"] = fallback_content
                    response["choices"][0]["message"] = final_message
                    logger.warning("Final response was empty; reused prior message content to avoid blank reply")

            response_text = final_message.get("content", "")

            if response_text:  # Only check non-empty responses
                detection_context = {
                    "response": response_text,
                    "user_query": user_messages[-1].get("content", "") if user_messages else None,
                    "conversation_history": user_messages[:-1] if len(user_messages) > 1 else [],
                    "model_info": {"model": active_model}
                }

                detection_result = await self.hallucination_detector.detect_hallucinations(**detection_context)
                logger.info(f"HALLUCINATION_CHECK: Detection completed - is_hallucination: {detection_result.is_hallucination}, confidence: {detection_result.confidence:.2f}")

                # Log detection results (warn-only to avoid response format changes)
                if detection_result.is_hallucination:
                    logger.warning(f"HALLUCINATION DETECTED in response: severity={detection_result.severity.value}, confidence={detection_result.confidence:.2f}")

                    # For high-confidence hallucinations, add warning to the response content
                    if detection_result.confidence > 0.8 and detection_result.severity in [HallucinationSeverity.HIGH, HallucinationSeverity.CRITICAL]:
                        warning_msg = "\n\n⚠️ **Content Warning**: This response may contain inaccuracies. Please verify critical information independently."
                        final_message["content"] = response_text + warning_msg
                elif logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"Hallucination check passed: confidence={detection_result.confidence:.2f}")

        except Exception as e:
            logger.warning(f"Hallucination detection failed: {e}")
            # Continue with normal response - don't block due to detection failure

        # DEBUG: Log that we're about to return response
        logger.warning(f"AGENT_LOOP: About to return response with content length: {len(response.get('choices', [{}])[0].get('message', {}).get('content', ''))}")
        # [FEATURE-9] TELEMETRY: Log Selection Precision
        # We track how efficient the tool selection was.
        if message.get("tool_calls"):
            used_count = len(message["tool_calls"])
            provided_count = len(active_tools)
            precision = used_count / provided_count if provided_count > 0 else 0

            track_event(
                event="tool_selection_quality",
                message=f"Selection Precision: {precision:.2f} ({used_count}/{provided_count})",
                severity=EventSeverity.INFO,
                category=EventCategory.PERFORMANCE,
                component="engine",
                metadata={
                    "provided_tools": provided_count,
                    "used_tools": used_count,
                    "precision": precision,
                    "request_id": request_id,
                    "model": active_model
                }
            )

        return response

    async def call_gateway_streaming(self, messages: List[Dict[str, Any]], model: Optional[str] = None, tools: Optional[List[Dict[str, Any]]] = None):
        """Yields SSE events from the Model Gateway."""
        target_model = model or self.state.agent_model

        # Offline Fallback
        if not self.state.internet_available:
            is_safe_local = self.state.is_local_model(target_model)
            if not is_safe_local:
                target_model = self.state.fallback_model or DEFAULT_FALLBACK_MODEL

        # Prepare candidates (Primary + Fallback)
        candidates = [target_model]
        fallback = self.state.fallback_model or DEFAULT_FALLBACK_MODEL
        if self.state.fallback_enabled and fallback not in candidates:
            candidates.append(fallback)

        headers = {}
        if self.state.router_auth_token:
            headers["Authorization"] = f"Bearer {self.state.router_auth_token}"

        client = await self.state.get_http_client()
        url = f"{self.state.gateway_base}/v1/chat/completions"

        last_error = None
        for attempt_model in candidates:
            # Smart Routing Resolution
            url, final_model = self._resolve_model_endpoint(attempt_model)

            if not self.state.mcp_circuit_breaker.is_allowed(attempt_model):
                continue

            active_tools = tools or self.executor.tool_definitions
            payload = {
                "model": final_model,
                "messages": messages,
                "tools": active_tools,
                "tool_choice": "auto",
                "stream": True,
                "stream_options": {"include_usage": True}, # Request precise billing data
                "logprobs": True, # Request confidence data
                "top_logprobs": 1
            }

            # [Optimization] Inject Context Window Limit
            # Default to 32768 to match Resident Model Policy (Formula 1)
            target_ctx = int(os.getenv("OLLAMA_NUM_CTX", "32768"))
            if "options" not in payload:
                payload["options"] = {"num_ctx": target_ctx}
            elif "num_ctx" not in payload["options"]:
                payload["options"]["num_ctx"] = target_ctx

            try:
                # Metrics Capture
                t0_stream = time.time()
                t_first = None
                token_count = 0

                # Verified Response Fields
                exact_usage = None
                finish_reason = None
                provider_req_id = None

                # Confidence Calculation
                total_prob = 0.0
                confidence_count = 0

                # Streaming Call
                async with client.stream("POST", url, json=payload, headers=headers, timeout=self.state.http_timeout) as response:
                    response.raise_for_status()
                    provider_req_id = response.headers.get("x-request-id", "")

                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)

                                # 1. Capture Usage (if present)
                                if "usage" in data and data["usage"]:
                                    exact_usage = data["usage"]

                                # 2. Capture Content & Finish Reason
                                if "choices" in data and len(data["choices"]) > 0:
                                    choice = data["choices"][0]
                                    delta = choice.get("delta", {})

                                    # TTFT Check
                                    if delta.get("content") and t_first is None:
                                        t_first = time.time()
                                        first_latency = (t_first - t0_stream) * 1000
                                        logger.info(f"PERF: ⚡ STREAM INITIALIZED. TTFT: {first_latency:.2f}ms")
                                    if delta.get("content"):
                                        token_count += 1

                                    if choice.get("finish_reason"):
                                        finish_reason = choice.get("finish_reason")

                                    # 3. Capture Logprobs (Confidence)
                                    # OpenAI/Grok format: choices[0].logprobs.content[].logprob
                                    if choice.get("logprobs") and choice["logprobs"].get("content"):
                                        # Note: In streaming, 'content' might be a list of 1 item corresponding to the delta
                                        # But usually logprobs come with the token.
                                        # Check format: 'logprobs': {'content': [{'token': 'The', 'logprob': -0.001, ...}]}
                                        content_probs = choice["logprobs"].get("content", [])
                                        for cp in content_probs:
                                            if "logprob" in cp:
                                                # Convert log-prob to linear prob: e^logprob
                                                # -0.001 -> 0.999
                                                try:
                                                    prob = math.exp(cp["logprob"])
                                                    total_prob += prob
                                                    confidence_count += 1
                                                except: pass # overflow/math error

                                yield data
                            except Exception:
                                pass

                # If we finished the stream successfully
                duration = time.time() - t0_stream
                ttft_ms = ((t_first - t0_stream) * 1000) if t_first else 0.0
                tps = token_count / max(0.1, duration)

                # Calculate Confidence
                avg_confidence = (total_prob / confidence_count) if confidence_count > 0 else 0.0

                # Prepare Metadata
                meta = {
                    "model": attempt_model,
                    "ttft_ms": int(ttft_ms),
                    "tps": round(tps, 2),
                    "duration_sec": round(duration, 2),
                    "finish_reason": finish_reason,
                    "provider_req_id": provider_req_id,
                    "estimated_tokens": token_count,
                    "confidence_score": round(avg_confidence, 4)
                }

                if exact_usage:
                    meta["usage"] = exact_usage
                    # Update billing accuracy
                    meta["billing_tokens"] = exact_usage.get("total_tokens", 0)

                # --- FINANCIAL ACCOUNTING ---
                try:
                    tracker = get_budget_tracker()
                    # Determine tokens for billing
                    p_tok = exact_usage.get("prompt_tokens", 0) if exact_usage else 0
                    c_tok = exact_usage.get("completion_tokens", token_count) if exact_usage else token_count

                    # If we didn't get usage (e.g. local), we implicitly don't charge (rate=0), OR we estimate if it's a paid model that failed to send usage.
                    # But estimate_cost handles known models.
                    if p_tok == 0 and not exact_usage:
                         # Rough estimate for prompt if missing
                         p_tok = len(json.dumps(messages)) // 4

                    cost = tracker.estimate_cost(attempt_model, p_tok, c_tok)
                    if cost > 0:
                        tracker.record_usage("agent_runner", cost)
                        meta["cost_usd"] = round(cost, 6)
                except Exception as budget_e:
                    logger.warning(f"Failed to record budget cost: {budget_e}")

                track_event(
                    "stream_completed",
                    category=EventCategory.PERFORMANCE,
                    severity=EventSeverity.INFO,
                    message=f"Stream OK ({len(json.dumps(meta))}b meta)",
                    metadata=meta
                )

                self.state.mcp_circuit_breaker.record_success(attempt_model)
                return

            except Exception as e:
                if "429" in str(e):
                     notify_critical(
                        title="Stream Rejection",
                        message=f"Model '{attempt_model}' stream rejected (429). Likely Budget Limit.",
                        source="AgentEngine"
                    )
                logger.error(f"Streaming failed for '{attempt_model}': {e}")
                self.state.mcp_circuit_breaker.record_failure(attempt_model)
                last_error = e
                # Loop to next candidate

            if last_error:
                raise HTTPException(status_code=500, detail=f"All streaming models failed. Last error: {last_error}")
        raise HTTPException(status_code=500, detail="All streaming models failed.")

    async def agent_stream(self, user_messages: List[Dict[str, Any]], model: Optional[str] = None, request_id: Optional[str] = None, skip_refinement: bool = False):
        """
        Generator that manages the Agent Loop and yields real-time events.
        Events:
        - {"type": "token", "content": "..."}
        - {"type": "tool_start", "tool": "name", "input": {...}}
        - {"type": "tool_end", "tool": "name", "output": "..."}
        - {"type": "error", "error": "..."}
        - {"type": "done", "usage": ...}
        """
        # Context Pruning
        PRUNE_LIMIT = 20
        if len(user_messages) > PRUNE_LIMIT:
            user_messages = user_messages[-PRUNE_LIMIT:]
            # Ensure valid start role
            while user_messages and user_messages[0].get("role") == "tool":
                user_messages.pop(0)

        # Context Injection (only for non-conversational queries)
        system_prompt = await self.get_system_prompt(user_messages, skip_refinement=skip_refinement)
        messages = [{"role": "system", "content": system_prompt}] + user_messages
        active_tools = await self.get_all_tools(user_messages)

        steps = 0
        while steps < self.state.max_tool_steps:
            steps += 1

            # --- Stream Consumption State ---
            current_tool_calls = [] # List of {index, id, function: {name, arguments}}
            current_content = ""
            content_emitted = False

            # 1. Call Gateway (Streaming)
            has_started_thinking = False
            try:
                async for chunk in self.call_gateway_streaming(messages, model, active_tools):
                    if not chunk.get("choices") or len(chunk["choices"]) == 0:
                        continue

                    delta = chunk["choices"][0].get("delta", {})

                    if STREAM_DEBUG_ENABLED:
                        logger.info(
                            f"[STREAM_DEBUG] delta_keys={list(delta.keys())} "
                            f"content_preview={_redact_preview(delta.get('content'))}"
                        )

                    # A. Content Token
                    if "content" in delta and delta["content"]:
                        token = delta["content"]
                        current_content += token
                        content_emitted = True
                        yield {"type": "token", "content": token}

                    # B. Tool Calls (Accumulation)
                    if "tool_calls" in delta and delta["tool_calls"]:
                        # Emit one-time thinking start signal
                        if not has_started_thinking:
                            yield {"type": "thinking_start", "count": 1}
                            has_started_thinking = True

                        for tc_chunk in delta["tool_calls"]:
                            idx = tc_chunk.get("index") # usually 0 or int
                            if idx is None:
                                idx = 0 # Safety for some providers

                            # Expand list if needed
                            while len(current_tool_calls) <= idx:
                                current_tool_calls.append({"index": len(current_tool_calls), "id": "", "function": {"name": "", "arguments": ""}})

                            target = current_tool_calls[idx]
                            if tc_chunk.get("id"):
                                target["id"] += tc_chunk["id"]

                            fn = tc_chunk.get("function", {})
                            if fn.get("name"):
                                target["function"]["name"] += fn["name"]
                            if fn.get("arguments"):
                                target["function"]["arguments"] += fn["arguments"]

                # 2. Process Accumulation
                # If we had tool calls, we need to handle them.
                # But first, append ANY content we received to history as the assistant message.
                assistant_msg = {"role": "assistant", "content": current_content}

                # [HALLUCINATION FIX]
                # Llama 3.1 (8B) often streams raw JSON text instead of using the tool_calls API.
                # We catch this pattern and convert it into a valid tool call execution.
                if not current_tool_calls and current_content.strip():
                    stripped = current_content.strip()
                    # Check for characteristic JSON signatures (allow generic text prefix)
                    json_start = stripped.find("{")
                    list_start = stripped.find("[")
                    candidate = None
                    if json_start != -1 and (list_start == -1 or json_start < list_start):
                        candidate = stripped[json_start:]
                    elif list_start != -1:
                        candidate = stripped[list_start:]

                    if candidate and '"name"' in candidate:
                        try:
                            # Attempt to clean potential markdown
                            cleaned = candidate
                            if cleaned.startswith("```"):
                                cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned
                            if cleaned.endswith("```"):
                                cleaned = cleaned.rsplit("\n", 1)[0]
                            cleaned = cleaned.strip("`").strip()
                            if cleaned.startswith("json"):
                                cleaned = cleaned[4:].strip()

                            data = json.loads(cleaned)
                            if isinstance(data, dict): data = [data]
                            parsed_calls = []
                            for item in data:
                                if isinstance(item, dict) and "name" in item:
                                     # [PATCH] Fuzzy Name Matching for Llama 3.1
                                     t_name = item["name"]
                                     if t_name == "get_time": t_name = "get_current_time"

                                     # Normalize arguments
                                     args = item.get("parameters", item.get("arguments", {}))
                                     if isinstance(args, str):
                                         try:
                                             args = json.loads(args)
                                         except:
                                             pass # Keep as string if parsing fails, let executor handle it

                                     parsed_calls.append({
                                        "index": len(parsed_calls),
                                        "id": f"call_h_{int(time.time())}_{len(parsed_calls)}",
                                        "function": {
                                            "name": t_name,
                                            "arguments": json.dumps(args) if isinstance(args, dict) else str(args)
                                        }
                                     })

                            if parsed_calls:
                                logger.warning(f"HALLUCINATION CONVERTED: Transformed raw text into {len(parsed_calls)} tool calls")
                                current_tool_calls = parsed_calls
                                # Note: We already yielded the text tokens, so the user sees the JSON.
                                # This is acceptable; we just ensure the ACTION happens.
                        except Exception as e:
                            logger.debug(f"Hallucination check failed (not valid JSON): {e}")

                if current_tool_calls:
                    # Reconstruct tool_calls array for the message history
                    tool_calls_payload = []
                    for tc in current_tool_calls:
                        tool_calls_payload.append({
                            "id": tc["id"],
                            "type": "function",
                            "function": {
                                "name": tc["function"]["name"],
                                "arguments": tc["function"]["arguments"]
                            }
                        })

                    assistant_msg["tool_calls"] = tool_calls_payload
                    messages.append(assistant_msg)

                    # Notify UI of upcoming tools
                    yield {"type": "thinking_start", "count": len(tool_calls_payload)}

                    # Execute Tools (Parallel)
                    tasks = [self.execute_tool_call(tc, request_id=request_id) for tc in tool_calls_payload]

                    # Yield "Running" events (optional, but good for UI to know distinct tools started)
                    for tc in tool_calls_payload:
                        yield {"type": "tool_start", "tool": tc["function"]["name"], "input": tc["function"]["arguments"]}

                    results = await asyncio.gather(*tasks, return_exceptions=True)

                    # Process Results
                    for i, result in enumerate(results):
                        tc = tool_calls_payload[i]
                        output_str = ""

                        if isinstance(result, BaseException):
                            output_str = json.dumps({"ok": False, "error": str(result)})
                        elif isinstance(result, dict):
                             # If it's a direct dictionary (from tool impl)
                             # We try to be helpful and dump the 'result' or whole dict
                             val = result.get("result", result.get("error", result))
                             output_str = json.dumps(val)
                        else:
                            output_str = str(result)

                        messages.append({
                            "tool_call_id": tc["id"],
                            "role": "tool",
                            "name": tc["function"]["name"],
                            "content": output_str
                        })

                        yield {"type": "tool_end", "tool": tc["function"]["name"], "output": output_str}

                        # Loop continues to next step (Model observes tool output)

                else:
                    # No tool calls -> This was the final answer.
                    # If the model produced no content, emit a minimal fallback so the stream is not blank.
                    if not content_emitted and not current_content.strip():
                        fallback_content = "How can I help?"
                        current_content = fallback_content
                        content_emitted = True
                        yield {"type": "token", "content": fallback_content}

                    # Append to history and break.
                    assistant_msg["content"] = current_content
                    messages.append(assistant_msg)

                    # [PHASE 42] Async Memory Storage (Fire and Forget)
                    yield {"type": "done"}

                    # [MEMORY] Store Episode in Memory Server (Async/Non-blocking)
                    if hasattr(self, "memory") and self.memory:
                        logger.info(f"DEBUG: Triggering async store_episode for {request_id}")
                        # We use create_task to fire and forget
                        asyncio.create_task(self.memory.store_episode(request_id, messages))
                    else:
                        logger.warning("DEBUG: Memory server not available in engine")

                    break

            except Exception as e:
                logger.error(f"Streaming error in agent_stream: {e}")
                yield {"type": "error", "error": f"Streaming failed: {e}", "request_id": request_id}
                break

    def _calculate_response_similarity(self, responses: List[str]) -> float:
        """PHASE 3: Advanced response stability detection"""
        if len(responses) < 2:
            return 0.0

        # Enhanced similarity metrics
        scores = []

        # 1. Length similarity (normalized)
        lengths = [len(r.split()) for r in responses]
        max_length = max(lengths)
        min_length = min(lengths)
        if max_length > 0:
            length_similarity = 1 - (max_length - min_length) / max_length
            scores.append(length_similarity)

        # 2. Word overlap similarity
        word_sets = [set(r.lower().split()) for r in responses]
        if word_sets:
            common_words = set.intersection(*word_sets)
            total_words = set.union(*word_sets)
            if total_words:
                word_overlap = len(common_words) / len(total_words)
                scores.append(word_overlap)

        # 3. Structural similarity (sentence count, punctuation)
        sentence_counts = [len(re.split(r'[.!?]+', r)) for r in responses]
        if sentence_counts:
            max_sentences = max(sentence_counts)
            min_sentences = min(sentence_counts)
            if max_sentences > 0:
                sentence_similarity = 1 - (max_sentences - min_sentences) / max_sentences
                scores.append(sentence_similarity * 0.5)  # Weight lower

        # 4. Ending pattern similarity (conversational vs informational)
        endings = []
        for r in responses:
            r = r.strip()
            if r.endswith(('?', '.', '!')):
                endings.append(r[-1])
            else:
                endings.append('other')

        if len(set(endings)) == 1:  # All responses end the same way
            scores.append(0.8)  # High similarity for consistent endings

        # Return average of all similarity scores
        return sum(scores) / len(scores) if scores else 0.0

    def _response_indicates_completion(self, message: Dict[str, Any]) -> bool:
        """Check if response indicates the query is complete"""
        content = message.get("content", "").lower()

        completion_signals = [
            "i hope this helps",
            "let me know if",
            "is there anything else",
            "does this answer",
            "please let me know",
            "i've provided",
            "here's the information",
            "that's all",
            "i'm done",
        ]

        return any(signal in content for signal in completion_signals)
