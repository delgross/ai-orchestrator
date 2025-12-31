import logging
import os
import time
import json
import asyncio
from typing import Dict, List, Any, Optional
from fastapi import HTTPException

from agent_runner.state import AgentState
from common.constants import OBJ_MODEL, ROLE_SYSTEM, ROLE_TOOL
from common.unified_tracking import track_event, EventSeverity, EventCategory
import agent_runner.intent as intent
from agent_runner.executor import ToolExecutor

logger = logging.getLogger("agent_runner")

class AgentEngine:
    def __init__(self, state: AgentState):
        self.state = state
        self.executor = ToolExecutor(state)

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

    async def call_gateway_with_tools(self, messages: List[Dict[str, Any]], model: Optional[str] = None, tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        target_model = model or self.state.agent_model
        
        # Universal Offline Fallback Logic
        if not self.state.internet_available:
            # Check if target model is remote. 
            # We treat 'ollama:' and 'local:' as safe. Everything else (openai:, gpt-, claude-, etc.) is suspect.
            is_safe_local = target_model.startswith(("ollama:", "local:", "test:"))
            
            if not is_safe_local:
                fallback = self.state.fallback_model or "ollama:llama3.3:70b-instruct-q8_0"
                if target_model != fallback:
                    logger.warning(f"OFFLINE MODE: Intercepting remote model '{target_model}'. Switching to fallback '{fallback}'.")
                    target_model = fallback

        # Prepare candidates: [Requested Model, Fallback Model]
        # We try the requested model first. If it fails or is circuit-broken, we try the fallback.
        candidates = []
        if target_model:
            candidates.append(target_model)
        
        fallback = self.state.fallback_model or "ollama:llama3.3:70b-instruct-q8_0"
        if self.state.fallback_enabled and fallback not in candidates:
            candidates.append(fallback)
            
        last_error: Any = None
        
        headers = {}
        if self.state.router_auth_token:
            headers["Authorization"] = f"Bearer {self.state.router_auth_token}"

        client = await self.state.get_http_client()
        url = f"{self.state.gateway_base}/v1/chat/completions"

        for attempt_model in candidates:
            # 1. Circuit Breaker Check
            if not self.state.mcp_circuit_breaker.is_allowed(attempt_model):
                logger.warning(f"Model '{attempt_model}' is circuit broken. Skipping.")
                last_error = f"Model '{attempt_model}' is circuit broken"
                continue
                
            # 2. Prepare Payload
            active_tools = tools or self.executor.tool_definitions
            payload = {
                OBJ_MODEL: attempt_model,
                "messages": messages,
                "tools": active_tools,
                "tool_choice": "auto",
                "stream": False,
            }
            
            # [COST-AUDIT] Log estimated token usage (Low CPU estimation)
            try:
                # Basic string length heuristic is sufficient for logging
                est_msg_tok = sum(len(str(m)) for m in messages) // 4
                est_tool_tok = sum(len(str(t)) for t in (tools or self.executor.tool_definitions)) // 4
                logger.info(f"[COST-AUDIT] Model: {attempt_model} | Msgs: ~{est_msg_tok} toks | Tools: ~{est_tool_tok} toks | Total Est: ~{est_msg_tok + est_tool_tok}")
            except Exception:
                pass
            
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
                logger.error(f"Model call failed for '{attempt_model}': {e}")
                self.state.mcp_circuit_breaker.record_failure(attempt_model)
                last_error = str(e)
                # Continue to next candidate (fallback)

        # If we get here, all candidates failed
        logger.error(f"All model attempts failed. Last error: {last_error}")
        raise HTTPException(status_code=500, detail=f"All models failed. Last error: {str(last_error)}")



    async def get_system_prompt(self, user_messages: Optional[List[Dict[str, Any]]] = None) -> str:
        """Construct the dynamic system prompt with memory context and environmental awareness."""
        memory_facts = ""
        memory_status_msg = ""
        if user_messages:
            try:
                # Use LLM to generate a context-aware search query
                search_query = await self._generate_search_query(user_messages)
                if search_query:
                    from agent_runner.tools.mcp import tool_mcp_proxy
                    
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
        if not self.state.internet_available:
             try:
                 # Quick check to 1.1.1.1 (fastest)
                 # We need to import here to avoid circulars if possible, or assume it's available
                 import httpx
                 # Use a temp client for this emergency check to avoid shared state locking issues
                 async with httpx.AsyncClient(timeout=3.0) as jit_client:
                     jit_res = await jit_client.head("https://1.1.1.1")
                     if jit_res.status_code < 400:
                         logger.info("JIT Internet Check PASSED. Overriding stale offline state.")
                         self.state.internet_available = True
             except Exception as jit_e:
                 logger.warning(f"JIT Internet Check failed: {jit_e}")

        if self.state.internet_available:
            env_instructions = (
                "You have access to real-time internet tools (exa, tavily, perplexity).\n"
                "PRIORITY RULE: For factual/public questions (e.g. news, stocks), use web search tools.\n"
                "PRIORITY RULE: For PERSONAL questions (e.g. 'my dog', 'I said'), use INTERNAL MEMORY first. DO NOT search the web for user-specific facts unless explicitly asked."
            )
        else:
            env_instructions = (
                "NOTICE: The system is currently in LOCAL-ONLY mode because the internet is unavailable.\n"
                "Do NOT attempt to use web search tools (exa, tavily, perplexity, firecrawl). They will fail.\n"
                "Inform the user that you are operating offline if they ask for real-time information.\n"
                "Rely on your internal knowledge and the 'project-memory' and 'filesystem' tools."
            )

        # Check for service outages via circuit breaker
        service_alerts = ""
        open_breakers = [name for name, b in self.state.mcp_circuit_breaker.get_status().items() if b["state"] == "open"]
        if open_breakers:
            service_alerts = (
                "\nCRITICAL SERVICE ALERTS:\n"
                f"The following MCP servers are temporarily DISABLED due to repeated infrastructure failures: {', '.join(open_breakers)}.\n"
                "Do NOT attempt to use tools from these servers until they are restored. Inform the user of the outage if they specifically requested these tools."
            )
        
        if memory_status_msg:
             service_alerts += f"\n{memory_status_msg}"

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
            f"{env_instructions}\n"
            f"{service_alerts}\n"
            "You are a helpful, intelligent assistant. Engage naturally with the user.\n"
            "When you use a tool, weave the result or confirmation naturally into your answer. Avoid robotic 'I have done X' statements unless necessary for clarity. Be concise.\n"
            "Use the tools provided to you to be the most helpful assistant possible.\n"
            "IMPORTANT: Focus on the user's LATEST message. Do not maintain context from unrelated previous topics.\n"
            "MEMORY CONSTRAINT: You have access to retrieved memory/facts below. Do NOT mention them unless they are DIRECTLY relevant to answering the CURRENT question. Do not say 'Regarding X...' if the user didn't ask about X."
            f"{memory_facts}"
            f"{files_info}"
        )
        return prompt

    async def agent_loop(self, user_messages: List[Dict[str, Any]], model: Optional[str] = None, tools: Optional[List[Dict[str, Any]]] = None, request_id: Optional[str] = None) -> Dict[str, Any]:
        # Context Pruning: Prevent "Choking" on long histories
        PRUNE_LIMIT = 20
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
            fallback = self.state.fallback_model or "ollama:llama3.3:70b-instruct-q8_0"
            logger.warning(f"Internet offline: Diverting from Cloud model to Local Fallback ({fallback})")
            active_model = fallback

        # 1. Context Injection: Get dynamic prompt
        system_prompt = await self.get_system_prompt(user_messages)
        messages = [{"role": ROLE_SYSTEM, "content": system_prompt}] + user_messages
        steps = 0
        active_tools = tools or await self.get_all_tools()
        
        while steps < self.state.max_tool_steps:
            steps += 1
            response = await self.call_gateway_with_tools(messages, active_model, active_tools)
            choice = response["choices"][0]
            message = choice["message"]
            
            messages.append(message)
            
            if not message.get("tool_calls"):
                # Check for Finalizer Handover
                if self.state.finalizer_enabled and self.state.finalizer_model and self.state.finalizer_model != active_model:
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
                    if isinstance(result, BaseException):
                        content = json.dumps({"ok": False, "error": str(result)})
                    elif isinstance(result, dict):
                        content = json.dumps(result.get("result", result.get("error")))
                    else:
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
            is_safe_local = target_model.startswith(("ollama:", "local:", "test:"))
            if not is_safe_local:
                target_model = self.state.fallback_model or "ollama:llama3.3:70b-instruct-q8_0"

        # Prepare candidates (Primary + Fallback)
        candidates = [target_model]
        fallback = self.state.fallback_model or "ollama:llama3.3:70b-instruct-q8_0"
        if self.state.fallback_enabled and fallback not in candidates:
            candidates.append(fallback)
            
        headers = {}
        if self.state.router_auth_token:
            headers["Authorization"] = f"Bearer {self.state.router_auth_token}"

        client = await self.state.get_http_client()
        url = f"{self.state.gateway_base}/v1/chat/completions"

        for attempt_model in candidates:
            if not self.state.mcp_circuit_breaker.is_allowed(attempt_model):
                continue

            active_tools = tools or self.executor.tool_definitions
            payload = {
                OBJ_MODEL: attempt_model,
                "messages": messages,
                "tools": active_tools,
                "tool_choice": "auto",
                "stream": True,
            }

            try:
                # Streaming Call
                async with client.stream("POST", url, json=payload, headers=headers, timeout=self.state.http_timeout) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                yield data
                            except Exception:
                                pass
                
                # If we finished the stream successfully, return (break loop)
                self.state.mcp_circuit_breaker.record_success(attempt_model)
                return 

            except Exception as e:
                logger.error(f"Streaming failed for '{attempt_model}': {e}")
                self.state.mcp_circuit_breaker.record_failure(attempt_model)
                # Loop to next candidate

        raise HTTPException(status_code=500, detail="All streaming models failed.")

    async def agent_stream(self, user_messages: List[Dict[str, Any]], model: Optional[str] = None, request_id: Optional[str] = None):
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
        system_prompt = await self.get_system_prompt(user_messages)
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
                yield {"type": "done", "stop_reason": "end_turn"}
                break
