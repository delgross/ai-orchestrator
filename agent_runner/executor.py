import asyncio
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional
import httpx

from agent_runner.state import AgentState
from agent_runner.quality_tiers import QualityTier, get_tier_config
from agent_runner.tool_categories import detect_query_capabilities, get_tools_for_capabilities, resolve_capability_conflicts
from agent_runner.tools import fs as fs_tools
from agent_runner.tools import mcp as mcp_tools
from agent_runner.tools import system as system_tools
# [PHASE 54] Introspection
from agent_runner.tools import introspection as introspection_tools
from agent_runner.tools import memory_edit as memory_edit_tools
from agent_runner.tools import memory_tools
# [PHASE 52]
from agent_runner.tools import node as node_tools
# [PHASE 53]
from agent_runner.tools import admin as admin_tools
# [PHASE 42]
from agent_runner.tools import registry as registry_tools
# Core Services
from agent_runner.tools import time as time_tools
from agent_runner.tools import location as location_tools
from agent_runner.tools import web as web_tools
from agent_runner.tools import admin_status as admin_status_tools
from agent_runner.tools import latency as latency_tools
from agent_runner.tools import tool_evaluation as tool_evaluation_tools
from agent_runner.tools import thinking as thinking_tools
from agent_runner.tools import advice as advice_tools

from common.unified_tracking import track_event, EventSeverity, EventCategory
# [PHASE 3] Performance Optimization
from common.caching import MultiLayerCache, MCPToolCache, CacheStrategy

logger = logging.getLogger("agent_runner.executor")

class ToolExecutor:
    def __init__(self, state: AgentState):
        self.state = state
        # MCP tool cache - stores discovered tools per server
        # NOTE: Cache invalidation framework available in agent_runner/cache_helpers.py
        # Future: Integrate with CacheInvalidator for automatic TTL and DB timestamp validation.
        self.mcp_tool_cache: Dict[str, List[Dict[str, Any]]] = {}
        self.tool_menu_summary = ""
        self.tool_impls = self._init_tool_impls()

        # [CONTEXT-DIET] Store definitions by category for dynamic loading
        # [CONTEXT-DIET] Store definitions by category for dynamic loading
        self.tool_categories = self._init_tool_categories()
        
        # [AUTODISCOVERY] Find and recover orphans (tools in Registry but not in Menu)
        self._auto_discover_orphans()
        
        # Flat list for legacy support / fallback
        self.tool_definitions = [t for cats in self.tool_categories.values() for t in cats]
        
        # [PHASE 3] Performance Optimization: Multi-layer caching
        underlying_cache = MultiLayerCache(
            max_size=10000,
            default_ttl=300.0,  # 5 minutes for MCP tools
            strategy=CacheStrategy.LRU
        )
        self.mcp_response_cache = MCPToolCache(underlying_cache)

        # [VECTOR-SEARCH] Trigger background indexing of tools
        if hasattr(self.state, "vector_store"):
            asyncio.create_task(self.state.vector_store.index_tools(self.tool_definitions))

    
    def invalidate_mcp_cache(self, server_name: Optional[str] = None):
        """
        Invalidate MCP tool response cache.
        
        Args:
            server_name: If provided, invalidate cache for specific server.
                         If None, invalidate entire MCP cache.
        """
        if server_name:
            # Invalidate specific server's cache
            invalidated = self.mcp_response_cache.cache.invalidate(
                namespace=self.mcp_response_cache.namespace,
                key=None  # Will invalidate all keys in namespace
            )
            logger.info(f"Invalidated {invalidated} cache entries for MCP server: {server_name}")
        else:
            # Invalidate all MCP cache
            self.mcp_response_cache.cache.clear()
            logger.info("Cleared entire MCP response cache")

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
            "run_command": system_tools.tool_run_command,
            "trigger_task": system_tools.tool_trigger_task,
            "report_missing_tool": system_tools.tool_report_missing_tool,
            "run_memory_consolidation": system_tools.tool_run_memory_consolidation,
            "remove_memory_from_file": memory_edit_tools.tool_remove_memory_from_file,
            "check_system_health": system_tools.tool_check_system_health,
            "import_mcp_config": mcp_tools.tool_import_mcp_config,
            "add_mcp_server": mcp_tools.tool_add_mcp_server,
            "install_mcp_package": mcp_tools.tool_install_mcp_package,
            "investigate_system_performance": latency_tools.tool_investigate_system_performance,
            "run_latency_tests": latency_tools.tool_run_latency_tests,
            # Phase 52: Node Tools
            "run_node": node_tools.run_node,
            "run_npm": node_tools.run_npm,
            # Phase 53: Admin Tools
            "unlock_session": admin_tools.unlock_session,
            "set_policy": admin_tools.set_policy,
            "check_admin_status": admin_tools.check_admin_status,
            # Registry Tools
            "registry_list": registry_tools.tool_registry_list,
            "registry_read": registry_tools.tool_registry_read,
            "registry_append": registry_tools.tool_registry_append,
            "registry_write": registry_tools.tool_registry_write,
            # Advice Utils
            "consult_advice": advice_tools.tool_consult_advice,
            "view_last_system_prompt": advice_tools.tool_debug_view_last_prompt,
            "view_active_advice": advice_tools.tool_debug_view_active_advice,
            # Introspection Tools
            "get_service_status": introspection_tools.tool_get_service_status,
            "get_component_map": introspection_tools.tool_get_component_map,
            "get_active_configuration": introspection_tools.tool_get_active_configuration,
            "list_system_toggles": introspection_tools.tool_list_system_toggles,
            "get_system_config": system_tools.tool_get_system_config,
            "set_system_config": system_tools.tool_set_system_config,
            "sentinel_authorize": system_tools.tool_sentinel_authorize,
            "register_trigger": system_tools.tool_register_trigger,
            "remove_trigger": system_tools.tool_remove_trigger,
            "list_triggers": system_tools.tool_list_triggers,
            # Quality Tier Management
            "set_quality_tier": system_tools.tool_set_quality_tier,
            "get_quality_tier": system_tools.tool_get_quality_tier,
            "get_quality_tier_comparison": system_tools.tool_get_quality_tier_comparison,
            # Core Services: Time and Location
            "get_current_time": time_tools.tool_get_current_time,
            "convert_time": time_tools.tool_convert_time,
            "get_location": location_tools.tool_get_location,
            
            # [MEMORY] Native Memory Tools (Decoupled from MCP)
            "memory_store_fact": memory_tools.tool_memory_store_fact,
            "memory_query_facts": memory_tools.tool_memory_query_facts,
            "memory_search_semantic": memory_tools.tool_memory_search_semantic,
            "memory_consolidate": memory_tools.tool_memory_consolidate,
            
            # System Control
            "restart_agent": system_tools.tool_restart_agent,
            "get_boot_status": system_tools.tool_get_boot_status,
            # System Tools (Additional)
            "set_mode": system_tools.tool_set_mode,
            "query_logs": system_tools.tool_query_logs,
            "add_lexicon_entry": system_tools.tool_add_lexicon_entry,
            "manage_secret": system_tools.tool_manage_secret,
            "clear_boot_status": system_tools.tool_clear_boot_status,
            "set_quality_tier": system_tools.tool_set_quality_tier,
            "get_quality_tier": system_tools.tool_get_quality_tier,
            "control_refinement": system_tools.tool_control_refinement,
            "set_context_prune_limit": system_tools.tool_set_context_prune_limit,
            "filter_tools_by_category": system_tools.tool_filter_tools_by_category,
            "get_layer_status": system_tools.tool_get_layer_status,
            # Web Tools
            "search_web": web_tools.tool_search_web,
            # Admin Status Tools
            "get_circuit_breaker_status": admin_status_tools.tool_get_circuit_breaker_status,
            "get_memory_status": admin_status_tools.tool_get_memory_status,
            "get_ingestion_status": admin_status_tools.tool_get_ingestion_status,
            "pause_ingestion": admin_status_tools.tool_pause_ingestion,
            "resume_ingestion": admin_status_tools.tool_resume_ingestion,
            "clear_ingestion_problem": admin_status_tools.tool_clear_ingestion_problem,
            "reset_circuit_breaker": admin_status_tools.tool_reset_circuit_breaker,
            "reset_all_circuit_breakers": admin_status_tools.tool_reset_all_circuit_breakers,
            "get_background_tasks_status": admin_status_tools.tool_get_background_tasks_status,
            "get_task_health": admin_status_tools.tool_get_task_health,
            "get_registry_health": admin_status_tools.tool_get_registry_health,
            "get_mcp_server_status": admin_status_tools.tool_get_mcp_server_status,
            "get_system_diagnostics": admin_status_tools.tool_get_system_diagnostics,
            "toggle_mcp_server": admin_status_tools.tool_toggle_mcp_server,
            "reset_mcp_servers": admin_status_tools.tool_reset_mcp_servers,
            "reload_mcp_servers": admin_status_tools.tool_reload_mcp_servers,
            "trigger_memory_consolidation": admin_status_tools.tool_trigger_memory_consolidation,
            "trigger_backup": admin_status_tools.tool_trigger_backup,
            "update_model_config": admin_status_tools.tool_update_model_config,
            "get_chat_functionality_analysis": admin_status_tools.tool_get_chat_functionality_analysis,
            "list_all_available_tools": admin_status_tools.tool_list_all_available_tools,
            "get_system_prompt": admin_status_tools.tool_get_system_prompt,
            "get_memory_facts": admin_status_tools.tool_get_memory_facts,
            "get_llm_roles": admin_status_tools.tool_get_llm_roles,
            "get_detailed_system_status": admin_status_tools.tool_get_detailed_system_status,
            "get_system_metrics": admin_status_tools.tool_get_system_metrics,
            "inspect_system_prompt": admin_status_tools.tool_inspect_system_prompt,
            "analyze_query_classification": admin_status_tools.tool_analyze_query_classification,
            "evaluate_response_quality": admin_status_tools.tool_evaluate_response_quality,
            # Latency Tools
            "investigate_system_performance": latency_tools.tool_investigate_system_performance,
            "run_chat_latency_test": latency_tools.tool_run_chat_latency_test,
            "run_latency_tests": latency_tools.tool_run_latency_tests,
            # Tool Evaluation Tools
            "evaluate_tool_health": tool_evaluation_tools.tool_evaluate_tool_health,
            "get_tool_health_dashboard": tool_evaluation_tools.tool_get_tool_health_dashboard,
            "deprecate_tool": tool_evaluation_tools.tool_deprecate_tool,
            "record_tool_usage": tool_evaluation_tools.tool_record_tool_usage,
            # Thinking Tools
            "sequential_thinking": thinking_tools.tool_sequential_thinking,
            "get_thinking_history": thinking_tools.tool_get_thinking_history,
            "start_thinking_session": thinking_tools.tool_start_thinking_session,
            "start_thinking_branch": thinking_tools.tool_start_thinking_branch,
            "get_thinking_progress": thinking_tools.tool_get_thinking_progress,
            "analyze_thinking_efficiency": thinking_tools.tool_analyze_thinking_efficiency,
             "get_thinking_progress": thinking_tools.tool_get_thinking_progress,
            "analyze_thinking_efficiency": thinking_tools.tool_analyze_thinking_efficiency,
            # Graph Tools (Stub)
            "get_graph_snapshot": self.tool_get_graph_snapshot,
        }
    
    def _init_tool_categories(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize tools grouped by category for Context Diet."""
        return {
            "core": [
                {
                    "type": "function",
                    "function": {
                        "name": "get_current_time",
                        "description": "Get current time in ISO format or specific timezone.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "timezone": {"type": "string", "description": "Timezone e.g. 'America/New_York'"}
                            }
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_location",
                        "description": "Get current physical location of the server/agent.",
                        "parameters": {"type": "object", "properties": {}}
                    }
                },
                 {
                    "type": "function",
                    "function": {
                        "name": "convert_time",
                        "description": "Convert time between timezones.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "time_str": {"type": "string", "description": "Time string"},
                                "source_tz": {"type": "string"},
                                "target_tz": {"type": "string"}
                            },
                             "required": ["time_str", "target_tz"]
                        }
                    }
                }
            ],
            "graph": [
                {
                    "type": "function",
                    "function": {
                        "name": "get_graph_snapshot",
                        "description": "Get a snapshot of the knowledge graph (nodes/edges).",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "limit": {"type": "integer", "description": "Max nodes (default 100)"},
                                "format": {"type": "string", "enum": ["json", "mermaid"], "default": "json"}
                            }
                        }
                    }
                }
            ],
            "filesystem": [
                 {
                    "type": "function",
                    "function": {
                        "name": "list_dir",
                        "description": "List contents of a directory in the sandboxed workspace.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string", "description": "Relative path (default '.')"},
                                "recursive": {"type": "boolean", "default": False},
                                "max_depth": {"type": "integer", "default": 2}
                            }
                        }
                    }
                },
                 {
                    "type": "function",
                    "function": {
                        "name": "read_text",
                        "description": "Read text file content.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string", "description": "Path to file"},
                                "start_line": {"type": "integer"},
                                "end_line": {"type": "integer"}
                            },
                            "required": ["path"]
                        }
                    }
                },
                 {
                    "type": "function",
                    "function": {
                        "name": "write_text",
                        "description": "Write text to file (overwrites).",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string", "description": "Path to file"},
                                "content": {"type": "string", "description": "Content to write"}
                            },
                            "required": ["path", "content"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "append_text",
                        "description": "Append text to file.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string"},
                                "content": {"type": "string"}
                            },
                            "required": ["path", "content"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "make_dir",
                        "description": "Create directory recursively.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string"}
                            },
                            "required": ["path"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "path_info",
                        "description": "Get file/directory metadata.",
                        "parameters": {
                             "type": "object",
                             "properties": { "path": {"type": "string"} },
                             "required": ["path"]
                        }
                    }
                },
                {
                     "type": "function",
                     "function": {
                         "name": "find_files",
                         "description": "Find files matching pattern.",
                         "parameters": {
                             "type": "object",
                             "properties": {
                                 "path": {"type": "string"},
                                 "pattern": {"type": "string", "description": "Glob pattern e.g. '*.py'"}
                             },
                             "required": ["path", "pattern"]
                         }
                     }
                }
            ],
            "system": [
                {
                    "type": "function",
                     "function": {
                         "name": "run_command",
                         "description": "Execute shell command (Sandboxed).",
                         "parameters": {
                             "type": "object",
                             "properties": {
                                 "command": {"type": "string"},
                                 "timeout": {"type": "integer", "default": 60},
                                 "background": {"type": "boolean", "default": False}
                             },
                             "required": ["command"]
                         }
                     }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "run_node",
                        "description": "Execute Node.js script.",
                        "parameters": {
                             "type": "object",
                             "properties": { "script": {"type": "string"} },
                             "required": ["script"]
                        }
                    }
                },
                {
                     "type": "function",
                     "function": {
                        "name": "check_system_health",
                        "description": "Run diagnostic health check.",
                        "parameters": {"type": "object", "properties": {}}
                     }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "restart_agent",
                        "description": "Restart the Agent Runner service.",
                        "parameters": {"type": "object", "properties": {}}
                    }
                },
                {
                     "type": "function",
                     "function": {
                         "name": "manage_secret",
                         "description": "Securely save/retrieve API keys.",
                         "parameters": {
                             "type": "object",
                             "properties": {
                                 "action": {"type": "string", "enum": ["set", "get", "delete"]},
                                 "key": {"type": "string"},
                                 "value": {"type": "string"}
                             },
                             "required": ["action", "key"]
                         }
                     }
                }
            ],
            "memory": [
                 {
                    "type": "function",
                    "function": {
                        "name": "memory_store_fact",
                        "description": "Store a fact in long-term memory.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "content": {"type": "string", "description": "fact content"},
                                "category": {"type": "string", "default": "general"},
                                "confidence": {"type": "number", "default": 1.0}
                            },
                            "required": ["content"]
                        }
                    }
                },
                 {
                    "type": "function",
                    "function": {
                        "name": "memory_query_facts",
                        "description": "Retrieve facts from long-term memory.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "Natural language query"},
                                "limit": {"type": "integer", "default": 5}
                            },
                            "required": ["query"]
                        }
                    }
                },
                 {
                    "type": "function",
                    "function": {
                        "name": "memory_search_semantic",
                        "description": "Semantic search over memory episodes.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string"},
                                "limit": {"type": "integer", "default": 10},
                                "threshold": {"type": "number", "default": 0.7}
                            },
                            "required": ["query"]
                        }
                    }
                },
                 {
                    "type": "function",
                    "function": {
                        "name": "memory_consolidate",
                        "description": "Trigger memory consolidation/cleanup.",
                        "parameters": {"type": "object", "properties": {}}
                    }
                }
            ],
            "thinking": [
                 {
                    "type": "function",
                    "function": {
                        "name": "sequential_thinking",
                        "description": "Internal Chain of Thought engine.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "thought": {"type": "string"},
                                "needs_more_time": {"type": "boolean"}
                            },
                             "required": ["thought", "needs_more_time"]
                        }
                    }
                }
            ],
            "admin": [
                {
                    "type": "function",
                    "function": {
                        "name": "unlock_session",
                        "description": "Unlock admin session with password.",
                        "parameters": {
                            "type": "object",
                            "properties": {"password": {"type": "string"}},
                            "required": ["password"]
                        }
                    }
                },
                {
                     "type": "function",
                     "function": {
                         "name": "set_policy",
                         "description": "Update security policy.",
                         "parameters": {
                             "type": "object",
                             "properties": {
                                 "entity": {"type": "string"},
                                 "policy": {"type": "string"}
                             },
                             "required": ["entity", "policy"]
                         }
                     }
                },
                {
                    "type": "function",
                    "function": {
                         "name": "check_admin_status",
                         "description": "Check current admin privileges.",
                         "parameters": {"type": "object", "properties": {}}
                    }
                }
            ],
            "cleanup": [
                {
                    "type": "function",
                    "function": {
                         "name": "remove_file",
                         "description": "Delete file.",
                         "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}
                    }
                },
                {
                    "type": "function",
                    "function": {
                         "name": "remove_dir",
                         "description": "Delete directory.",
                         "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}
                    }
                }
            ],
            "exploration": [
                {
                    "type": "function",
                    "function": {
                        "name": "get_component_map",
                        "description": "List all system roles and their assigned models. Use to answer questions about models, inventory all LLMs, list all internal models, or what model is the Router using. Returns data from database (source of truth).",
                        "parameters": {"type": "object", "properties": {}}
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_active_configuration",
                        "description": "Read the current system configuration from database, including all model assignments (AGENT_MODEL, ROUTER_MODEL, etc.). Use to answer questions about models, inventory all LLMs, or show system configuration. Secrets are masked. Database is source of truth.",
                        "parameters": {"type": "object", "properties": {}}
                    }
                },
                # [SYSTEM UNIFICATION] - Bringing Orphans Home
                {
                    "type": "function",
                    "function": {
                        "name": "search_web",
                        "description": "Search the web for real-time information.",
                         "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string"},
                                "domain": {"type": "string", "description": "Optional domain filter"}
                            },
                            "required": ["query"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "consult_advice",
                        "description": "Consult the Advice Subsystem/Critic.",
                        "parameters": {"type": "object", "properties": {"topic": {"type": "string"}}, "required": ["topic"]}
                    }
                },
                {
                    "type": "function",
                    "function": {
                         "name": "run_latency_tests",
                         "description": "Run system latency diagnostics.",
                         "parameters": {"type": "object", "properties": {}}
                    }
                },
                {
                    "type": "function",
                    "function": {
                         "name": "get_circuit_breaker_status",
                         "description": "Check circuit breaker health.",
                         "parameters": {"type": "object", "properties": {}}
                    }
                },
                {
                     "type": "function",
                     "function": {
                         "name": "ingest_knowledge",
                         "description": "Ingest raw text/markdown into Sovereign Memory.",
                         "parameters": {
                             "type": "object", 
                             "properties": {
                                 "content": {"type": "string"},
                                 "source": {"type": "string"},
                                 "category": {"type": "string"}
                             },
                             "required": ["content", "source"]
                         }
                     }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_mcp_server_status",
                        "description": "Get status of all MCP servers (enabled/disabled, tool counts). Use this to debug missing tools.",
                        "parameters": {"type": "object", "properties": {}}
                    }
                },

                {
                    "type": "function",
                    "function": {
                        "name": "list_all_available_tools",
                        "description": "List all available tools in the system by category.",
                        "parameters": {"type": "object", "properties": {"category": {"type": "string", "description": "Optional category filter"}}}
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_system_prompt",
                        "description": "Get the current system prompt being used.",
                        "parameters": {"type": "object", "properties": {}}
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_memory_facts",
                        "description": "Get facts from memory.",
                        "parameters": {"type": "object", "properties": {"entity": {"type": "string"}, "relation": {"type": "string"}, "limit": {"type": "integer"}}}
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_llm_roles",
                        "description": "Get LLM role assignments.",
                        "parameters": {"type": "object", "properties": {}}
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "list_system_toggles",
                        "description": "List system toggles and their current states.",
                        "parameters": {"type": "object", "properties": {}}
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_system_config",
                        "description": "Get a specific system configuration value.",
                        "parameters": {"type": "object", "properties": {"key": {"type": "string"}}, "required": ["key"]}
                    }
                }
            ]
        }
        
    def _auto_discover_orphans(self):
        """
        Identify tools present in `_init_tool_impls` but missing from `_init_tool_categories`.
        Automatically register them in an 'auto_discovered' category to fail-safe against invisibility.
        """
        registered = set(self.tool_impls.keys())
        categorized = set()
        
        for cat_tools in self.tool_categories.values():
            for t in cat_tools:
                categorized.add(t["function"]["name"])
                
        orphans = registered - categorized
        
        if not orphans:
            return
            
        logger.warning(f"⚠️ [AUTODISCOVERY] Found {len(orphans)} orphaned tools! Auto-registering them to 'auto_discovered'.")
        
        auto_discovered = []
        for name in orphans:
            func = self.tool_impls[name]
            doc = (func.__doc__ or "No description provided.").strip().split("\n")[0]
            
            auto_discovered.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": f"[AUTO] {doc}",
                    "parameters": {"type": "object", "properties": {}} # Default to empty schema if unknown
                }
            })
            logger.info(f"  + Adopted Orphan: {name}")
            
        self.tool_categories["auto_discovered"] = auto_discovered

    async def _disable_failed_server(self, server_name: str, reason: str):
        """Helper to disable a failing server and log the reason.
           Updates both runtime state and database.
        """
        import time
        logger.warning(f"[{server_name}] Disabling server due to failure: {reason}")
        
        # Mark as disabled in Runtime State
        if hasattr(self.state, "toggle_mcp_server"):
             await self.state.toggle_mcp_server(server_name, False, persist=True)  # Now persist to DB
        else:
             # Fallback if method signature doesn't match yet
             self.state.mcp_servers[server_name]["enabled"] = False
             self.state.mcp_servers[server_name]["disabled_reason"] = "discovery_failed"
             
             # Update database immediately (discovery failures are rare, no debouncing needed)
             if hasattr(self.state, "config_manager") and self.state.config_manager:
                 try:
                     config = self.state.mcp_servers[server_name].copy()
                     await self.state.config_manager.update_mcp_server(server_name, config)
                     logger.info(f"[{server_name}] Updated database - disabled due to discovery failure")
                 except Exception as e:
                     logger.warning(f"[{server_name}] Failed to update database: {e}")
             
        # Record in Circuit Breaker
        if hasattr(self.state, "mcp_circuit_breaker"):
            self.state.mcp_circuit_breaker.record_failure(server_name, error=reason)
            
        # Notify
        if hasattr(self.state, "system_event_queue"):
            await self.state.system_event_queue.put({
                "event": {
                    "type": "system_status",
                    "content": f"MCP Server '{server_name}' disabled: {reason}",
                    "severity": "warning"
                },
                "request_id": None,
                "timestamp": time.time()
            })

    async def _discover_single_server(self, server_name: str, cfg: dict, attempt: int = 1, max_attempts: int = 3, disable_on_failure: bool = True) -> bool:
        """Discover tools from a single MCP server with retry logic.
        
        Args:
            server_name: Name of the MCP server
            cfg: Server configuration
            attempt: Current attempt number
            max_attempts: Maximum number of attempts
            disable_on_failure: If True, disable server on failure. If False, only log the failure.
                               Use False for periodic refreshes to avoid disabling servers temporarily.
        
        Returns True if successful, False otherwise.
        """
        from agent_runner.tools.mcp import tool_mcp_proxy
        from agent_runner.constants import CORE_MCP_SERVERS
        
        is_core = server_name in CORE_MCP_SERVERS

        # Fast-path: if already initialized with cached tools, skip rediscovery
        if cfg.get("enabled", True) and server_name in self.mcp_tool_cache and self.state.stdio_process_initialized.get(server_name, False):
            logger.info(f"[{server_name}] Already initialized with cached tools; skipping rediscovery.")
            return True

        # Protect caches: if we already have tools cached for this server, avoid disabling on refresh failures
        effective_disable_on_failure = disable_on_failure
        if server_name in self.mcp_tool_cache:
            effective_disable_on_failure = False

        from agent_runner.tools.mcp import perform_pulse_check, PulseCheckFailed, tool_mcp_proxy # Added imports

        # [DARWINIAN DISCOVERY] Pulse Check
        # Run strict startup check to ensure server is actually viable (has API keys, etc)
        # We only do this on the PRIMARY attempt (attempt 1) to avoid spamming process spawns on retry
        if attempt == 1 and cfg.get("enabled", True):
            try:
                await perform_pulse_check(self.state, server_name, cfg)
            except PulseCheckFailed as e:
                logger.error(f"[Darwinian] Server '{server_name}' FAILED pulse check: {e}")
                if disable_on_failure:
                    await self._disable_failed_server(server_name, f"Darwinian Pulse Check Failed: {e}")
                    return False
                else:
                    logger.warning(f"[{server_name}] Pulse check failed but disable_on_failure=False. Proceeding with caution.")


        
        # [FIX] Intelligent timeout: longer for first attempt, shorter for retries
        # First attempt gets 45s (for locally heavy setups), retries get 30s
        timeout = 45.0 if attempt == 1 else 30.0
        # Core services get extra time
        if is_core and attempt == 1:
            timeout = 60.0
        
        # [FIX] Pre-flight validation
        if attempt == 1:
            # Check if command exists
            cmd = cfg.get("cmd", cfg.get("command"))
            if cmd:
                import shutil
                first_cmd = cmd[0] if isinstance(cmd, list) else cmd
                if not shutil.which(first_cmd):
                    error_msg = f"Command not found: {first_cmd}"
                    logger.error(f"[{server_name}] {error_msg}")
                    if not is_core:
                        await self._disable_failed_server(server_name, error_msg)
                    return False
        
        logger.info(f"[{server_name}] Discovery attempt {attempt}/{max_attempts} (timeout={timeout}s)")
        
        try:
            res = await asyncio.wait_for(
                tool_mcp_proxy(self.state, server_name, "tools/list", {}, bypass_circuit_breaker=True),
                timeout=timeout
            )
            
            # Safety check: ensure res is not None
            if res is None:
                logger.error(f"[{server_name}] tool_mcp_proxy returned None")
                if not is_core and disable_on_failure:
                    await self._disable_failed_server(server_name, "Discovery returned None")
                return False
            
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

                logger.info(f"✅ Discovered {len(defs)} tools from MCP server '{server_name}'")
                
                # [FIX] Explicitly mark healthy so execution doesn't fail later
                current_failures = self.state.mcp_server_health.get(server_name, {}).get("consecutive_failures", 0)
                self.state.mcp_server_health[server_name] = {
                    "healthy": True,
                    "error": None,
                    "last_check": time.time(),
                    "last_success": time.time(),
                    "last_failure": self.state.mcp_server_health.get(server_name, {}).get("last_failure"),
                    "consecutive_failures": 0 
                }
                
                return True
            else:
                error_msg = res.get("error", "Unknown error")
                logger.warning(f"[{server_name}] Discovery returned error: {error_msg}")
                if attempt < max_attempts:
                    # Retry with exponential backoff
                    backoff = min(2.0 ** (attempt - 1), 5.0)  # 1s, 2s, 4s max
                    logger.info(f"[{server_name}] Retrying in {backoff}s...")
                    await asyncio.sleep(backoff)
                    return await self._discover_single_server(server_name, cfg, attempt + 1, max_attempts, disable_on_failure)
                else:
                    # All retries exhausted
                    if not is_core and disable_on_failure:
                        await self._disable_failed_server(server_name, f"Discovery failed after {max_attempts} attempts: {error_msg}")
                    elif is_core:
                        logger.error(f"🚨 CRITICAL: Core service '{server_name}' failed after {max_attempts} attempts: {error_msg}")
                        self.state.mcp_circuit_breaker.record_failure(server_name, weight=1, error=error_msg)
                    return False
                    
        except asyncio.TimeoutError:
            error_msg = f"Discovery timeout ({timeout}s)"
            logger.warning(f"[{server_name}] {error_msg}")
            if attempt < max_attempts:
                # Retry with exponential backoff
                backoff = min(2.0 ** (attempt - 1), 5.0)
                logger.info(f"[{server_name}] Retrying after timeout in {backoff}s...")
                await asyncio.sleep(backoff)
                return await self._discover_single_server(server_name, cfg, attempt + 1, max_attempts)
            else:
                # All retries exhausted
                if not is_core and disable_on_failure:
                    await self._disable_failed_server(server_name, f"{error_msg} after {max_attempts} attempts")
                elif is_core:
                    logger.error(f"🚨 CRITICAL: Core service '{server_name}' {error_msg} after {max_attempts} attempts")
                    self.state.mcp_circuit_breaker.record_failure(server_name, weight=1, error=error_msg)
                return False
                
        except Exception as e:
            error_msg = str(e)
            logger.warning(f"[{server_name}] Discovery exception: {error_msg}", exc_info=True)
            
            # [FIX] Enhanced error logging - capture more context
            import traceback
            error_details = {
                "error": error_msg,
                "traceback": traceback.format_exc(),
                "config": {k: v for k, v in cfg.items() if k != "env"}  # Don't log env vars
            }
            logger.debug(f"[{server_name}] Full error context: {error_details}")
            
            if attempt < max_attempts:
                # Retry with exponential backoff
                backoff = min(2.0 ** (attempt - 1), 5.0)
                logger.info(f"[{server_name}] Retrying after exception in {backoff}s...")
                await asyncio.sleep(backoff)
                return await self._discover_single_server(server_name, cfg, attempt + 1, max_attempts)
            else:
                # All retries exhausted
                if not is_core and effective_disable_on_failure:
                    await self._disable_failed_server(server_name, f"Discovery exception after {max_attempts} attempts: {error_msg}")
                elif is_core:
                    logger.error(f"🚨 CRITICAL: Core service '{server_name}' discovery exception after {max_attempts} attempts: {error_msg}")
                    self.state.mcp_circuit_breaker.record_failure(server_name, weight=1, error=error_msg)
                
                # [Fix] Notify user via Unified Tracking
                try:
                    from common.unified_tracking import track_mcp_event, EventSeverity
                    track_mcp_event(
                        event="mcp_discovery_failed",
                        server=server_name,
                        message=f"Failed to discover tools after {max_attempts} attempts: {error_msg}",
                        severity=EventSeverity.CRITICAL if is_core else EventSeverity.HIGH,
                        error=e,
                        component="executor"
                    )
                except ImportError:
                    pass
                return False

    async def discover_mcp_tools(self):
        """Discover tools from all configured MCP servers with improved error handling and retries."""
        logger.info(f"Starting MCP discovery. Servers: {list(self.state.mcp_servers.keys())}")
        
        # [FIX] Discover servers with limited parallelism to prevent resource exhaustion
        import asyncio
        semaphore = asyncio.Semaphore(1)  # Max 1 concurrent discovery (Sequential Startup to prevent stdio deadlocks)

        # [FIX] Prevent concurrent discovery runs in the same process
        if not hasattr(self.state, "mcp_discovery_lock"):
            self.state.mcp_discovery_lock = asyncio.Lock()
        if self.state.mcp_discovery_lock.locked():
            logger.info("MCP discovery already in progress; skipping duplicate run.")
            return
        await self.state.mcp_discovery_lock.acquire()

        try:
            async def discover_with_semaphore(server_name: str, cfg: dict):
                async with semaphore:
                    return await self._discover_single_server(server_name, cfg)
            
            # Create discovery tasks
            tasks = []
            for server_name in list(self.state.mcp_servers.keys()):
                cfg = self.state.mcp_servers[server_name]
                
                # Skip Disabled Servers
                if not cfg.get("enabled", True):
                    if server_name in self.mcp_tool_cache:
                        del self.mcp_tool_cache[server_name]
                    logger.info(f"Skipping disabled MCP server: {server_name}")
                    continue
                
                tasks.append(discover_with_semaphore(server_name, cfg))
            
            # Execute discoveries in parallel (with semaphore limit)
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                successful = sum(1 for r in results if r is True)
                logger.info(f"MCP Discovery complete: {successful}/{len(tasks)} servers succeeded")
            
            menu_lines = []
            
            from agent_runner.constants import CORE_MCP_SERVERS
            core_servers = CORE_MCP_SERVERS
            
            for srv, tools in self.mcp_tool_cache.items():
                if not tools:
                    continue
                # [FIX] Include ALL servers (including Core) in the menu
                # if srv in core_servers:
                #    continue
                
                # Improve Menu: Include first tool description for context
                desc = ""
                if tools:
                    desc = tools[0]["function"].get("description", "")[:60] + "..."
                
                t_names = [t["function"]["name"] for t in tools[:5]]
                line = f"- Server '{srv}': {desc}\n  Tools: {', '.join(t_names)}"
                menu_lines.append(line)
            
            if menu_lines:
                self.tool_menu_summary = "\n".join(menu_lines)
            else:
                self.tool_menu_summary = "(No external tools available)"
                
            logger.info(f"Generated Maître d' Menu: {self.tool_menu_summary}")
            
            # [FEATURE REQUEST]: Formally track all functions.
            # We persist the full registry to disk so the Agent can "read about itself".
            try:
                registry_path = os.path.join(self.state.agent_fs_root, "system", "tool_registry.json")
                os.makedirs(os.path.dirname(registry_path), exist_ok=True)
                
                full_registry = {
                    "timestamp": time.time(),
                    "native_tools": self.tool_definitions,
                    "mcp_tools": self.mcp_tool_cache
                }
                
                with open(registry_path, "w") as f:
                    json.dump(full_registry, f, indent=2)
                    
                logger.info(f"Persisted Tool Registry to {registry_path}")
            except Exception as e:
                logger.warning(f"Failed to persist tool registry: {e}")

        finally:
            # Release discovery lock
            if hasattr(self.state, "mcp_discovery_lock") and self.state.mcp_discovery_lock.locked():
                self.state.mcp_discovery_lock.release()

    async def _analyze_query_with_router(self, user_query: str, messages: List[Dict[str, Any]], quality_tier: Optional['QualityTier'] = None) -> Optional[Any]:
        """Pre-analyze query with router for parallel processing."""
        try:
            from agent_runner.router_analyzer import analyze_query
            import httpx

            async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as http_client:
                return await analyze_query(
                    query=user_query,
                    messages=messages,
                    gateway_base=self.state.gateway_base,
                    http_client=http_client,
                    available_tools=[],  # Will be filled in later
                    available_models=getattr(self.state, 'available_models', [])
                )
        except Exception as e:
            logger.debug(f"Parallel router analysis failed: {e}")
            return None

    async def get_capability_based_tools(self, query: str, quality_tier: Optional['QualityTier'] = None) -> Dict[str, Any]:
        """
        Get tools based on capability detection for a query.
        Returns capability analysis and recommended tool categories/tools.
        """
        # Detect capabilities in the query
        detected_capabilities = detect_query_capabilities(query)

        if not detected_capabilities:
            # Fallback to minimal tool set if no capabilities detected
            return {
                "capabilities": {},
                "categories": ["core", "thinking", "exploration", "admin"],
                "priority_tools": [],
                "confidence_breakdown": {},
                "tool_selection": [],
                "quality_tier": "fallback",
                "conflicts_resolved": False
            }

        # Resolve capability conflicts to prevent resource competition
        capabilities = resolve_capability_conflicts(detected_capabilities)

        # Log conflict resolution if any changes were made
        if capabilities != detected_capabilities:
            resolved_count = len(capabilities)
            original_count = len(detected_capabilities)
            logger.info(f"⚖️ Resolved capability conflicts: {original_count} → {resolved_count} capabilities")

        # Get quality tier configuration
        max_tools = 50  # Default
        quality_tier_name = "balanced"  # Default

        if quality_tier:
            from agent_runner.quality_tiers import get_tier_config
            tier_config = get_tier_config(quality_tier)
            max_tools = tier_config.get("max_tools", 50)
            quality_tier_name = quality_tier.name.lower()

        # Get tool recommendations with enhanced priority selection
        tool_recommendations = get_tools_for_capabilities(
            capabilities,
            max_tools=max_tools,
            quality_tier=quality_tier_name
        )

        # Add conflict resolution metadata
        tool_recommendations["conflicts_resolved"] = capabilities != detected_capabilities
        tool_recommendations["original_capabilities"] = detected_capabilities

        return tool_recommendations

    async def get_all_tools(self, messages: Optional[List[Dict[str, Any]]] = None, precomputed_intent: Optional[Dict[str, Any]] = None, quality_tier: Optional['QualityTier'] = None, precomputed_router_analysis: Optional[Any] = None, capability_analysis: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Combine built-in tools with discovered MCP tools, filtering by Intent Menu via Context Diet.
        
        Args:
            precomputed_intent: If provided, use this instead of classifying again (for parallelism)
        """
        # [CONTEXT-DIET] Start with minimal core set
        # Always include CORE (Time/Location), THINKING (Internal Monologue), and EXPLORATION (self-awareness tools)
        tools = []
        tools.extend(self.tool_categories.get("core", []))
        tools.extend(self.tool_categories.get("thinking", []))
        tools.extend(self.tool_categories.get("memory", []))
        # Always include exploration tools (get_component_map, get_active_configuration, get_llm_roles) so AI can answer questions about itself
        tools.extend(self.tool_categories.get("exploration", []))
        # Always include admin tools for system introspection and configuration
        tools.extend(self.tool_categories.get("admin", []))
                
        target_servers = set()
        capability_analysis = None

        if precomputed_intent:
            # [OPTIMIZATION] Use precomputed intent result (from parallel execution)
            target_servers = set(precomputed_intent.get("target_servers", []))
        elif messages:
            last_user_msg = next((m for m in reversed(messages) if m.get("role") == "user"), None)
            if last_user_msg:
                query_text = str(last_user_msg.get("content", ""))

                # [CAPABILITY ENHANCEMENT] Use precomputed capability analysis if available
                if not capability_analysis:
                    capability_analysis = await self.get_capability_based_tools(query_text, quality_tier)

                # Use capability-based categories as additional target servers
                capability_categories = set(capability_analysis.get("categories", []))
                target_servers.update(capability_categories)

                # [LEGACY] Also run Maître d' intent classification for backward compatibility
                from agent_runner.intent import classify_search_intent
                intent_res = await classify_search_intent(query_text, self.state, self.tool_menu_summary)
                target_servers.update(set(intent_res.get("target_servers", [])))

                logger.info(f"🎯 CAPABILITY ANALYSIS: {len(capability_analysis.get('capabilities', {}))} capabilities detected, {len(target_servers)} target servers")
        else:
            # BROAD DISCOVERY: If no messages, expose EVERYTHING (for external MCP clients/Cursor)
            target_servers = set(self.mcp_tool_cache.keys())
            # Also expose all system categories for broad discovery
            target_servers.add("filesystem")
            target_servers.add("system")
            target_servers.add("admin")
            target_servers.add("memory")
            target_servers.add("cleanup")
            
        # [CONTEXT-DIET] Dynamic Category Loading based on Maître d' Request + Capability Analysis
        # Priority loading based on capability detection
        if capability_analysis:
            # Load categories detected by capability analysis first (higher priority)
            capability_categories = capability_analysis.get("categories", [])
            for category in capability_categories:
                if category in self.tool_categories and category not in ["core", "thinking", "exploration", "admin", "memory"]:
                    tools.extend(self.tool_categories.get(category, []))
                    logger.debug(f"Loaded capability-detected category: {category}")
        
        # [FIX] Deduplicate tools by name to prevent Context Window pollution
        unique_tools = {}
        for t in tools:
            t_name = t.get("function", {}).get("name")
            if t_name and t_name not in unique_tools:
                unique_tools[t_name] = t
        tools = list(unique_tools.values())

        
        # [FEATURE: SYSTEM AWARENESS] Inject Context Tags
        # We classify tools by origin (Local vs Remote) to help Agent reasoning.
        def _tag_tools(tool_list: List[Dict[str, Any]], tag: str) -> List[Dict[str, Any]]:
            tagged = []
            for t in tool_list:
                # Deep copy to avoid mutating cache
                if not t: continue
                new_t = t.copy()
                if "function" in new_t:
                    new_t["function"] = new_t["function"].copy()
                    desc = new_t["function"].get("description", "")
                    # Prevent double tagging
                    if not desc.startswith("["):
                        new_t["function"]["description"] = f"{tag} {desc}"
                tagged.append(new_t)
            return tagged

        # Legacy Maître d' based loading (fallback/compatibility)
        if "filesystem" in target_servers:
            tools.extend(_tag_tools(self.tool_categories.get("filesystem", []), "[LOCAL SYSTEM]"))
            tools.extend(_tag_tools(self.tool_categories.get("cleanup", []), "[LOCAL SYSTEM]"))

        if "system" in target_servers or "admin" in target_servers:
             tools.extend(_tag_tools(self.tool_categories.get("system", []), "[LOCAL SYSTEM]"))
             tools.extend(_tag_tools(self.tool_categories.get("admin", []), "[LOCAL SYSTEM]"))
             
             # Also add Graph tools if system/admin is requested, or if "graph" is explicit
             if "graph" in target_servers or "system" in target_servers:
                 tools.extend(_tag_tools(self.tool_categories.get("graph", []), "[VISUALIZATION]"))

        if "memory" in target_servers or "project-memory" in target_servers:
             # Memory is internal but safe, maybe [MEMORY] tag? For now leave generic or [INTERNAL]
             tools.extend(_tag_tools(self.tool_categories.get("memory", []), "[INTERNAL MEMORY]"))
                
        for server_name, server_tools in self.mcp_tool_cache.items():
            server_cfg = self.state.mcp_servers.get(server_name, {})
            
            # [FIX] Filter out disabled servers - don't expose their tools to LLM
            if not server_cfg.get("enabled", True):
                continue  # Skip disabled servers
            
            if server_cfg.get("requires_internet") and not self.state.internet_available:
                continue

            from agent_runner.constants import CORE_MCP_SERVERS
            is_core = server_name in CORE_MCP_SERVERS
            if is_core or (server_name in target_servers):
                # MCP Tools are harder to classify. Core ones like 'fetch' are REMOTE.
                # Project-specific ones might be Local.
                # For now, we default to [MCP] to distinguish them.
                # If specific server is known, we could tag better.
                tag = "[MCP]"
                if server_name in ["fetch", "tavily-search", "github"]:
                    tag = "[REMOTE]"
                elif server_name in ["postgres", "filesystem-mcp"]: # hypothetical
                    tag = "[LOCAL SYSTEM]"
                
                # Wrap and Tag
                tagged_mcp = _tag_tools(server_tools, tag)
                
                for t in tagged_mcp:
                    orig_func = t.get("function", {})
                    wrapped = {
                        "type": "function",
                        "function": {
                            "name": f"mcp__{server_name}__{orig_func.get('name')}",
                            "description": orig_func.get("description"), # Already tagged by helper
                            "parameters": orig_func.get("parameters")
                        }
                    }
                    tools.append(wrapped)

        # [CAPABILITY ENHANCEMENT] Advanced priority-based tool selection
        if capability_analysis:
            priority_tools = capability_analysis.get("priority_tools", [])
            tool_priority_scores = capability_analysis.get("tool_priority_scores", {})

            if priority_tools or tool_priority_scores:
                # Enhanced prioritization using confidence scores
                tool_priority_map = {}

                # Assign priority scores to tools
                for tool in tools:
                    func_name = tool.get("function", {}).get("name", "")
                    priority_score = 0

                    # Direct priority tool match (highest priority)
                    for priority_tool in priority_tools:
                        if priority_tool in func_name:
                            priority_score = max(priority_score, 100)  # High priority

                    # Confidence-based scoring
                    for scored_tool, score in tool_priority_scores.items():
                        if scored_tool in func_name:
                            priority_score = max(priority_score, score * 50)  # Scale to 0-50 range

                    tool_priority_map[func_name] = priority_score

                # Sort tools by priority score (highest first)
                tools.sort(key=lambda t: tool_priority_map.get(t.get("function", {}).get("name", ""), 0), reverse=True)

                # Log prioritization results
                high_priority_count = sum(1 for score in tool_priority_map.values() if score > 50)
                if high_priority_count > 0:
                    logger.info(f"🎯 Prioritized {high_priority_count} high-priority tools, {len(tools)} total tools available")

        # SEMANTIC TOOL FILTERING: Use Router Analyzer for intelligent selection
        logger.info(f"🔍 ROUTER ANALYZER: Checking conditions - messages: {len(messages) if messages else 0}, quality_tier: {quality_tier}, MAXIMUM: {QualityTier.MAXIMUM}")
        if False and messages and quality_tier != QualityTier.MAXIMUM:  # [TUNING] Disabled for Latency (Formula 1 Mode)
            try:
                logger.info(f"🔍 ROUTER ANALYZER: Starting semantic tool filtering for {len(tools)} tools")
                from agent_runner.router_analyzer import analyze_query, filter_tools_by_router_analysis

                # Get semantic analysis of the query
                user_query = messages[-1].get("content", "") if messages else ""
                if user_query:  # Only analyze if we have a query
                    # Use precomputed router analysis if available (parallel processing optimization)
                    if precomputed_router_analysis:
                        logger.info("Using precomputed router analysis (parallel processing)")
                        router_analysis = precomputed_router_analysis
                    else:
                        logger.info(f"🔍 ROUTER ANALYZER: Analyzing query: '{user_query[:50]}...'")

                        # Create HTTP client for router analyzer
                        import httpx
                        async with httpx.AsyncClient(timeout=httpx.Timeout(25.0)) as http_client:
                            router_analysis = await analyze_query(
                                query=user_query,
                                messages=messages,
                                gateway_base=self.state.gateway_base,
                                http_client=http_client,
                                available_tools=tools,
                                available_models=getattr(self.state, 'available_models', [])
                            )

                    # Apply intelligent filtering based on semantic analysis
                    original_count = len(tools)
                    tools = filter_tools_by_router_analysis(
                        all_tools=tools,
                        router_analysis=router_analysis,
                        mode="moderate",  # Balanced approach
                        min_confidence=0.7,
                        max_tools_aggressive=8,   # Very selective when high confidence
                        max_tools_moderate=15     # Reasonable limit when category-based
                    )

                    reduction = original_count - len(tools)
                    if reduction > 0:
                        logger.info(
                            "semantic_tool_filtering",
                            extra={
                                "original_tools": original_count,
                                "filtered_tools": len(tools),
                                "reduction": reduction,
                                "confidence": router_analysis.confidence,
                                "categories": router_analysis.tool_categories,
                                "recommended_tools": router_analysis.recommended_tools[:5]  # Log first 5
                            }
                        )

            except Exception as e:
                logger.warning(f"Router analyzer failed, implementing enhanced fallback: {e}")

                # Enhanced error recovery strategy
                fallback_applied = False
                try:
                    # Strategy 1: Try cached analysis for similar queries
                    cached_fallback = await self._get_cached_router_analysis_for_similar_query(user_query)
                    if cached_fallback:
                        logger.info("Using cached router analysis as fallback")
                        tools = filter_tools_by_router_analysis(
                            all_tools=tools,
                            router_analysis=cached_fallback,
                            mode="moderate",
                            min_confidence=0.6,  # Lower threshold for cached results
                            max_tools_aggressive=10,
                            max_tools_moderate=20
                        )
                        reduction = original_count - len(tools)
                        if reduction > 0:
                            logger.info(f"Applied cached semantic filtering: {original_count} → {len(tools)} tools")
                        fallback_applied = True

                    # Strategy 2: Keyword-based filtering as intelligent fallback
                    if not fallback_applied:
                        keyword_filtered_tools = self._filter_tools_by_keywords(user_query, tools)
                        if len(keyword_filtered_tools) < len(tools):
                            logger.info(f"Applied keyword-based filtering: {len(tools)} → {len(keyword_filtered_tools)} tools")
                            tools = keyword_filtered_tools
                            fallback_applied = True

                    # Strategy 3: Domain-specific filtering
                    if not fallback_applied:
                        domain_filtered_tools = self._filter_tools_by_domain(user_query, tools)
                        if len(domain_filtered_tools) < len(tools):
                            logger.info(f"Applied domain-based filtering: {len(tools)} → {len(domain_filtered_tools)} tools")
                            tools = domain_filtered_tools
                            fallback_applied = True

                except Exception as fallback_error:
                    logger.error(f"All fallback strategies failed: {fallback_error}")

                # Final fallback: Continue with numeric filtering as safety net
                logger.info("Using numeric filtering as final fallback")

        # Apply quality tier filtering (safety net)
        if quality_tier is not None:
            tier_config = get_tier_config(quality_tier)
            tool_config = tier_config.get("tool_filtering", {})
            max_tools = tool_config.get("max_tools", self.state.max_tool_count)  # Default to maximum

            # Apply max_tools limit
            if len(tools) > max_tools:
                tools = tools[:max_tools]

        return tools

    async def execute_tool_call(self, tool_call: Dict[str, Any], request_id: Optional[str] = None, user_query: str = "") -> Dict[str, Any]:
        fn = tool_call.get("function") or {}
        name = fn.get("name")
        args_str = fn.get("arguments") or "{}"
        
        # Parse arguments for security check
        try:
            if isinstance(args_str, str):
                args_dict = json.loads(args_str)
            else:
                args_dict = args_str
        except json.JSONDecodeError:
            args_dict = {}
        
        # Extract password if provided (for admin tools)
        password = args_dict.pop("password", None) if isinstance(args_dict, dict) else None

        # Phase 3: Structured tool validation (Pydantic-style)
        if name and not str(name).startswith("mcp__"):
            if not isinstance(args_dict, dict):
                return {"ok": False, "error": "Tool arguments must be a JSON object"}
            validation_error = self._validate_tool_args(name, args_dict)
            if validation_error:
                return {"ok": False, "error": validation_error}
        
        # Check security before execution (including MCP proxy tools)
        from agent_runner.tools.system import check_tool_security
        
        # For MCP proxy tools, extract server name for security check
        if name and str(name).startswith("mcp__"):
            # MCP tools: check if server requires admin (future: server-level config)
            # For now, allow MCP tools but log for audit
            logger.debug(f"MCP proxy tool call: {name} (security check deferred to server level)")
        else:
            # Built-in tools: check security
            security_check = await check_tool_security(self.state, name, password)
            
            if not security_check["allowed"]:
                return {
                    "ok": False,
                    "error": f"Access Denied: {security_check['reason']}",
                    "requires_admin": security_check.get("requires_admin", False),
                    "hint": security_check.get("hint", "")
                }
        
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
                    
                    # [PHASE 3] Use cache for deterministic tools
                    tool_full_name = f"{server}_{tool}"
                    
                    async def execute_mcp_tool():
                        from agent_runner.tools.mcp import tool_mcp_proxy
                        return await tool_mcp_proxy(self.state, server, tool, args)
                    
                    result = await self.mcp_response_cache.get_or_execute(
                        tool_name=tool_full_name,
                        arguments=args,
                        executor_func=execute_mcp_tool,
                        ttl=300.0  # 5 minutes
                    )
                    
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
                        # Record tool success for maître d' learning system
                        success = result.get("ok", False)
                        if success and user_query and len(user_query.strip()) > 3:
                            from agent_runner.feedback import record_tool_success

                            # Skip core servers that are always available
                            if server not in ["project-memory", "location", "thinking", "system-control"]:
                                await record_tool_success(user_query.strip(), server, state=self.state)
                                logger.debug(f"Maître d' learned: '{user_query[:40]}...' → {server}")
                    except Exception as e:
                        logger.debug(f"Failed to record maître d' learning: {e}")

                    return result
                except Exception as e:
                    import traceback
                    logger.error(f"MCP PROXY CRASH: {traceback.format_exc()}")
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
            # [REGISTRY LOOKUP] Fallback: Check if this is a known MCP tool (Clean Name Routing)
            # This enables Vector Search results (which return clean names) to be executed correctly.
            found_server = None
            
            # 1. Fast Lookup (Optimization would be a separate dict, but iteration is fine for <1000 tools)
            for server_name, tools in self.mcp_tool_cache.items():
                for t in tools:
                    if t["function"]["name"] == name:
                        found_server = server_name
                        break
                if found_server:
                    break
            
            if found_server:
                # ROUTING SUCCESS: We found the server for this tool.
                # Now we recursively call ourselves (or specific proxy logic) with the resolved route.
                # But since we are already inside execute_tool_call, let's just use the logic above.
                # Construct a "Prefixed" name to trigger the MCP Logic Block? 
                # OR just call tool_mcp_proxy directly here. Calling proxy is cleaner.
                
                logger.info(f"🔄 Registry Routing: '{name}' -> '{found_server}'")
                
                try:
                    # Parse args if likely string
                    parsed_args = {}
                    if isinstance(args_str, str):
                        try:
                            parsed_args = json.loads(args_str)
                        except:
                            parsed_args = {}
                    elif isinstance(args_str, dict):
                        parsed_args = args_str

                    from agent_runner.tools.mcp import tool_mcp_proxy
                    return await tool_mcp_proxy(self.state, found_server, name, parsed_args)
                except Exception as e:
                    return {"ok": False, "error": f"Routed Execution Failed: {e}"}

            # If still not found, then it effectively doesn't exist.
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
            import traceback
            logger.error(f"LOCAL TOOL CRASH ({name}): {traceback.format_exc()}")
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

    def _validate_tool_args(self, name: str, args: Dict[str, Any]) -> Optional[str]:
        """
        Lightweight validation of tool args against known JSON schema (native + MCP).
        Returns an error string if validation fails, otherwise None.
        """
        schema = self._find_tool_schema(name)
        if not schema:
            return None  # No schema available -> skip validation

        required = schema.get("required", [])
        properties = schema.get("properties", {})

        for req_field in required:
            if req_field not in args:
                return f"Missing required parameter: '{req_field}'"

        # Best-effort type checks
        for field, spec in properties.items():
            if field in args and isinstance(spec, dict):
                expected_type = spec.get("type")
                if expected_type == "string" and not isinstance(args[field], str):
                    return f"Parameter '{field}' must be a string"
                if expected_type == "integer" and not isinstance(args[field], int):
                    return f"Parameter '{field}' must be an integer"
                if expected_type == "number" and not isinstance(args[field], (int, float)):
                    return f"Parameter '{field}' must be a number"
                if expected_type == "boolean" and not isinstance(args[field], bool):
                    return f"Parameter '{field}' must be a boolean"

        return None

    def _find_tool_schema(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Locate the JSON schema for a tool by name from native tool definitions or MCP cache.
        """
        # Native tool definitions
        for t in self.tool_definitions:
            fn = t.get("function", {})
            if fn.get("name") == name:
                return fn.get("parameters", {})

        # MCP tool definitions
        for tools in self.mcp_tool_cache.values():
            for t in tools or []:
                fn = t.get("function", {})
                if fn.get("name") == name:
                    return fn.get("parameters", {})

        return None

    async def tool_knowledge_search(self, state: AgentState, query: str, kb_id: str = "default", filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Query the RAG server for deep content."""
        from agent_runner.constants import DEFAULT_RAG_URL, DEFAULT_RAG_QUERY_PATH
        
        # Get RAG URL from config or use default
        rag_base = state.config.get("rag", {}).get("url", DEFAULT_RAG_URL)
        rag_url = f"{rag_base.rstrip('/')}{DEFAULT_RAG_QUERY_PATH}"
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
        from agent_runner.constants import DEFAULT_RAG_URL, DEFAULT_RAG_INGEST_PATH
        
        # Get RAG URL from config or use default
        rag_base = state.config.get("rag", {}).get("url", DEFAULT_RAG_URL)
        rag_url = f"{rag_base.rstrip('/')}{DEFAULT_RAG_INGEST_PATH}"
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

    async def _get_cached_router_analysis_for_similar_query(self, query: str):
        """Get cached router analysis for similar queries as fallback."""
        try:
            # Simple similarity check - look for queries with same key terms
            key_terms = set(query.lower().split()[:3])  # First 3 words

            # This is a simplified implementation - in production, you'd want
            # a more sophisticated similarity algorithm and proper cache
            # For now, return None to trigger other fallbacks
            return None

        except Exception as e:
            logger.debug(f"Cache similarity check failed: {e}")
            return None

    def _filter_tools_by_keywords(self, query: str, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter tools based on keyword matching in query."""
        query_lower = query.lower()
        filtered_tools = []

        # Define keyword mappings to tool categories
        keyword_mappings = {
            'file': ['filesystem', 'file'],
            'directory': ['filesystem', 'file'],
            'list': ['filesystem', 'file'],
            'read': ['filesystem', 'file'],
            'write': ['filesystem', 'file'],
            'search': ['search', 'web_search'],
            'find': ['search', 'filesystem'],
            'weather': ['weather'],
            'time': ['system', 'utility'],
            'date': ['system', 'utility'],
            'run': ['system', 'execution'],
            'execute': ['system', 'execution'],
            'code': ['code', 'programming'],
            'python': ['code', 'programming'],
            'memory': ['memory', 'knowledge'],
            'remember': ['memory', 'knowledge'],
            'recall': ['memory', 'knowledge']
        }

        # Find relevant categories
        relevant_categories = set()
        for keyword, categories in keyword_mappings.items():
            if keyword in query_lower:
                relevant_categories.update(categories)

        # If no keywords found, return all tools (no filtering)
        if not relevant_categories:
            return tools

        # Filter tools by category
        for tool in tools:
            tool_name = tool.get('function', {}).get('name', '').lower()
            tool_desc = tool.get('function', {}).get('description', '').lower()

            # Check if tool matches relevant categories
            for category in relevant_categories:
                if category in tool_name or category in tool_desc:
                    filtered_tools.append(tool)
                    break

        # If no tools matched, return a reasonable subset (top 15)
        if not filtered_tools:
            filtered_tools = tools[:15]

        return filtered_tools

    def _filter_tools_by_domain(self, query: str, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter tools based on query domain analysis."""
        query_lower = query.lower()

        # Domain detection
        if any(word in query_lower for word in ['file', 'directory', 'read', 'write', 'list']):
            # File system domain
            domain_tools = [t for t in tools if 'file' in t.get('function', {}).get('name', '').lower()]
            return domain_tools[:12] if domain_tools else tools[:12]

        elif any(word in query_lower for word in ['search', 'find', 'look']):
            # Search domain
            domain_tools = [t for t in tools if 'search' in t.get('function', {}).get('name', '').lower()]
            return domain_tools[:10] if domain_tools else tools[:10]

        elif any(word in query_lower for word in ['weather', 'temperature', 'forecast']):
            # Weather domain
            domain_tools = [t for t in tools if 'weather' in t.get('function', {}).get('name', '').lower()]
            return domain_tools[:5] if domain_tools else tools[:5]

        elif any(word in query_lower for word in ['run', 'execute', 'code']):
            # Execution domain
            domain_tools = [t for t in tools if any(x in t.get('function', {}).get('name', '').lower()
                                                   for x in ['run', 'execute', 'code'])]
            return domain_tools[:8] if domain_tools else tools[:8]

        # Default: return top tools
        return tools[:15]

    async def tool_get_graph_snapshot(self, limit: int = 100, format: str = "json") -> Dict[str, Any]:
        """Tool wrapper for GraphService.get_graph_snapshot."""
        if not hasattr(self.state, "graph"):
            return {"error": "GraphService not initialized"}
            
        if format == "mermaid":
            diagram = await self.state.graph.render_mermaid()
            return {"diagram": diagram}
            
        return await self.state.graph.get_graph_snapshot(limit=limit)
