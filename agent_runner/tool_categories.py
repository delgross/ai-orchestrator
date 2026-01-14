"""
Tool Category Definitions and Utilities

Provides centralized tool categorization for better LLM tool selection.
Also includes capability-based query classification for intelligent tool selection.
"""

from typing import Dict, List, Optional, Any, Set
import re

# Valid tool categories
VALID_CATEGORIES = {
    "web_search", "filesystem", "code", "browser", "memory",
    "scraping", "automation", "http", "weather", "document", "ollama",
    "system", "status", "control", "exploration", "thinking", "knowledge",
    "admin", "introspection", "latency", "node", "mcp", "data_processing",
    "security", "api_integration", "workflow_automation"
}

# Category hierarchy for better organization
CATEGORY_HIERARCHY = {
    "filesystem": {
        "read": ["read_text", "path_info", "list_dir", "find_files"],
        "write": ["write_text", "append_text", "make_dir"],
        "manage": ["remove_file", "remove_dir", "move_path", "copy_file", "copy_path", "batch_operations"],
        "watch": ["watch_path", "query_static_resources"]
    },
    "system": {
        "status": ["get_system_status", "get_memory_status", "get_ingestion_status", "get_service_status",
                   "get_circuit_breaker_status", "get_background_tasks_status", "get_task_health",
                   "get_registry_health", "get_mcp_server_status", "get_system_diagnostics",
                   "get_detailed_system_status", "get_system_metrics", "check_system_health"],
        "control": ["set_system_config", "restart_agent", "pause_ingestion", "resume_ingestion",
                    "clear_ingestion_problem", "reset_circuit_breaker", "reset_all_circuit_breakers",
                    "toggle_mcp_server", "reset_mcp_servers", "reload_mcp_servers", "trigger_memory_consolidation",
                    "trigger_backup", "update_model_config", "set_mode", "manage_secret",
                    "add_mcp_server", "remove_mcp_server", "install_mcp_package"],
        "exploration": ["list_all_available_tools", "get_system_prompt", "get_memory_facts",
                       "get_llm_roles", "get_component_map", "get_active_configuration",
                       "list_system_toggles", "get_system_config"]
    },
    "thinking": {
        "core": ["sequential_thinking", "get_thinking_history", "store_thinking_result"],
        "advanced": ["start_thinking_session", "start_thinking_branch", "get_thinking_progress",
                     "analyze_thinking_efficiency", "repair_thinking_session"]
    },
    "knowledge": {
        "search": ["search", "knowledge_search", "semantic_search"],
        "ingest": ["ingest_knowledge", "ingest_file"],
        "memory": ["memory_store_fact", "memory_query_facts", "memory_search_semantic", "memory_consolidate", "remove_memory_from_file", "run_memory_consolidation"]
    },
    "data_processing": {
        "parsing": ["parse_json", "parse_csv"],
        "transformation": ["transform_data"],
        "reporting": ["generate_report"]
    },
    "security": {
        "passwords": ["generate_password", "validate_password_strength"],
        "cryptography": ["hash_string", "generate_token"]
    },
    "api_integration": {
        "http": ["http_request", "api_health_check"],
        "webhooks": ["create_webhook", "call_webhook"],
        "parsing": ["parse_api_response"]
    },
    "workflow_automation": {
        "workflows": ["create_workflow", "execute_workflow"],
        "scheduling": ["schedule_task", "list_scheduled_tasks", "cancel_scheduled_task"],
        "pipelines": ["create_pipeline"]
    },
    "vector_tool_retrieval": {
        "search": ["vector_tool_search"],
        "analysis": ["compare_retrieval_methods"],
        "hybrid": ["hybrid_tool_retrieval"]
    },
    "admin": {
        "session": ["unlock_session", "check_admin_status"],
        "policy": ["set_policy", "sentinel_authorize"],
        "triggers": ["register_trigger", "remove_trigger", "list_triggers"]
    }
}

# Tool name to category mapping (comprehensive)
TOOL_CATEGORY_MAP = {
    # Filesystem
    "list_dir": "filesystem",
    "path_info": "filesystem",
    "read_text": "filesystem",
    "write_text": "filesystem",
    "append_text": "filesystem",
    "make_dir": "filesystem",
    "remove_file": "filesystem",
    "remove_dir": "filesystem",
    "move_path": "filesystem",
    "copy_file": "filesystem",
    "copy_path": "filesystem",
    "find_files": "filesystem",
    "batch_operations": "filesystem",
    "watch_path": "filesystem",
    "query_static_resources": "filesystem",
    
    # System Status
    "get_system_status": "status",
    "get_memory_status": "status",
    "get_ingestion_status": "status",
    "get_service_status": "status",
    "get_circuit_breaker_status": "status",
    "get_background_tasks_status": "status",
    "get_task_health": "status",
    "get_registry_health": "status",
    "get_mcp_server_status": "status",
    "get_system_diagnostics": "status",
    "get_detailed_system_status": "status",
    "get_system_metrics": "status",
    "check_system_health": "status",
    "get_system_dashboard": "status",
    "get_system_warnings": "status",
    
    # System Control
    "set_system_config": "control",
    "restart_agent": "control",
    "pause_ingestion": "control",
    "resume_ingestion": "control",
    "clear_ingestion_problem": "control",
    "reset_circuit_breaker": "control",
    "reset_all_circuit_breakers": "control",
    "toggle_mcp_server": "control",
    "reset_mcp_servers": "control",
    "reload_mcp_servers": "control",
    "add_mcp_server": "control",
    "remove_mcp_server": "control",
    "install_mcp_package": "control",
    "trigger_memory_consolidation": "control",
    "trigger_backup": "control",
    "update_model_config": "control",
    "set_mode": "control",
    "manage_secret": "control",
    "save_model_preset": "control",
    "load_model_preset": "control",
    "list_model_presets": "control",
    
    # Exploration
    "list_all_available_tools": "exploration",
    "get_system_prompt": "exploration",
    "get_memory_facts": "exploration",
    "get_llm_roles": "exploration",
    "get_component_map": "exploration",
    "get_active_configuration": "exploration",
    "list_system_toggles": "exploration",
    "get_system_config": "exploration",
    
    # Thinking
    "sequential_thinking": "thinking",
    "get_thinking_history": "thinking",
    "store_thinking_result": "thinking",
    "start_thinking_session": "thinking",
    "start_thinking_branch": "thinking",
    "get_thinking_progress": "thinking",
    "analyze_thinking_efficiency": "thinking",
    "repair_thinking_session": "thinking",
    
    # Knowledge
    "search": "knowledge",
    "knowledge_search": "knowledge",
    "ingest_knowledge": "knowledge",
    "ingest_file": "knowledge",
    "remove_memory_from_file": "knowledge",
    "run_memory_consolidation": "knowledge",
    "memory_store_fact": "memory",
    "memory_query_facts": "memory",
    "memory_search_semantic": "memory",
    "memory_consolidate": "memory",
    
    # Admin
    "unlock_session": "admin",
    "check_admin_status": "admin",
    "set_policy": "admin",
    "sentinel_authorize": "admin",
    "register_trigger": "admin",
    "remove_trigger": "admin",
    "list_triggers": "admin",
    
    # Latency
    "run_latency_tests": "latency",
    "investigate_system_performance": "latency",
    
    # Node
    "run_node": "node",
    "run_npm": "node",
    
    # MCP
    "mcp_proxy": "mcp",
    "import_mcp_config": "mcp",
    
    # System
    "run_command": "code",
    "trigger_task": "code",
    "report_missing_tool": "code",
    
    # Registry
    "registry_list": "admin",
    "registry_read": "admin",
    "registry_write": "admin",
    "registry_append": "admin",
    "registry_manage": "admin",
    
    # Web
    "search_web": "web_search",
}

# Category synonyms for flexible matching
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
    "status": ["health", "check", "monitor", "diagnostics"],
    "control": ["set", "update", "trigger", "manage", "configure"],
    "exploration": ["list", "get", "read", "query", "inspect"],
    "thinking": ["reason", "analyze", "plan", "think"],
    "knowledge": ["search", "memory", "fact", "ingest"],
    "admin": ["admin", "manage", "policy", "trigger", "inspect", "analyze", "evaluate"],
}

# ============================================================================
# CAPABILITY TAXONOMY - Expanded Query Classification System
# ============================================================================

# Core capabilities with detection patterns and tool mappings
CAPABILITY_TAXONOMY = {
    # Information Retrieval & Research
    "web_search": {
        "description": "Current events, news, real-time information, research queries",
        "keywords": ["news", "current", "latest", "today", "breaking", "headlines", "what happened",
                    "recent", "update", "search", "find", "lookup", "research", "widespread", "rioting"],
        "categories": ["web_search"],
        "priority_tools": ["tavily-search", "brave-search"],
        "confidence_boost": 0.8
    },
    "research": {
        "description": "Academic research, citations, scholarly queries",
        "keywords": ["academic", "research", "paper", "study", "citation", "scholarly", "journal",
                    "literature", "evidence", "source", "reference", "bibliography"],
        "categories": ["web_search", "document"],
        "priority_tools": ["academic_search", "citation_formatter"],
        "confidence_boost": 0.7
    },

    # Memory & Knowledge Management
    "memory": {
        "description": "Previous conversations, stored facts, user preferences, recall",
        "keywords": ["remember", "recall", "previous", "before", "conversation", "discussed",
                    "stored", "preference", "history", "what did we", "do you remember"],
        "categories": ["memory"],
        "priority_tools": ["memory_query_facts", "memory_search_semantic"],
        "confidence_boost": 0.9
    },

    # Code Execution & Development
    "code_execution": {
        "description": "Running scripts, commands, code execution, development tasks",
        "keywords": ["run", "execute", "script", "command", "compile", "build", "install",
                    "terminal", "shell", "bash", "python", "npm", "pip"],
        "categories": ["code", "node"],
        "priority_tools": ["run_command", "run_node", "run_npm"],
        "confidence_boost": 0.8
    },

    # File System Operations
    "file_access": {
        "description": "Reading, writing, listing, managing files and directories",
        "keywords": ["file", "directory", "folder", "list", "read", "write", "create", "delete",
                    "copy", "move", "find", "search files", "save", "open"],
        "categories": ["filesystem"],
        "priority_tools": ["list_dir", "read_text", "write_text", "find_files"],
        "confidence_boost": 0.8
    },

    # System Administration & Management
    "system_admin": {
        "description": "System configuration, health checks, service management",
        "keywords": ["status", "health", "config", "restart", "system", "service", "monitor",
                    "diagnostics", "performance", "memory", "cpu", "disk"],
        "categories": ["status", "control", "system"],
        "priority_tools": ["get_system_status", "restart_agent", "check_system_health"],
        "confidence_boost": 0.7
    },

    # Data Analysis & Processing
    "data_analysis": {
        "description": "Statistical analysis, data processing, calculations, visualizations",
        "keywords": ["analyze", "statistics", "data", "calculate", "chart", "graph", "average",
                    "sum", "count", "percentage", "trend", "correlation", "excel", "spreadsheet"],
        "categories": ["code", "filesystem"],
        "priority_tools": ["data_analysis", "statistical_functions"],
        "confidence_boost": 1.1
    },

    # Creative Content Generation
    "creative": {
        "description": "Writing, brainstorming, content creation, creative tasks",
        "keywords": ["write", "create", "brainstorm", "content", "story", "article", "blog",
                    "marketing", "copy", "creative", "design", "idea", "generate"],
        "categories": ["thinking"],
        "priority_tools": ["content_writer", "idea_generator"],
        "confidence_boost": 1.2  # Boost confidence for creative detection
    },

    # Communication & Scheduling
    "communication": {
        "description": "Email, messaging, calendar, scheduling, notifications",
        "keywords": ["email", "message", "schedule", "calendar", "meeting", "appointment",
                    "reminder", "notification", "contact", "send"],
        "categories": ["automation"],
        "priority_tools": ["email_client", "calendar_scheduler"],
        "confidence_boost": 1.0
    },

    # Automation & Workflow
    "automation": {
        "description": "Task automation, workflow creation, batch processing",
        "keywords": ["automate", "workflow", "batch", "schedule", "task", "process",
                    "routine", "macro", "script workflow"],
        "categories": ["automation", "code"],
        "priority_tools": ["workflow_engine", "task_scheduler", "batch_processor"],
        "confidence_boost": 1.0
    },

    # Multimedia Processing
    "multimedia": {
        "description": "Image, audio, video processing and manipulation",
        "keywords": ["image", "photo", "picture", "audio", "video", "media", "edit",
                    "process", "convert", "resize", "filter", "crop"],
        "categories": ["filesystem"],
        "priority_tools": ["image_processor", "audio_editor", "video_tools"],
        "confidence_boost": 0.6
    },

    # Database & Storage
    "database": {
        "description": "Database queries, data storage, complex data operations",
        "keywords": ["database", "query", "sql", "table", "record", "store", "retrieve",
                    "analytics", "report", "business intelligence"],
        "categories": ["code", "filesystem"],
        "priority_tools": ["database_query", "data_warehouse", "analytics_engine"],
        "confidence_boost": 0.6
    },

    # Networking & APIs
    "networking": {
        "description": "API calls, webhooks, integrations, cloud services",
        "keywords": ["api", "webhook", "integration", "cloud", "service", "endpoint",
                    "request", "response", "connect", "sync"],
        "categories": ["http", "automation"],
        "priority_tools": ["api_client", "webhook_manager", "cloud_integrations"],
        "confidence_boost": 0.6
    },

    # Security & Compliance
    "security": {
        "description": "Encryption, authentication, access control, security checks",
        "keywords": ["encrypt", "decrypt", "password", "security", "access", "permission",
                    "authenticate", "secure", "compliance", "audit"],
        "categories": ["system", "admin"],
        "priority_tools": ["encryption_engine", "auth_manager", "security_scanner"],
        "confidence_boost": 0.7
    },

    # Learning & Education
    "learning": {
        "description": "Tutorials, explanations, educational content, skill development",
        "keywords": ["learn", "tutorial", "explain", "how to", "teach", "course",
                    "training", "skill", "understand", "example"],
        "categories": ["thinking", "exploration"],
        "priority_tools": ["tutorial_generator", "explanation_engine", "learning_assistant"],
        "confidence_boost": 0.6
    }
}


def get_tool_category(tool_name: str, tool_description: str = "") -> Optional[str]:
    """
    Get category for a tool by name and description.
    
    Strategy:
    1. Check hardcoded map (most reliable)
    2. Try pattern-based categorization
    3. Try MCP server name pattern
    4. Return None if no match
    """
    # 1. Check hardcoded map
    if tool_name in TOOL_CATEGORY_MAP:
        return TOOL_CATEGORY_MAP[tool_name]
    
    # 2. Pattern-based categorization
    tool_lower = tool_name.lower()
    desc_lower = tool_description.lower()
    combined_text = f"{tool_lower} {desc_lower}"
    
    patterns = {
        "web_search": [
            r"web_search", r"brave_search", r"google.*search", r"search.*web",
            r"lookup.*web", r"find.*information", r"research.*web"
        ],
        "filesystem": [
            r"read.*file", r"write.*file", r"list.*dir", r"path.*info",
            r"create.*file", r"delete.*file", r"copy.*file", r"move.*file",
            r"find.*file", r"watch.*path", r"make_dir", r"remove_file",
            r"remove_dir", r"append_text", r"batch_operations"
        ],
        "code": [
            r"execute.*command", r"run.*script", r"sequential.*thinking",
            r"debug", r"refactor", r"compile", r"test.*code"
        ],
        "memory": [
            r"store.*fact", r"query.*fact", r"semantic.*search", r"project_memory",
            r"remember", r"recall", r"knowledge.*base", r"delete.*fact"
        ],
        "status": [
            r"get.*status", r"check.*health", r"get.*health", r"system.*status",
            r"memory.*status", r"ingestion.*status", r"circuit.*breaker"
        ],
        "control": [
            r"set.*config", r"restart", r"pause", r"resume", r"reset",
            r"trigger", r"update.*model", r"toggle", r"reload"
        ],
        "exploration": [
            r"list.*tools", r"get.*prompt", r"get.*facts", r"get.*roles",
            r"get.*component", r"get.*configuration", r"list.*toggles"
        ],
        "thinking": [
            r"thinking", r"sequential", r"thought", r"reason", r"analyze"
        ],
        "knowledge": [
            r"search", r"knowledge", r"ingest", r"memory", r"semantic"
        ],
    }
    
    import re
    for category, pattern_list in patterns.items():
        for pattern in pattern_list:
            if re.search(pattern, combined_text, re.IGNORECASE):
                return category
    
    # 3. MCP server name pattern
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
                "project-memory": "memory",
                "scrapezy": "scraping",
                "macos_automator": "automation",
                "ollama": "ollama",
                "mcp_pandoc": "document",
                "weather": "weather",
                "thinking": "thinking",
                "sequential-thinking": "thinking",
                "system-control": "admin",
            }
            if server_name in server_to_category:
                return server_to_category[server_name]
    
    return None


def normalize_category(category: str) -> Optional[str]:
    """Normalize a category name using synonyms."""
    category_lower = category.lower()
    
    # Direct match
    if category_lower in VALID_CATEGORIES:
        return category_lower
    
    # Check synonyms
    for valid_cat, synonyms in CATEGORY_SYNONYMS.items():
        if category_lower in synonyms or category_lower == valid_cat:
            return valid_cat
    
    return None


def get_tools_by_category(tools: List[Dict[str, Any]], categories: List[str]) -> List[Dict[str, Any]]:
    """Filter tools by category."""
    normalized_categories = [normalize_category(c) for c in categories if normalize_category(c)]
    if not normalized_categories:
        return tools
    
    filtered = []
    for tool in tools:
        func = tool.get("function", {})
        tool_name = func.get("name", "")
        category = tool.get("category") or get_tool_category(tool_name, func.get("description", ""))
        
        if category in normalized_categories:
            filtered.append(tool)
    
    return filtered


# ============================================================================
# CAPABILITY DETECTION FUNCTIONS
# ============================================================================

def detect_query_capabilities(query: str) -> Dict[str, float]:
    """
    Detect which capabilities are needed for a query.
    Returns a dictionary of capability names with confidence scores.
    """
    query_lower = query.lower()
    detected_capabilities = {}

    # Enhanced keyword matching with word boundaries and partial matches
    for capability_name, capability_data in CAPABILITY_TAXONOMY.items():
        confidence = 0.0

        # Enhanced keyword matching
        for keyword in capability_data["keywords"]:
            keyword_lower = keyword.lower()

            # Exact phrase match (highest weight)
            if keyword_lower in query_lower:
                if f" {keyword_lower} " in f" {query_lower} " or query_lower.startswith(keyword_lower) or query_lower.endswith(keyword_lower):
                    confidence += 0.4
                else:
                    confidence += 0.2

            # Word-by-word matching for multi-word keywords
            keyword_words = keyword_lower.split()
            if len(keyword_words) > 1:
                match_count = sum(1 for word in keyword_words if word in query_lower)
                if match_count == len(keyword_words):
                    confidence += 0.3
                elif match_count > 0:
                    confidence += 0.1 * (match_count / len(keyword_words))

        # Enhanced pattern matching
        patterns = _get_capability_patterns(capability_name)
        for pattern in patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                confidence += 0.3

        # Semantic intent detection for common patterns
        confidence += _detect_semantic_intent(query_lower, capability_name)

        # Apply confidence boost and threshold
        if confidence > 0:
            final_confidence = min(confidence * capability_data["confidence_boost"], 1.0)
            if final_confidence >= 0.25:  # Lower threshold for broader detection
                detected_capabilities[capability_name] = final_confidence

    return detected_capabilities


def _detect_semantic_intent(query_lower: str, capability_name: str) -> float:
    """Additional semantic intent detection for edge cases."""
    confidence_boost = 0.0

    if capability_name == "automation":
        # Detect automation intent
        automation_indicators = ["backup", "monitor", "schedule", "routine", "automatically", "workflow"]
        if any(indicator in query_lower for indicator in automation_indicators):
            confidence_boost += 0.2

    elif capability_name == "system_admin":
        # Detect system admin intent
        system_indicators = ["memory usage", "cpu", "disk space", "performance", "status", "health", "diagnostics"]
        if any(indicator in query_lower for indicator in system_indicators):
            confidence_boost += 0.2

    elif capability_name == "data_analysis":
        # Detect data analysis intent
        data_indicators = ["chart", "graph", "visualize", "plot", "statistics", "analyze data"]
        if any(indicator in query_lower for indicator in data_indicators):
            confidence_boost += 0.2

    elif capability_name == "multimedia":
        # Detect multimedia intent
        media_indicators = ["image", "video", "audio", "photo", "picture", "media file"]
        if any(indicator in query_lower for indicator in media_indicators):
            confidence_boost += 0.2

    return confidence_boost


def _get_capability_patterns(capability_name: str) -> List[str]:
    """Get regex patterns for capability detection."""
    patterns = {
        "web_search": [
            r"what.*happened.*in", r"latest.*news", r"current.*events",
            r"breaking.*news", r"today.*news", r"search.*for"
        ],
        "memory": [
            r"what.*we.*talked", r"do.*you.*remember", r"previous.*conversation",
            r"what.*was.*discussed", r"recall.*that"
        ],
        "code_execution": [
            r"run.*command", r"execute.*script", r"install.*package",
            r"pip.*install", r"npm.*install"
        ],
        "file_access": [
            r"list.*files", r"read.*file", r"write.*to.*file",
            r"create.*file", r"delete.*file"
        ],
        "data_analysis": [
            r"analyze.*data", r"calculate.*average", r"create.*chart",
            r"statistical.*analysis"
        ],
        "creative": [
            r"write.*article", r"create.*content", r"brainstorm.*ideas",
            r"generate.*text"
        ],
        "research": [
            r"academic.*research", r"find.*sources", r"scholarly.*article"
        ],
        "communication": [
            r"send.*email", r"schedule.*meeting", r"set.*reminder"
        ],
        "automation": [
            r"automate.*process", r"create.*workflow", r"batch.*process"
        ],
        "multimedia": [
            r"edit.*image", r"process.*video", r"convert.*audio"
        ],
        "database": [
            r"query.*database", r"run.*sql", r"analyze.*table"
        ],
        "networking": [
            r"call.*api", r"webhook.*integration", r"cloud.*service"
        ],
        "security": [
            r"encrypt.*data", r"check.*security", r"access.*control"
        ],
        "learning": [
            r"how.*do.*i", r"explain.*how", r"learn.*about", r"tutorial.*for"
        ]
    }

    return patterns.get(capability_name, [])


def get_tools_for_capabilities(capabilities: Dict[str, float], max_tools: int = 50, quality_tier: str = "balanced") -> Dict[str, Any]:
    """
    Get prioritized tool selection based on detected capabilities.
    Returns tool categories and priority tools with intelligent prioritization.
    """
    selected_categories = set()
    priority_tools = []
    category_confidence = {}
    tool_priority_scores = {}

    # Sort capabilities by confidence (highest first)
    sorted_capabilities = sorted(capabilities.items(), key=lambda x: x[1], reverse=True)

    for capability_name, confidence in sorted_capabilities:
        capability_data = CAPABILITY_TAXONOMY[capability_name]

        # Add categories with confidence weighting
        for category in capability_data["categories"]:
            if category not in category_confidence:
                category_confidence[category] = confidence
            else:
                category_confidence[category] = max(category_confidence[category], confidence)

            selected_categories.add(category)

        # Add priority tools with scoring
        for tool in capability_data["priority_tools"]:
            if tool not in tool_priority_scores:
                tool_priority_scores[tool] = confidence
            else:
                tool_priority_scores[tool] = max(tool_priority_scores[tool], confidence)

    # Apply quality tier constraints
    tier_multipliers = {
        "fastest": 0.3,    # Very restrictive
        "fast": 0.5,       # Restrictive
        "balanced": 0.8,   # Moderate
        "quality": 1.0     # Full access
    }

    tier_multiplier = tier_multipliers.get(quality_tier.lower(), 0.8)
    effective_max_tools = int(max_tools * tier_multiplier)

    # Sort tools by priority score and select top tools
    sorted_tools = sorted(tool_priority_scores.items(), key=lambda x: x[1], reverse=True)
    priority_tools = [tool for tool, score in sorted_tools[:effective_max_tools//2]]  # Half for priority tools

    # Select top categories based on confidence
    sorted_categories = sorted(category_confidence.items(), key=lambda x: x[1], reverse=True)
    selected_categories = [cat for cat, score in sorted_categories[:effective_max_tools//2]]  # Half for categories

    return {
        "categories": selected_categories,
        "priority_tools": priority_tools,
        "category_confidence": category_confidence,
        "tool_priority_scores": tool_priority_scores,
        "capability_breakdown": sorted_capabilities,
        "quality_tier": quality_tier,
        "max_tools_limit": effective_max_tools
    }


def get_capability_memory_allocation(capabilities: Dict[str, float]) -> Dict[str, Any]:
    """
    Calculate optimal memory allocation settings based on detected capabilities.
    Returns memory allocation strategy for context, tools, and caching.
    """
    # Base memory allocations
    base_context_window = 4000
    base_max_tools = 50
    base_cache_priority = 1.0

    capability_count = len(capabilities)
    avg_confidence = sum(conf for conf in capabilities.values()) / len(capabilities) if capabilities else 1.0

    # Capability-specific memory requirements
    memory_requirements = {
        # High memory capabilities (need more context and tools)
        "research": {"context_multiplier": 2.0, "tool_multiplier": 1.5, "cache_priority": 2.0},
        "data_analysis": {"context_multiplier": 1.8, "tool_multiplier": 1.4, "cache_priority": 1.8},
        "creative": {"context_multiplier": 1.6, "tool_multiplier": 1.2, "cache_priority": 1.5},
        "automation": {"context_multiplier": 1.4, "tool_multiplier": 1.6, "cache_priority": 1.3},

        # Medium memory capabilities
        "web_search": {"context_multiplier": 1.2, "tool_multiplier": 1.1, "cache_priority": 1.4},
        "communication": {"context_multiplier": 1.1, "tool_multiplier": 1.0, "cache_priority": 1.2},
        "system_admin": {"context_multiplier": 1.3, "tool_multiplier": 1.2, "cache_priority": 1.1},

        # Low memory capabilities
        "file_access": {"context_multiplier": 1.0, "tool_multiplier": 0.8, "cache_priority": 1.0},
        "code_execution": {"context_multiplier": 1.1, "tool_multiplier": 0.9, "cache_priority": 1.0},
        "memory": {"context_multiplier": 1.2, "tool_multiplier": 0.9, "cache_priority": 1.5},

        # Default for other capabilities
        "default": {"context_multiplier": 1.0, "tool_multiplier": 1.0, "cache_priority": 1.0}
    }

    # Calculate weighted averages based on detected capabilities
    total_context_weight = 0.0
    total_tool_weight = 0.0
    total_cache_weight = 0.0
    total_weight = 0.0

    for capability_name, confidence in capabilities.items():
        req = memory_requirements.get(capability_name, memory_requirements["default"])
        total_context_weight += req["context_multiplier"] * confidence
        total_tool_weight += req["tool_multiplier"] * confidence
        total_cache_weight += req["cache_priority"] * confidence
        total_weight += confidence

    # Calculate final allocations
    if total_weight > 0:
        avg_context_multiplier = total_context_weight / total_weight
        avg_tool_multiplier = total_tool_weight / total_weight
        avg_cache_priority = total_cache_weight / total_weight
    else:
        avg_context_multiplier = avg_tool_multiplier = avg_cache_priority = 1.0

    # Apply capability count scaling (more capabilities need more resources)
    scale_factor = 1.0 + (capability_count - 1) * 0.1  # 10% increase per additional capability

    optimal_context_window = int(base_context_window * avg_context_multiplier * scale_factor)
    optimal_max_tools = int(base_max_tools * avg_tool_multiplier * scale_factor)
    cache_priority = avg_cache_priority * scale_factor

    # Context pruning strategy based on capabilities
    context_pruning_strategy = "balanced"
    if any(cap in capabilities for cap in ["research", "data_analysis", "creative"]):
        context_pruning_strategy = "preserve_recent"  # Keep more recent context for complex tasks
    elif any(cap in capabilities for cap in ["file_access", "code_execution"]):
        context_pruning_strategy = "aggressive"  # Can prune more for simple tasks

    return {
        "context_window": optimal_context_window,
        "max_tools": optimal_max_tools,
        "cache_priority": cache_priority,
        "context_pruning_strategy": context_pruning_strategy,
        "capability_count": capability_count,
        "avg_confidence": avg_confidence,
        "scale_factor": scale_factor
    }


def get_capability_context_window_adjustment(capabilities: Dict[str, float]) -> int:
    """
    Legacy function for backward compatibility.
    Use get_capability_memory_allocation() for full memory optimization.
    """
    allocation = get_capability_memory_allocation(capabilities)
    return allocation["context_window"]


def resolve_capability_conflicts(capabilities: Dict[str, float]) -> Dict[str, float]:
    """
    Resolve conflicts between capabilities that might compete for the same resources.
    Returns filtered capabilities with adjusted confidence scores.
    """
    # Define conflict groups (capabilities that shouldn't be active simultaneously)
    conflict_groups = [
        # File operations vs other operations
        {"file_access", "code_execution"},

        # Memory vs external search
        {"memory", "web_search"},

        # System admin vs user tasks
        {"system_admin", "creative", "learning"},

        # Data analysis vs simple queries
        {"data_analysis", "communication"}
    ]

    resolved_capabilities = capabilities.copy()

    for conflict_group in conflict_groups:
        # Find capabilities in this group
        active_in_group = {cap: conf for cap, conf in capabilities.items() if cap in conflict_group}

        if len(active_in_group) > 1:
            # Keep the highest confidence capability, reduce others
            sorted_group = sorted(active_in_group.items(), key=lambda x: x[1], reverse=True)
            winner = sorted_group[0][0]

            # Reduce confidence of losing capabilities
            for cap, _ in sorted_group[1:]:
                resolved_capabilities[cap] *= 0.5

    return resolved_capabilities


def generate_capability_orchestration_prompt(capabilities: Dict[str, float]) -> str:
    """
    Generate orchestration guidance for multi-capability queries.
    Provides hints to the LLM on how to coordinate multiple capabilities.
    """
    if len(capabilities) <= 1:
        return ""

    # Sort capabilities by confidence for execution order hints
    sorted_capabilities = sorted(capabilities.items(), key=lambda x: x[1], reverse=True)
    capability_names = [cap for cap, _ in sorted_capabilities]

    # Define execution patterns for common multi-capability combinations
    orchestration_patterns = {
        ("research", "data_analysis", "creative"): """
MULTI-CAPABILITY ORCHESTRATION: Research → Analysis → Creation
1. Use research tools to gather information first
2. Apply data analysis tools to process findings
3. Use creative tools to synthesize and present results
Example: "Find studies → Analyze data → Write report"
""",

        ("web_search", "data_analysis"): """
MULTI-CAPABILITY ORCHESTRATION: Search → Analysis
1. Search for relevant data sources first
2. Analyze the retrieved information
Example: "Find data online → Process and summarize"
""",

        ("memory", "creative"): """
MULTI-CAPABILITY ORCHESTRATION: Recall → Create
1. Query memory for relevant past information
2. Use creative tools to build upon historical context
Example: "Recall previous work → Generate new content"
""",

        ("automation", "system_admin"): """
MULTI-CAPABILITY ORCHESTRATION: Plan → Execute
1. Use automation tools to plan system operations
2. Apply system admin tools to execute changes
Example: "Design workflow → Implement system changes"
""",

        ("communication", "file_access"): """
MULTI-CAPABILITY ORCHESTRATION: Prepare → Send
1. Use file access tools to prepare content
2. Apply communication tools to send/deliver
Example: "Create document → Send via email"
"""
    }

    # Find matching orchestration pattern
    for capability_combo, guidance in orchestration_patterns.items():
        if all(cap in capability_names for cap in capability_combo):
            return guidance.strip()

    # Generic multi-capability guidance
    if len(capabilities) > 2:
        return f"""
MULTI-CAPABILITY QUERY DETECTED: {', '.join(capability_names[:3])}{'...' if len(capability_names) > 3 else ''}
COORDINATION STRATEGY:
• Execute capabilities in logical sequence: {capability_names[0]} → {capability_names[1]} → {capability_names[2]}
• Pass results from one capability to the next
• Synthesize final results across all capabilities
"""

    # Simple two-capability guidance
    cap1, cap2 = capability_names[:2]
    return f"""
DUAL-CAPABILITY QUERY: {cap1} + {cap2}
COORDINATION APPROACH:
• Start with {cap1} capability to gather information
• Apply {cap2} capability to process or transform results
• Combine outputs for comprehensive response

RESULT SYNTHESIS:
• Prioritize actionable insights from {cap1}
• Use {cap2} results to add depth and context
• Present integrated solution, not separate results
"""

    return ""


def generate_result_synthesis_guidance(capabilities: Dict[str, float]) -> str:
    """
    Generate guidance for synthesizing results from multiple capabilities.
    Provides instructions on how to combine and prioritize different result types.
    """
    if len(capabilities) <= 1:
        return ""

    # Define result prioritization by capability type
    result_priorities = {
        "research": "factual accuracy and source credibility",
        "data_analysis": "quantitative insights and statistical significance",
        "web_search": "timeliness and relevance of information",
        "memory": "personalization and historical context",
        "creative": "clarity and engagement of presentation",
        "automation": "efficiency and reliability of implementation",
        "system_admin": "stability and security of changes",
        "code_execution": "correctness and performance of code",
        "file_access": "accessibility and organization of data",
        "communication": "clarity and effectiveness of messaging",
        "learning": "educational value and understanding",
        "security": "compliance and protection levels",
        "database": "data integrity and query performance",
        "multimedia": "quality and usability of media",
        "networking": "connectivity and integration success"
    }

    # Sort capabilities by confidence for prioritization
    sorted_capabilities = sorted(capabilities.items(), key=lambda x: x[1], reverse=True)
    capability_names = [cap for cap, _ in sorted_capabilities]

    synthesis_parts = []

    # Primary result guidance
    primary_cap = capability_names[0]
    synthesis_parts.append(f"PRIMARY RESULTS ({primary_cap}): Focus on {result_priorities.get(primary_cap, 'quality and relevance')}")

    # Secondary results guidance
    if len(capability_names) > 1:
        secondary_caps = capability_names[1:]
        synthesis_parts.append(f"SUPPORTING RESULTS ({', '.join(secondary_caps)}): Use to enhance and contextualize primary findings")

    # Integration guidance
    if len(capability_names) >= 3:
        synthesis_parts.append("INTEGRATION: Synthesize across all capabilities for comprehensive solution")
    elif len(capability_names) == 2:
        synthesis_parts.append("INTEGRATION: Combine complementary results into unified response")

    # Quality checks
    synthesis_parts.append("QUALITY CHECKS:")
    synthesis_parts.append("• Verify information consistency across capabilities")
    synthesis_parts.append("• Prioritize recent, authoritative sources")
    synthesis_parts.append("• Ensure actionable, practical recommendations")
    synthesis_parts.append("• Balance comprehensiveness with clarity")

    return "\n".join(f"• {part}" if not part.startswith("•") else part for part in synthesis_parts)


def get_capability_execution_sequence(capabilities: Dict[str, float]) -> List[str]:
    """
    Determine optimal execution sequence for multiple capabilities.
    Returns ordered list of capability names.
    """
    # Define execution priority (lower number = higher priority)
    execution_priority = {
        # Information gathering first
        "web_search": 1,
        "research": 1,
        "memory": 2,

        # Processing/analysis second
        "data_analysis": 3,
        "code_execution": 4,

        # Action/output last
        "creative": 5,
        "communication": 6,
        "automation": 7,
        "file_access": 8,
        "system_admin": 9,

        # Utilities can be anytime
        "multimedia": 10,
        "database": 10,
        "networking": 10,
        "security": 10,
        "learning": 10
    }

    # Sort by priority, then by confidence
    capability_list = list(capabilities.items())
    capability_list.sort(key=lambda x: (
        execution_priority.get(x[0], 99),  # Priority first
        -x[1]  # Higher confidence first (descending)
    ))

    return [cap for cap, _ in capability_list]
