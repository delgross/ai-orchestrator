import asyncio
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional
import httpx

from agent_runner.state import AgentState
from agent_runner.tools import fs as fs_tools
from agent_runner.tools import mcp as mcp_tools
from common.unified_tracking import track_event, EventSeverity, EventCategory

logger = logging.getLogger("agent_runner.executor")

class ToolExecutor:
    def __init__(self, state: AgentState):
        self.state = state
        self.mcp_tool_cache: Dict[str, List[Dict[str, Any]]] = {}
        self.tool_menu_summary = ""
        self.tool_impls = self._init_tool_impls()
        self.tool_definitions = self._init_tool_definitions()

    def _init_tool_impls(self) -> Dict[str, Any]:
        return {
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

    def _init_tool_definitions(self) -> List[Dict[str, Any]]:
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
                            "kb_id": {"type": "string", "description": "The specific knowledge base to search (default 'default')."},
                            "filters": {"type": "object", "description": "Optional metadata filters (e.g. {'brand': 'TIME', 'visual_credibility': {'$gt': 0.8}})."}
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
        
        menu_lines = []
        core_servers = {"project-memory", "time", "weather", "thinking", "system-control"}
        
        for srv, tools in self.mcp_tool_cache.items():
            if not tools:
                continue
            if srv in core_servers:
                continue
            
            t_names = [t["function"]["name"] for t in tools[:8]]
            if len(tools) > 8:
                t_names.append("...")
            line = f"{srv}: {', '.join(t_names)}"
            menu_lines.append(line)
        
        self.tool_menu_summary = "\n".join(menu_lines)
        if not self.tool_menu_summary:
            self.tool_menu_summary = "(No external tools available)"
        logger.info(f"Generated Maître d' Menu: {self.tool_menu_summary}")

    async def get_all_tools(self, messages: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """Combine built-in tools with discovered MCP tools, filtering by Intent Menu."""
        tools = list(self.tool_definitions)
        
        target_servers = set()
        if messages:
            last_user_msg = next((m for m in reversed(messages) if m.get("role") == "user"), None)
            if last_user_msg:
                from agent_runner.intent import classify_search_intent
                intent = await classify_search_intent(str(last_user_msg.get("content", "")), self.state, self.tool_menu_summary)
                target_servers = set(intent.get("target_servers", []))
                
        for server_name, server_tools in self.mcp_tool_cache.items():
            server_cfg = self.state.mcp_servers.get(server_name, {})
            if server_cfg.get("requires_internet") and not self.state.internet_available:
                continue

            is_core = server_name in ["project-memory", "time", "weather", "system-control", "thinking"]
            if is_core or (server_name in target_servers):
                for t in server_tools:
                    orig_func = t.get("function", {})
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
                        component="executor",
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
                        component="executor",
                        metadata={"server": server, "tool": tool},
                        request_id=request_id
                    )
                    
                    try:
                        # [TODO] Record success once messages/query is available in executor
                        pass
                    except Exception as e:
                        logger.warning(f"Failed to record learning: {e}")

                    return result
                except Exception as e:
                    track_event(
                        event="mcp_proxy_error",
                        message=f"MCP tool failed: {server}::{tool}",
                        severity=EventSeverity.HIGH,
                        category=EventCategory.MCP,
                        component="executor",
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
                component="executor",
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
                component="executor",
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
                component="executor",
                metadata={"tool_name": name, "error_type": type(e).__name__},
                error=e,
                request_id=request_id
            )
            return {"ok": False, "error": str(e)}

    async def tool_knowledge_search(self, state: AgentState, query: str, kb_id: str = "default", filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Query the RAG server for deep content."""
        rag_url = "http://127.0.0.1:5555/query"
        try:
            async with httpx.AsyncClient() as client:
                payload = {"query": query, "kb_id": kb_id, "limit": 7}
                if filters:
                    payload["filters"] = filters
                r = await client.post(rag_url, json=payload, timeout=25.0)
                if r.status_code == 200:
                    data = r.json()
                    return {
                        "ok": True, 
                        "context_found": data.get("answer", ""), 
                        "chunks": data.get("context", [])
                    }
                else:
                    return {"ok": False, "error": f"RAG server returned {r.status_code}"}
        except Exception as e:
            return {"ok": False, "error": f"RAG connection failed: {str(e)}"}

    async def tool_unified_search(self, state: AgentState, query: str) -> Dict[str, Any]:
        """Check both Facts and RAG in one go with adaptive multi-domain routing."""
        from agent_runner.intent import classify_search_intent
        intent = await classify_search_intent(query, self.state, self.tool_menu_summary)
        
        # Determine which layers to search
        search_rag = intent.get("rag", True)
        search_facts = intent.get("facts", True)
        
        target_kbs = ["default"]
        q_lower = query.lower()
        
        # CIRCUIT BREAKER: Fast health check before committing to complex parallel search
        try:
            async with httpx.AsyncClient() as client:
                stats_res = await client.get("http://127.0.0.1:5555/stats", timeout=2.0)
                if stats_res.status_code != 200:
                    logger.warning("UNIFIED SEARCH: RAG Circuit Breaker TRIPPED. Falling back to MEMORY ONLY.")
                    search_rag = False
                else:
                    available_kbs = stats_res.json().get("knowledge_bases", {}).keys()
                    for kb in available_kbs:
                        if kb.replace("farm-", "").replace("osu-", "") in q_lower:
                            target_kbs.append(kb)
        except Exception as e:
            logger.warning(f"UNIFIED SEARCH: RAG Connection Failed ({e}). Falling back to MEMORY ONLY.")
            search_rag = False

        if search_rag:
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
            
            target_kbs = list(set(target_kbs))
            if len(target_kbs) > 1 and "default" in target_kbs:
                target_kbs.remove("default")

        # Start parallel searches
        from agent_runner.tools.mcp import tool_mcp_proxy
        search_tasks = []
        fact_idx = -1
        
        if search_facts:
            fact_idx = len(search_tasks)
            search_tasks.append(asyncio.create_task(tool_mcp_proxy(state, "project-memory", "semantic_search", {"query": query})))
        
        rag_start_idx = len(search_tasks)
        if search_rag and target_kbs:
            for kb in target_kbs:
                search_tasks.append(asyncio.create_task(self.tool_knowledge_search(state, query, kb_id=kb)))
        
        if not search_tasks:
             return {"ok": True, "message": "No search domains active."}

        all_results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        fact_res = {"ok": False}
        if fact_idx != -1:
            fact_res = all_results[fact_idx] if not isinstance(all_results[fact_idx], BaseException) else {"ok": False}
        
        rag_results = all_results[rag_start_idx:]
        combined_context = f"SEARCH MODE: Hybrid (Domains: {', '.join(target_kbs) if search_rag else 'Memory-Only'})\n\n"
        
        if fact_res.get("ok"):
            try:
                res_obj = fact_res.get("result", {})
                content = res_obj.get("content", [])
                if content and content[0].get("text"):
                    facts_data = json.loads(content[0]["text"])
                    facts = facts_data.get("facts", [])
                else:
                    facts = res_obj.get("facts", [])
                
                if facts:
                    combined_context += "### [MEMORY DIARY]:\n"
                    for f in facts[:5]:
                        combined_context += f"- {f.get('entity')} {f.get('relation')} {f.get('target')}\n"
                    combined_context += "\n"
            except Exception:
                pass
        
        if search_rag:
            for i, rag_res in enumerate(rag_results):
                if isinstance(rag_res, Exception) or not rag_res.get("ok"):
                    continue
                chunks = rag_res.get("chunks", [])
                kb_name = target_kbs[i]
                if chunks:
                    combined_context += f"### [DEEP KNOWLEDGE: {kb_name}]\n"
                    for c in chunks[:3]:
                        combined_context += f"- {c.get('content')[:300]}...\n"
                    combined_context += "\n"
                
        if len(combined_context) < 50:
            return {"ok": True, "message": "No relevant info found."}
            
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
            ext = os.path.splitext(path)[1].lower()
            if ext not in ['.txt', '.md', '.csv']:
                return {"ok": False, "error": f"Unsupported file type: {ext}"}
            
            with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            
            return await self.tool_ingest_knowledge(state, content, kb_id, source_name=os.path.basename(path))
        except Exception as e:
            return {"ok": False, "error": f"Ingestion failed: {str(e)}"}
