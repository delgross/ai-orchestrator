import logging
import os
import time
import json
from typing import Dict, List, Any, Optional
from fastapi import HTTPException
import httpx
import asyncio

from agent_runner.state import AgentState
from common.constants import OBJ_MODEL, ROLE_SYSTEM, ROLE_TOOL
from common.unified_tracking import track_event, EventSeverity, EventCategory
from agent_runner.tools import fs as fs_tools
from agent_runner.tools import mcp as mcp_tools

logger = logging.getLogger("agent_runner")

class AgentEngine:
    def __init__(self, state: AgentState):
        self.state = state
        self.tool_impls = self._init_tool_impls()
        self.tool_definitions = self._init_tool_definitions()
        self.mcp_tool_cache: Dict[str, List[Dict[str, Any]]] = {}

    def _init_tool_impls(self):
        impls = {
            "list_dir": fs_tools.tool_list_dir,
            "path_info": fs_tools.tool_path_info,
            "read_text": fs_tools.tool_read_text,
            "write_text": fs_tools.tool_write_text,
            "append_text": fs_tools.tool_append_text,
            "make_dir": fs_tools.tool_make_dir,
            "remove_file": fs_tools.tool_remove_file,
            "remove_dir": fs_tools.tool_remove_dir,
            "move_path": fs_tools.tool_move_path,
            "copy_file": fs_tools.tool_copy_file,
            "copy_path": fs_tools.tool_copy_path,
            "find_files": fs_tools.tool_find_files,
            "batch_operations": fs_tools.tool_batch_operations,
            "watch_path": fs_tools.tool_watch_path,
            "query_static_resources": fs_tools.tool_query_static_resources,
            "mcp_proxy": mcp_tools.tool_mcp_proxy,
            "knowledge_search": self.tool_knowledge_search,
            "search": self.tool_unified_search,
            "ingest_knowledge": self.tool_ingest_knowledge,
            "ingest_file": self.tool_ingest_file,
        }
        return impls

    def _init_tool_definitions(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "list_dir",
                    "description": "List contents of a directory in the sandboxed workspace. Returns file names, sizes, and types.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Relative path to list (default '.')"},
                            "recursive": {"type": "boolean", "description": "Whether to list subdirectories", "default": False},
                            "max_depth": {"type": "integer", "description": "Max recursion depth", "default": 2}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_text",
                    "description": "Read the text content of a file from the workspace.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Path to the file to read."},
                            "max_bytes": {"type": "integer", "description": "Optional limit on bytes to read."}
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_text",
                    "description": "Create a new file or overwrite an existing one with text content.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Path to create/overwrite."},
                            "content": {"type": "string", "description": "The text content to write."},
                            "overwrite": {"type": "boolean", "description": "Whether to allow overwriting existing files.", "default": False}
                        },
                        "required": ["path", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "mcp_proxy",
                    "description": "Call a tool on an MCP (Model Context Protocol) server. Useful for external capabilities like weather, search, or specialized databases.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "server": {"type": "string", "description": "The name of the MCP server to call."},
                            "tool": {"type": "string", "description": "The name of the tool on that server."},
                            "arguments": {"type": "object", "description": "The arguments to pass to the tool."}
                        },
                        "required": ["server", "tool", "arguments"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "query_static_resources",
                    "description": "Search or read documentation and reference materials from the 'Static Resources' folder.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Optional keyword search query."},
                            "resource_name": {"type": "string", "description": "Specific file name to read."},
                            "list_all": {"type": "boolean", "description": "List all available resources."}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "knowledge_search",
                    "description": "Deep search across uploaded PDFs, manuals, and long-form documents in your knowledge bases (RAG). Use this for complex questions that require more than just short facts.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The specific question or topic to search for."},
                            "kb_id": {"type": "string", "description": "The specific knowledge base to search (default 'default'). Use 'farm-noc' for equipment/infrastructure data."}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search",
                    "description": "The ultimate search tool. It automatically checks your short-term facts (SurrealDB) AND your deep-knowledge bases (RAG). Use this first for any question about your project, farm, or past conversations.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The question or topic to search for."}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "ingest_knowledge",
                    "description": "Store a piece of text into the deep knowledge base (RAG). Use this for permanent business logic, farm specs, or medical protocols.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "The content to remember."},
                            "kb_id": {"type": "string", "description": "Knowledge base ID (default 'default')."},
                            "source_name": {"type": "string", "description": "Friendly name for the source (e.g. 'Farm Policy 2025')."}
                        },
                        "required": ["text"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "ingest_file",
                    "description": "Take an existing file from the uploads folder and ingest it into the deep knowledge base.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Path to the file (e.g. 'uploads/data.txt')."},
                            "kb_id": {"type": "string", "description": "Knowledge base ID (default 'default')."}
                        },
                        "required": ["path"]
                    }
                }
            }
        ]

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
            active_tools = tools or self.tool_definitions
            payload = {
                OBJ_MODEL: attempt_model,
                "messages": messages,
                "tools": active_tools,
                "tool_choice": "auto",
                "stream": False,
            }
            
            # [COST-AUDIT] Log estimated token usage
            try:
                msg_len = len(json.dumps(messages))
                tool_len = len(json.dumps(active_tools))
                est_msg_tok = msg_len // 4
                est_tool_tok = tool_len // 4
                logger.info(f"[COST-AUDIT] Model: {attempt_model} | Msgs: ~{est_msg_tok} toks | Tools: ~{est_tool_tok} toks | Total Est: ~{est_msg_tok + est_tool_tok}")
            except: pass
            
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

    async def execute_tool_call(self, tool_call: Dict[str, Any], request_id: Optional[str] = None) -> Dict[str, Any]:
        fn = tool_call.get("function") or {}
        name = fn.get("name")
        args_str = fn.get("arguments") or "{}"
        
        if name and str(name).startswith("mcp__"):
            parts = str(name).split("__")
            if len(parts) >= 3:
                server = parts[1]
                tool = "__".join(parts[2:])
                try:
                    args = json.loads(args_str)
                    track_event(
                        event="mcp_proxy_call",
                        message=f"Calling MCP tool: {server}::{tool}",
                        severity=EventSeverity.INFO,
                        category=EventCategory.MCP,
                        component="engine",
                        metadata={"server": server, "tool": tool, "arguments": args},
                        request_id=request_id
                    )
                    from agent_runner.tools.mcp import tool_mcp_proxy
                    result = await tool_mcp_proxy(self.state, server, tool, args)
                    track_event(
                        event="mcp_proxy_ok",
                        message=f"MCP tool success: {server}::{tool}",
                        severity=EventSeverity.INFO,
                        category=EventCategory.MCP,
                        component="engine",
                        metadata={"server": server, "tool": tool},
                        request_id=request_id
                    )
                    return result
                except Exception as e:
                    track_event(
                        event="mcp_proxy_error",
                        message=f"MCP tool failed: {server}::{tool}",
                        severity=EventSeverity.HIGH,
                        category=EventCategory.MCP,
                        component="engine",
                        metadata={"server": server, "tool": tool, "error_type": type(e).__name__},
                        error=e,
                        request_id=request_id
                    )
                    return {"ok": False, "error": str(e)}

        if name not in self.tool_impls:
            return {"ok": False, "error": f"Unknown tool '{name}'"}
            
        try:
            args = json.loads(args_str)
            impl = self.tool_impls[name]
            
            track_event(
                event="tool_call",
                message=f"Calling local tool: {name}",
                severity=EventSeverity.INFO,
                category=EventCategory.TASK,
                component="engine",
                metadata={"tool_name": name, "arguments": args},
                request_id=request_id
            )
            
            if asyncio.iscoroutinefunction(impl):
                result = await impl(self.state, **args)
            else:
                result = impl(self.state, **args)
            
            track_event(
                event="tool_ok",
                message=f"Local tool success: {name}",
                severity=EventSeverity.INFO,
                category=EventCategory.TASK,
                component="engine",
                metadata={"tool_name": name},
                request_id=request_id
            )
            return {"ok": True, "result": result}
        except Exception as e:
            track_event(
                event="tool_error",
                message=f"Local tool failed: {name}",
                severity=EventSeverity.HIGH,
                category=EventCategory.TASK,
                component="engine",
                metadata={"tool_name": name, "error_type": type(e).__name__},
                error=e,
                request_id=request_id
            )
            return {"ok": False, "error": str(e)}

    async def discover_mcp_tools(self):
        """Discover tools from all configured MCP servers."""
        logger.info(f"Starting MCP discovery. Servers: {list(self.state.mcp_servers.keys())}")
        for server_name in list(self.state.mcp_servers.keys()):
            cfg = self.state.mcp_servers[server_name]
            logger.info(f"Discovering tools for {server_name}. Config: {cfg}")
            try:
                from agent_runner.tools.mcp import tool_mcp_proxy
                res = await tool_mcp_proxy(self.state, server_name, "tools/list", {}, bypass_circuit_breaker=True)
                if res.get("ok"):
                    # Handle both direct result or nested result
                    data = res.get("result", res)
                    remote_tools = data.get("tools", [])
                    defs = []
                    for rt in remote_tools:
                        defs.append({
                            "type": "function",
                            "function": {
                                "name": rt.get("name"),
                                "description": rt.get("description"),
                                "parameters": rt.get("inputSchema", {"type": "object", "properties": {}})
                            }
                        })
                    self.mcp_tool_cache[server_name] = defs
                    logger.info(f"Discovered {len(defs)} tools from MCP server '{server_name}'")
            except Exception as e:
                logger.warning(f"Failed discovery for {server_name}: {e}")
        
        # [FEATURE-9] Generate Static Tool Menu (The "Maître d' Menu")
        # We build a concise summary string of all available servers + tool names
        # Format: "ServerName: Tool1, Tool2 (Description snippet)"
        menu_lines = []
        for srv, tools in self.mcp_tool_cache.items():
            if not tools: continue
            # Get first tool description or server name as hint
            desc_hint = tools[0]["function"].get("description", "")[:60].replace("\n", " ") + "..."
            t_names = [t["function"]["name"] for t in tools[:5]] # Limit to first 5 tools to keep menu small
            if len(tools) > 5:
                t_names.append("...")
            line = f"{srv}: {', '.join(t_names)} | Hint: {desc_hint}"
            menu_lines.append(line)
        
        self.tool_menu_summary = "\n".join(menu_lines)
        logger.info(f"Generated Tool Menu ({len(menu_lines)} servers):\n{self.tool_menu_summary}")

    async def get_all_tools(self, messages: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """Combine built-in tools with discovered MCP tools, filtering by environmental constraints."""
        tools = list(self.tool_definitions)
        
    async def get_all_tools(self, messages: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """Combine built-in tools with discovered MCP tools, filtering by Intent Menu."""
        tools = list(self.tool_definitions)
        
        # 1. Determine Identity/Intent via Maître d'
        target_servers = set()
        if messages:
             # Get last user message
            last_user_msg = next((m for m in reversed(messages) if m.get("role") == "user"), None)
            if last_user_msg:
                # We classify intent based on the latest query
                intent = await self._classify_search_intent(str(last_user_msg.get("content", "")))
                target_servers = set(intent.get("target_servers", []))
                
        # 2. Add Discovered Tools (Filtered)
        for server_name, server_tools in self.mcp_tool_cache.items():
            # Environmental check
            server_cfg = self.state.mcp_servers.get(server_name, {})
            if server_cfg.get("requires_internet") and not self.state.internet_available:
                continue

            # Core servers are ALWAYS allowed (safety/utility)
            is_core = server_name in ["project-memory", "time", "weather", "system-control", "thinking"]
            
            # Selection Logic: Include if Core OR Selected by Maître d'
            if is_core or (server_name in target_servers):
                for t in server_tools:
                    orig_func = t.get("function", {})
                    # No description keywords needed anymore - decision was made at server level!
                    wrapped = {
                        "type": "function",
                        "function": {
                            "name": f"mcp__{server_name}__{orig_func.get('name')}",
                            "description": orig_func.get("description"),
                            "parameters": orig_func.get("parameters")
                        }
                    }
                    tools.append(wrapped)
        
        return tools
        
        return tools

    def _extract_text_content(self, content: Any) -> str:
        """Extract plain text from potential list-based content (common in advanced clients)."""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            # Extract text from blocks like [{'type': 'text', 'text': 'hi'}]
            return " ".join([str(block.get("text", "")) for block in content if isinstance(block, dict) and block.get("type") == "text"])
        return str(content)

    async def _generate_search_query(self, messages: List[Dict[str, Any]]) -> str:
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

        last_user_content = self._extract_text_content(last_user_msg.get("content"))

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
            text = self._extract_text_content(m.get("content"))
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
            response = await self.call_gateway_with_tools(
                messages=prompt_msgs,
                model=self.state.agent_model, 
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

        prompt = (
            "You are Antigravity, a powerful agentic AI assistant running inside the Orchestrator.\n"
            f"Current System Time: {current_time_str}\n"
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
                    else:
                        logger.warning(f"Finalizer '{finalizer_model_id}' is CIRCUIT BROKEN. Skipping directly to fallback.")
                        # 2. Attempt Fallback (Directly)
                         # Preserve Worker's draft in case both Finalizer and Fallback fail
                        worker_draft = messages.pop() if messages else None
                        await self._handle_fallback(messages, active_tools, worker_draft)
            
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
                    category=EventCategory.METRIC,
                    component="engine",
                    metadata={
                        "provided_count": provided_count,
                        "used_count": used_count,
                        "precision": precision,
                        "intent": "feature_9_maitre_d"
                    }
                )

                # Store episode before returning
                if request_id:
                    try:
                        logger.info(f"Storing request {request_id} with {len(messages)} messages")
                        from agent_runner.tools.mcp import tool_mcp_proxy
                        await tool_mcp_proxy(self.state, "project-memory", "store_episode", {"request_id": request_id, "messages": messages})
                    except Exception as e:
                        logger.warning(f"Failed to store episode for request {request_id}: {e}")

                return response
            

            
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

    async def tool_knowledge_search(self, state: AgentState, query: str, kb_id: str = "default") -> Dict[str, Any]:
        """Query the RAG server for deep content."""
        rag_url = "http://127.0.0.1:5555/query"
        try:
            async with httpx.AsyncClient() as client:
                # Use query-specific limit for depth
                payload = {"query": query, "kb_id": kb_id, "limit": 7}
                r = await client.post(rag_url, json=payload, timeout=25.0)
                if r.status_code == 200:
                    data = r.json()
                    # Return both the concatenated text AND the raw chunks for citation building
                    return {
                        "ok": True, 
                        "context_found": data.get("answer", ""), 
                        "chunks": data.get("context", [])
                    }
                else:
                    return {"ok": False, "error": f"RAG server returned {r.status_code}"}
        except Exception as e:
            return {"ok": False, "error": f"RAG connection failed: {str(e)}"}

    async def _classify_search_intent(self, query: str) -> Dict[str, Any]:
        """Classify query and select relevant toolsets using the 'Maître d' Menu'."""
        menu = getattr(self, "tool_menu_summary", "")
        if not menu:
            # Fallback if discovery hasn't run
            return {"target_servers": [], "notes": "No menu available"}

        prompt = (
            "You are the Tool Selector (The Maître d').\n"
            f"User Query: '{query}'\n\n"
            "Available Toolsets (Menu):\n"
            f"{menu}\n\n"
            "Task: Return a JSON object with a list of 'target_servers' that are REQUIRED to answer the query.\n"
            "Rules:\n"
            "1. Be minimalistic. Only select servers if absolutely necessary.\n"
            "2. If the user asks a personal question (e.g. 'my dog'), ONLY select 'project-memory' (or similar).\n"
            "3. If the user asks a public question (e.g. 'stocks'), select search tools (e.g. 'tavily-search', 'exa').\n"
            "4. If no tools are needed (chitchat), return empty list.\n"
            "Response Format: {\"target_servers\": [\"server1\", \"server2\"]}"
        )

        try:
            # Helper for explicit fast call
            async with httpx.AsyncClient() as client:
                payload = {
                    "model": self.state.agent_model, # e.g. gpt-4o-mini
                    "messages": [{"role": "system", "content": prompt}],
                    "stream": False,
                    "response_format": {"type": "json_object"}
                }
                r = await client.post(f"{self.state.gateway_url}/v1/chat/completions", json=payload, timeout=5.0)
                if r.status_code == 200:
                    data = r.json()
                    content = data["choices"][0]["message"]["content"]
                    return json.loads(content)
        except Exception as e:
            logger.warning(f"Intent classification failed: {e}")
        
        # Safe Fallback: Return empty (Core tools will still be loaded by get_all_tools)
        return {"target_servers": []}

    async def tool_unified_search(self, state: AgentState, query: str) -> Dict[str, Any]:
        """Check both Facts and RAG in one go with adaptive multi-domain routing."""
        # 1. INTENT CLASSIFICATION (Feature 6: Adaptive Search)
        intent = await self._classify_search_intent(query)
        
        # 2. DYNAMIC DISPATCHER
        # Get existing KB stats to see what's actually available
        target_kbs = ["default"] if intent["rag"] else []
        q_lower = query.lower()
        
        if intent["rag"]:
            # CIRCUIT BREAKER: Fast health check before committing to complex parallel search
            try:
                async with httpx.AsyncClient() as client:
                    # We check stats as it doubles as a health & discovery check
                    stats_res = await client.get("http://127.0.0.1:5555/stats", timeout=2.0)
                    if stats_res.status_code != 200:
                        logger.warning("UNIFIED SEARCH: RAG Circuit Breaker TRIPPED. Falling back to MEMORY ONLY.")
                        target_kbs = [] # Disable RAG for this query
                    else:
                        available_kbs = stats_res.json().get("knowledge_bases", {}).keys()
                        # Detect if query keywords match any known KB names
                        for kb in available_kbs:
                            if kb.replace("farm-", "").replace("osu-", "") in q_lower:
                                target_kbs.append(kb)
            except Exception as e:
                logger.warning(f"UNIFIED SEARCH: RAG Connection Failed ({e}). Falling back to MEMORY ONLY.")
                target_kbs = []

            # Hardcoded semantic fallbacks for common aliases
            domains = {
                "farm-noc": ["starlink", "router", "noc", "wan", "lan", "ip", "network", "omada"],
                "osu-med": ["medical", "osu", "clinic", "health", "radiology", "doctor"],
                "farm-beekeeping": ["bees", "hive", "honey", "queen", "apiary", "pollination"],
                "farm-agronomy": ["planting", "harvest", "soil", "crop", "seed", "fertilizer", "tractor"],
                "farm-woodworking": ["woodworking", "wood", "saw", "joint", "joinery", "lathe", "planer", "workshop", "lumber", "species"]
            }
            for kb, keywords in domains.items():
                if any(w in q_lower for w in keywords):
                    target_kbs.append(kb)
            
            # Filter duplicates and remove 'default' if we have specific hits
            target_kbs = list(set(target_kbs))
            if len(target_kbs) > 1 and "default" in target_kbs:
                target_kbs.remove("default")

        # 3. Start parallel searches across ALL relevant layers
        from agent_runner.tools.mcp import tool_mcp_proxy
        
        search_tasks = []
        fact_idx = -1
        
        # Parallel Fact Search (The Diary)
        if intent["facts"]:
            fact_idx = len(search_tasks)
            search_tasks.append(asyncio.create_task(tool_mcp_proxy(state, "project-memory", "semantic_search", {"query": query})))
        
        # Parallel Multi-KB Search (The Library)
        rag_start_idx = len(search_tasks)
        if target_kbs:
            for kb in target_kbs:
                search_tasks.append(asyncio.create_task(self.tool_knowledge_search(state, query, kb_id=kb)))
        
        if not search_tasks:
             return {"ok": True, "message": "Query classified as out-of-scope for searching."}

        # Wait for all
        all_results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        fact_res = {"ok": False}
        if fact_idx != -1:
            fact_res = all_results[fact_idx] if not isinstance(all_results[fact_idx], BaseException) else {"ok": False}
        
        rag_results = all_results[rag_start_idx:]
        
        combined_context = f"SEARCH MODE: Hybrid (Domains: {', '.join(target_kbs)})\n\n"
        
        if fact_res.get("ok"):
            # Unwrap MCP response
            try:
                res_obj = fact_res.get("result", {})
                if "content" in res_obj:
                    # Standard MCP TextContent
                    facts_data = json.loads(res_obj["content"][0]["text"])
                    facts = facts_data.get("facts", [])
                else:
                    facts = res_obj.get("facts", [])
                
                if facts:
                    combined_context += "### [MEMORY DIARY] (Short-term confirmed facts):\n"
                    # Filter for only high confidence facts in search results
                    for f in facts[:5]:
                        if f.get("confidence", 1.0) > 0.4:
                            combined_context += f"- {f.get('entity')} {f.get('relation')} {f.get('target')} (Confidence: {f.get('confidence', 0.0):.2f})\n"
                    combined_context += "\n"
            except: pass
        
        # 3. Process Multi-KB results
        for i, rag_res in enumerate(rag_results):
            if isinstance(rag_res, Exception) or not rag_res.get("ok"):
                continue
                
            chunks = rag_res.get("chunks", [])
            kb_name = target_kbs[i]
            if chunks:
                combined_context += f"### [DEEP KNOWLEDGE: {kb_name}]\n"
                for j, c in enumerate(chunks):
                    fname = c.get("filename", "Unknown Source")
                    quality = c.get("quality_score", 0.0)
                    combined_context += f"\n[DOC {j+1} from {fname}] (QoI: {quality:.2f})\n{c.get('content')}\n"
                combined_context += "\n"
                
        if len(combined_context) < 50:
            return {"ok": True, "message": "No relevant info found in facts or documents."}
            
        return {"ok": True, "search_results": combined_context}

    async def tool_ingest_knowledge(self, state: AgentState, text: str, kb_id: str = "default", source_name: str = "Chat") -> Dict[str, Any]:
        """Manually push text into RAG."""
        rag_url = "http://127.0.0.1:5555/ingest"
        try:
            payload = {
                "content": text,
                "kb_id": kb_id,
                "filename": source_name,
                "metadata": {"type": "manual_ingest", "timestamp": time.time()}
            }
            async with httpx.AsyncClient() as client:
                r = await client.post(rag_url, json=payload, timeout=30.0)
                if r.status_code == 200:
                    return {"ok": True, "message": f"Successfully ingested {len(text)} chars into KB '{kb_id}'"}
                return {"ok": False, "error": f"RAG server error: {r.status_code}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}


    async def tool_ingest_file(self, state: AgentState, path: str, kb_id: str = "default") -> Dict[str, Any]:
        """Ingest a file from the local filesystem (sandbox) into RAG."""
        full_path = os.path.join(state.agent_fs_root, path)
        if not os.path.exists(full_path):
            return {"ok": False, "error": f"File not found: {path}"}
        
        try:
            # Check extension
            ext = os.path.splitext(path)[1].lower()
            if ext not in ['.txt', '.md', '.csv']:
                return {"ok": False, "error": f"Unsupported file type for direct ingestion: {ext}. Currently only text-based files are supported."}
            
            with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            
            return await self.tool_ingest_knowledge(state, content, kb_id, source_name=os.path.basename(path))
        except Exception as e:
            return {"ok": False, "error": f"Ingestion failed: {str(e)}"}

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
                # 3. Revert to Worker
                if worker_draft: messages.append(worker_draft)
        else:
            # Fallback disabled, Revert
            logger.warning("Fallback disabled. Reverting to Worker response.")
            if worker_draft: messages.append(worker_draft)
