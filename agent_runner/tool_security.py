"""
Tool Security Defaults

Defines which tools require admin access.
Database is source of truth, but this provides defaults for tools not yet indexed.
"""

# Tools that require admin/sudo access
ADMIN_REQUIRED_TOOLS = {
    # Dangerous Operations
    "reset_all_circuit_breakers",
    "trigger_backup",
    "update_model_config",
    "deprecate_tool",
    "clear_ingestion_problem",
    
    # Internal/System Operations
    "query_logs",
    "add_lexicon_entry",
    "record_tool_usage",
    "store_llm_opportunities",
    "store_medium_term_plan",
    
    # Advanced Operations
    "start_thinking_branch",
    "repair_thinking_session",
    "registry_manage",
    
    # Model Preset Management
    "save_model_preset",
    "load_model_preset",
    "delete_model_preset",
}

# All other tools are public (no admin required)

def tool_requires_admin(tool_name: str) -> bool:
    """Check if tool requires admin (from code defaults)."""
    return tool_name in ADMIN_REQUIRED_TOOLS

