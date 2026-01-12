import logging
import os
import time
import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple
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
from agent_runner.prompts import get_healer_prompt, get_base_system_instructions, get_service_alerts
from agent_runner.memory_server import MemoryServer
from agent_runner.nexus import Nexus
import math

logger = logging.getLogger("agent_runner")

class AgentEngine:
    def __init__(self, state: AgentState):
        self.state = state
        self.executor = ToolExecutor(state)
        self.memory = MemoryServer(state)
        self.nexus = Nexus(state, self)

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
        return await intent.classify_search_intent(query, self.state, self.executor.tool_menu_summary)

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
                logger.warning(f"Model '{attempt_model}' is circuit broken. Skipping.")
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
            # Default to 32768 to match Resident Model Policy (Formula 1)
            target_ctx = int(os.getenv("OLLAMA_NUM_CTX", "32768"))
            if "options" not in payload:
                payload["options"] = {"num_ctx": target_ctx}
            elif "num_ctx" not in payload["options"]:
                payload["options"]["num_ctx"] = target_ctx
            
            # [COST-AUDIT] Log estimated token usage (Low CPU estimation)
            try:
                # Basic string length heuristic is sufficient for logging
                est_msg_tok = sum(len(str(m)) for m in messages) // 4
                est_tool_tok = sum(len(str(t)) for t in (tools or self.executor.tool_definitions)) // 4
                logger.info(f"[COST-AUDIT] Model: {attempt_model} | Msgs: ~{est_msg_tok} toks | Tools: ~{est_tool_tok} toks | Total Est: ~{est_msg_tok + est_tool_tok}")
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
                
                logger.error(f"Model call failed for '{attempt_model}': {e}")
                self.state.mcp_circuit_breaker.record_failure(attempt_model)
                last_error = str(e)
                # Continue to next candidate (fallback)

        # If we get here, all candidates failed
        logger.error(f"All model attempts failed. Last error: {last_error}")
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

    async def get_system_prompt(self, user_messages: Optional[List[Dict[str, Any]]] = None, skip_refinement: bool = False) -> str:
        """Construct the dynamic system prompt with memory context and environmental awareness."""
        
        # JIT Load Registry if empty (Startup)
        if not hasattr(self, "registry_cache") or self.registry_cache is None:
            await self._load_registry_cache()
            
        memory_facts = ""
        memory_status_msg = ""
        if user_messages:
            try:
                # Use LLM to generate a context-aware search query
                # [PHASE 14] BYPASS: Skip expensive query refinement for local/periodic tasks
                if skip_refinement:
                    search_query = ""
                else:
                    search_query = await self._generate_search_query(user_messages)
                
                # [FEATURE-11] Context Rehydration (Startup Awareness)
                # We proactively load the "system_architecture" bank to ensure the agent knows itself.
                # We also list available banks to give the agent a "Map" of its mind.
                from agent_runner.tools.mcp import tool_mcp_proxy
                
                # 1. Fetch Architecture (Fast, cached ideally, but for now direct)
                arch_ctx = ""
                try:
                    t0_arch = time.time()
                    arch_res = await tool_mcp_proxy(self.state, "project-memory", "query_facts", {"kb_id": "system_architecture", "limit": 50}, bypass_circuit_breaker=True)
                    dur_arch = (time.time() - t0_arch) * 1000
                    logger.info(f"PERF: Architecture Hydration took {dur_arch:.2f}ms")

                    if arch_res.get("ok"):
                        # Facts come as a list of dicts directly from query_facts (unlike search which wraps in content)
                        # Wait, tool_mcp_proxy returns the raw tool result. 
                        # query_facts returns {"ok": True, "facts": [...]}
                        # Let's check the result structure carefully.
                        raw_res = arch_res.get("result", {})
                        if isinstance(raw_res, str): raw_res = json.loads(raw_res)
                        
                        arch_facts = raw_res.get("facts", [])
                        if arch_facts:
                            fact_lines = [f"- {f.get('entity')} {f.get('relation')} {f.get('target')}" for f in arch_facts]
                            arch_ctx = (
                                "\n### SELF-AWARENESS (Internal Architecture)\n"
                                "You are aware of your own internal components. Do not hallucinate external tools.\n"
                                + "\n".join(fact_lines) + "\n"
                            )
                except Exception as e:
                    logger.warning(f"Failed to hydrate architecture context: {e}")

                if search_query:
                    
                    t0_mem = time.time()
                    search_res = await tool_mcp_proxy(self.state, "project-memory", "semantic_search", {"query": search_query, "limit": 10}, bypass_circuit_breaker=True)
                    dur_mem = (time.time() - t0_mem) * 1000
                    logger.info(f"Memory Retrieval took {dur_mem:.2f}ms")

                    if search_res.get("ok"):
                        # Extract facts from MCP response format
                        # Stdio MCP servers return [TextContent(text='{...}')]
                        result_obj = search_res.get("result", {})
                        content_list = result_obj.get("content", []) if isinstance(result_obj, dict) else []
                        
                        facts_data = []
                        if content_list and content_list[0].get("type") == "text":
                            try:
                                # The MCP server returns a JSON-string in the text field
                                inner_res = json.loads(content_list[0].get("text", "{}"))
                                facts_data = inner_res.get("facts", [])
                            except (json.JSONDecodeError, TypeError):
                                facts_data = []
                        
                        if facts_data:
                            # Log retrieved facts for debugging
                            log_facts = [f"{f.get('entity')} {f.get('relation')} {f.get('target')}" for f in facts_data]
                            logger.info(f"Memory Hit: Found {len(facts_data)} facts: {log_facts}")
                            fact_strings = [f"- {s}" for s in log_facts]
                            memory_facts = (
                                "\n### BACKGROUND INFORMATION (Memory Context)\n"
                                "The following facts may or may not be relevant to the current conversation.\n"
                                "If a fact is useful for answering the specific question, incorporate it naturally.\n"
                                "If a fact is irrelevant, IGNORE it completely. Do not mention that you are ignoring it.\n\n"
                                + "\n".join(fact_strings)
                            )
                    else:
                        memory_status_msg = f"\nSYSTEM ALERT: Long-term memory retrieval failed (MCP Error: {search_res.get('error')}). You are operating with limited context."
            except Exception as e:
                logger.warning(f"Context injection failed during prompt construction: {e}")
                memory_status_msg = f"\nSYSTEM ALERT: Long-term memory retrieval failed (Exception: {str(e)}). Context injection skipped."

        # Build the base instructions based on internet availability
        current_time_str = time.strftime("%Y-%m-%d %H:%M:%S")

        # JIT Recovery: If system thinks it's offline, double-check one last time before giving up.
        # JIT Recovery: If system thinks it's offline, OR just as a sanity check before prompting
        # We always want correct state before generating prompts.
        # [REMOVED] JIT Internet Check
        # We now rely entirely on the background health_monitor to maintain state.internet_available.
        # This prevents blocking prompt generation on network latency and avoids "flapping" state.
            
        # Removed "Forced Internet" Hack (Phase 12 Cleanup)

        env_instructions = get_base_system_instructions(self.state.internet_available)

        # [MEMORY REGISTRY INJECTION]
        if hasattr(self, "registry_cache") and self.registry_cache:
            env_instructions += f"\n\n### PERMANENT MEMORY REGISTRY (Always Available)\n{self.registry_cache}\n"

        # Check for service outages via circuit breaker
        open_breakers = [name for name, b in self.state.mcp_circuit_breaker.get_status().items() if b["state"] == "open"]
        service_alerts = get_service_alerts(open_breakers, memory_status_msg)

        # Files Context: Surface recently uploaded files from Chatbox
        upload_dir = os.path.join(self.state.agent_fs_root, "uploads")
        files_info = ""
        if os.path.exists(upload_dir):
            try:
                files = [f for f in os.listdir(upload_dir) if not f.startswith('.')]
                if files:
                    # Sort by modification time
                    files.sort(key=lambda x: os.path.getmtime(os.path.join(upload_dir, x)), reverse=True)
                    file_summaries = []
                    for f in files[:10]:
                        if "_" in f:
                            try:
                                f_id, f_name = f.split("_", 1)
                                file_summaries.append(f"- {f_name} [ID: {f_id}]")
                            except ValueError:
                                file_summaries.append(f"- {f}")
                        else:
                            file_summaries.append(f"- {f}")
                    
                    if file_summaries:
                        files_info = (
                            "\n### UPLOADED FILES & KNOWLEDGE BASES (Deep Context):\n"
                            "The following files were uploaded and are ready for deep processing.\n"
                            "1. TO READ RAW TEXT: Use 'read_text(path=\"uploads/{ID}_{FILENAME}\")'.\n"
                            "2. TO SEARCH DEEP MEANING (RAG): Use 'search(query=\"...\")'. This checks facts AND files simultaneously.\n"
                            "\nRecent Uploads:\n"
                            + "\n".join(file_summaries)
                        )
            except Exception as e:
                logger.warning(f"Failed to list uploads for prompt: {e}")

        # Location Context
        location_str = "Unknown Location"
        if self.state.location and self.state.location.get("city") != "Unknown":
            loc = self.state.location
            # e.g. "New York, New York, US (Lat: 40.7, Lon: -74.0)"
            location_str = f"{loc.get('city')}, {loc.get('region')}, {loc.get('country')}"
            
        prompt = (
            "You are Antigravity, a powerful agentic AI assistant running inside the Orchestrator.\n"
            f"Current System Time: {current_time_str}\n"
            f"Current Location: {location_str}\n"
            f"Active Mode: {self.state.active_mode.upper()}  <-- ADAPT YOUR BEHAVIOR TO THIS MODE.\n"
            f"{env_instructions}\n"
            f"{service_alerts}\n"
            "You are a helpful, intelligent assistant. Engage naturally with the user.\n"
            "When you use a tool, weave the result or confirmation naturally into your answer. Avoid robotic 'I have done X' statements unless necessary for clarity. Be concise.\n"
            "Use the tools provided to you to be the most helpful assistant possible. Do not explain which tools you are using or mention anything about tools.\n"
            "IMPORTANT: Focus on the user's LATEST message. Do not maintain context from unrelated previous topics.\n"
            f"{'STYLE: Do NOT use ANY emojis in your response. Keep tone professional/dry.' if self.state.config.get('preferences', {}).get('suppress_emoji') else ''}\n"
            "MEMORY CONSTRAINT: You have access to retrieved memory/facts below. Do NOT mention them unless they are DIRECTLY relevant to answering the CURRENT question. Do not say 'Regarding X...' if the user didn't ask about X."
            f"{memory_facts}\n"
            f"{arch_ctx}"
            f"{files_info}\n"
            "\n### SHELL SAFETY PROTOCOL (Command Execution)\n"
            "You have full shell access (Developer Mode). This is a POWERFUL privilege.\n"
            "1. CONFINEMENT: Favor executing commands within the workspace ('state.agent_fs_root').\n"
            "2. DESTRUCTIVENESS: NEVER run destructive commands (rm -rf, mkfs) outside the workspace without explicit user confirmation.\n"
            "3. PURPOSE: Only generate commands necessary for the requested task. Do not explore the user's system idly.\n"
            "4. APPLESCRIPT: You MAY use 'osascript' if the user asks for macOS automation, but verify it is safe first.\n"
        )
        return prompt

    async def agent_loop(self, user_messages: List[Dict[str, Any]], model: Optional[str] = None, tools: Optional[List[Dict[str, Any]]] = None, request_id: Optional[str] = None, skip_refinement: bool = False, quality_tier: Optional[Any] = None) -> Dict[str, Any]:
        
        # [FEATURE] Quality Tier Override
        # If provided, temporarily override the state's quality tier for this request.
        original_tier = None
        if quality_tier and hasattr(self.state, "set_quality_tier"):
            try:
                # We assume quality_tier is an Enum or can be converted. 
                # Ideally, chat.py passes the Enum member.
                from agent_runner.quality_tiers import QualityTier
                if isinstance(quality_tier, str):
                    # Try to map string to Enum
                    tier_enum = QualityTier[quality_tier.upper()]
                else:
                    tier_enum = quality_tier
                
                original_tier = self.state.quality_tier
                self.state._request_quality_tier = tier_enum # Set request-scoped override
                # self.state.set_quality_tier(tier_enum) # System-wide change (avoid?)
                # Used _request_quality_tier property in state instead of global set
            except Exception as e:
                logger.warning(f"Failed to apply quality tier '{quality_tier}': {e}")
        
        # [PHASE 55] Slash Commands (Meta-Control)
        # Intercept local commands like /save or /clear before they hit the LLM
        try:
            from agent_runner.services.slash_commands import SlashCommandProcessor
            processor = SlashCommandProcessor(self.state)
            user_messages, immediate_resp = await processor.process_messages(user_messages)
            
            if immediate_resp:
                logger.info(f"Slash Command Intercepted. Returning immediate response.")
                # Return synthetic OpenAI-style response
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
        except ImportError:
            pass # Optional dependency
        except Exception as e:
            logger.warning(f"Slash command processing failed: {e}")

        # Context Pruning: Prevent "Choking" on long histories
        PRUNE_LIMIT = self.state.context_prune_limit or DEFAULT_CONTEXT_PRUNE_LIMIT
        if len(user_messages) > PRUNE_LIMIT:
            original_len = len(user_messages)
            user_messages = user_messages[-PRUNE_LIMIT:]
            
            # Sanity Check: Don't start with a 'tool' outcome as it violates OpenAI protocol
            # (A tool message must be preceded by a tool_call)
            while user_messages and user_messages[0].get("role") == "tool":
                user_messages.pop(0)
            
            logger.info(f"Context Pruned: {original_len} -> {len(user_messages)} messages")

        # Context Awareness: Adjust model if offline
        active_model = model or self.state.agent_model
        if not self.state.internet_available and active_model.startswith("openai:"):
            fallback = self.state.fallback_model or DEFAULT_FALLBACK_MODEL
            logger.warning(f"Internet offline: Diverting from Cloud model to Local Fallback ({fallback})")
            active_model = fallback

        # 1. Context Injection: Get dynamic prompt
        system_prompt = await self.get_system_prompt(user_messages, skip_refinement=skip_refinement)
        messages = [{"role": ROLE_SYSTEM, "content": system_prompt}] + user_messages
        steps = 0
        active_tools = tools or await self.get_all_tools(user_messages)
        
        # [SAFETY CLAMP]
        # 2. Limit excessive tools
        if len(active_tools) > self.state.max_tool_count:
             logger.warning(f"Tool Count {len(active_tools)} exceeds limit. Truncating to {self.state.max_tool_count}.")
             active_tools = active_tools[:self.state.max_tool_count]

        logger.info(f"DEBUG: Active Tools passed to Model: {[t['function']['name'] for t in active_tools]}")

        while steps < self.state.max_tool_steps:
            steps += 1
            response = await self.call_gateway_with_tools(messages, active_model, active_tools)
            choice = response["choices"][0]
            message = choice["message"]
            
            messages.append(message)
            
            # [VERIFICATION CHEAT CODE] - Hallucination Converter
            # Llama 3 often outputs raw text (hallucination) instead of JSON tool calls.
            # We detect the trigger in the TEXT content and force it into a Tool Call.
            if not message.get("tool_calls"):
                
                # [LATENCY OPTIMIZATION] Adaptive Logic: Skip Finalizer for Smart Models
                is_smart_model = self.state.is_high_tier_model(active_model)
                if is_smart_model:
                     logger.info(f"⚡ Adaptive Logic: Skipping Finalizer for High-Tier Model ({active_model})")
                
                # Check for Finalizer Handover (Only if NOT smart model)
                elif self.state.finalizer_enabled and self.state.finalizer_model and self.state.finalizer_model != active_model:
                    # Circuit Breaker Check
                    # We reuse the registry for model stability tracking
                    finalizer_model_id = self.state.finalizer_model
                    is_cb_allowed = self.state.mcp_circuit_breaker.is_allowed(finalizer_model_id)

                    if is_cb_allowed:
                        logger.info(f"Finalizer Handover: {active_model} -> {finalizer_model_id}")
                        
                        # Preserve Worker's draft in case both Finalizer and Fallback fail
                        worker_draft = messages.pop() if messages else None
                        
                        try:
                            # 1. Attempt Finalizer
                            final_res = await self.call_gateway_with_tools(messages, finalizer_model_id, active_tools)
                            response = final_res
                            message = response["choices"][0]["message"]
                            messages.append(message)
                            
                            # Success: Record it
                            self.state.mcp_circuit_breaker.record_success(finalizer_model_id)
                            
                        except Exception as e:
                            logger.error(f"Finalizer execution failed: {e}")
                            # Failure: Record it
                            self.state.mcp_circuit_breaker.record_failure(finalizer_model_id)
                            
                            # 2. Attempt Fallback (Logic centralized below)
                            await self._handle_fallback(messages, active_tools, worker_draft)

                
                # Store episode before returning final answer
                if request_id:
                    try:
                        logger.info(f"Storing request {request_id} with {len(messages)} messages")
                        from agent_runner.tools.mcp import tool_mcp_proxy
                        # Sanitize messages to simple JSON types (Dicts) explicitly
                        safe_messages = json.loads(json.dumps(messages, default=str))
                        await tool_mcp_proxy(self.state, "project-memory", "store_episode", {"request_id": request_id, "messages": safe_messages})
                    except Exception as e:
                        logger.warning(f"Failed to store episode for request {request_id}: {e}")

                return response
            
            # [FEATURE-9] TELEMETRY: Log Selection Precision
            # We track how efficient the Maître d' was.
            # Precision = (Tools Used / Tools Provided)
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
                        "provided_count": provided_count,
                        "used_count": used_count,
                        "precision": precision,
                        "intent": "feature_9_maitre_d"
                    }
                )
            

            
            # Helper for tool execution loop
            # Helper for tool execution loop
            if message.get("tool_calls"):
                logger.info(f"Executing {len(message['tool_calls'])} tool calls in PARALLEL")
                
                # Execute all tools concurrently
                tasks = [self.execute_tool_call(tc, request_id=request_id) for tc in message["tool_calls"]]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for i, result in enumerate(results):
                    tool_call = message["tool_calls"][i]
                    
                    # Handle crash inside tool execution wrapper
                    # Handle crash inside tool execution wrapper
                    if isinstance(result, BaseException) or (isinstance(result, dict) and result.get("error")):
                        # Error detected
                        error_str = str(result) if isinstance(result, BaseException) else result.get("error")
                        self.state.tool_consecutive_failures += 1
                        
                        # [ESCALATION PROTOCOL]
                        # VERIFICATION: Threshold lowered to 1
                        if self.state.tool_consecutive_failures >= 1:
                            logger.warning(f"Escalation Protocol Triggered! Failures: {self.state.tool_consecutive_failures}")
                            
                            # 1. Notify User (Real-time Toast via Nexus)
                            if not hasattr(self.state, 'system_event_queue'):
                                self.state.system_event_queue = asyncio.Queue()
                            
                            self.state.system_event_queue.put_nowait({
                                "event": {
                                    "type": "system_status",
                                    "content": "⚠️ Healer Escalation: Summoning QwQ...", 
                                    "severity": "warning"
                                },
                                "request_id": request_id,
                                "timestamp": time.time()
                            })
                            
                            logger.warning(f"Escalation Protocol Triggered! Failures: {self.state.tool_consecutive_failures}")
                            
                            # 2. Summon Healer (Cold Storage)
                            # We construct a prompt for the Healer
                            healer_prompt = get_healer_prompt(
                                tool_call['function']['name'],
                                str(tool_call['function']['arguments']),
                                error_str
                            )
                            
                            try:
                                # Call Healer with keep_alive=0 (UNLOAD AFTER USE)
                                logger.info("Calling HEALER (QwQ)... (Expect delay)")
                                start_time = time.time()
                                healer_res = await self.call_gateway_with_tools(
                                    healer_prompt, 
                                    self.state.healer_model, 
                                    active_tools,
                                    keep_alive=0 # Force Unload
                                ) 
                                # Healer returns a chat completion response
                                healer_msg = healer_res["choices"][0]["message"]
                                content = json.dumps({"ok": False, "error": f"Escalated to Healer. Healer says: {healer_msg['content']}", "healed": True})
                                
                                # Reset counter after intervention
                                self.state.tool_consecutive_failures = 0
                                logger.info(f"Healer finished in {time.time() - start_time:.2f}s")
                                
                            except Exception as h_err:
                                logger.error(f"Healer failed: {h_err}")
                                content = json.dumps({"ok": False, "error": f"Healer Failed: {str(h_err)} | Original: {error_str}"})
                        else:
                            # Standard Error Report
                            content = json.dumps({"ok": False, "error": error_str})
                            
                    elif isinstance(result, dict):
                        # Success
                        self.state.tool_consecutive_failures = 0
                        content = json.dumps(result.get("result", result.get("error")))
                    else:
                        # Success (other types)
                        self.state.tool_consecutive_failures = 0
                        content = json.dumps(result)
                        
                    messages.append({
                        "role": ROLE_TOOL,
                        "tool_call_id": tool_call["id"],
                        "content": content
                    })
        
        # 2. Episodic Logging: Store the thread for background consolidation (Max steps reached)
        if request_id:
             try:
                 logger.info(f"Storing request {request_id} with {len(messages)} messages")
                 from agent_runner.tools.mcp import tool_mcp_proxy
                 # Sanitize messages to simple JSON types (Dicts) explicitly
                 safe_messages = json.loads(json.dumps(messages, default=str))
                 await tool_mcp_proxy(self.state, "project-memory", "store_episode", {"request_id": request_id, "messages": safe_messages})
             except Exception as e:
                 logger.warning(f"Failed to store episode for request {request_id}: {e}")

        return {"error": "Max tool steps reached"}

    async def _handle_fallback(self, messages, active_tools, worker_draft):
        """Centralized fallback logic when primary/finalizer models fail."""
        if self.state.fallback_enabled and self.state.fallback_model:
            logger.info(f"Activating Fallback Engine: {self.state.fallback_model}")
            try:
                fallback_res = await self.call_gateway_with_tools(messages, self.state.fallback_model, active_tools)
                response = fallback_res
                message = response["choices"][0]["message"]
                message["content"] = f"{message.get('content', '')}\n\n[System: Generated by Fallback Engine]"
                messages.append(message)
            except Exception as fb_e:
                logger.error(f"Fallback Engine failed: {fb_e}")
                if worker_draft:
                    messages.append(worker_draft)
        else:
            # Fallback disabled, Revert
            logger.warning("Fallback disabled. Reverting to Worker response.")
            if worker_draft:
                messages.append(worker_draft)

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
                OBJ_MODEL: final_model,
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

        # Context Injection
        system_prompt = await self.get_system_prompt(user_messages, skip_refinement=skip_refinement)
        messages = [{"role": ROLE_SYSTEM, "content": system_prompt}] + user_messages
        active_tools = await self.get_all_tools(user_messages)
        
        steps = 0
        while steps < self.state.max_tool_steps:
            steps += 1
            
            # --- Stream Consumption State ---
            current_tool_calls = [] # List of {index, id, function: {name, arguments}}
            current_content = ""
            
            # 1. Call Gateway (Streaming)
            has_started_thinking = False
            async for chunk in self.call_gateway_streaming(messages, model, active_tools):
                if not chunk.get("choices"):
                    continue
                
                delta = chunk["choices"][0].get("delta", {})
                
                # A. Content Token
                if "content" in delta and delta["content"]:
                    token = delta["content"]
                    current_content += token
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
                # We already yielded tokens.
                # Append to history and break.
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
