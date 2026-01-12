from common.constants import ROLE_SYSTEM, ROLE_USER

def get_healer_prompt(tool_name: str, args: str, error_str: str) -> list:
    """
    Construct the prompt for the Healer (Escalation Protocol).
    """
    return [
        {"role": ROLE_SYSTEM, "content": "You are the HEALER. The System Agent has failed to use a tool twice. Analyze the error and Provide the CORRECT tool call JSON or a fix explanation. Do NOT pontificate. Fix it."},
        {"role": ROLE_USER, "content": f"Tool Call Failed Twice.\nTool: {tool_name}\nArgs: {args}\nError: {error_str}\n\nFIX IT."}
    ]

def get_base_system_instructions(internet_available: bool) -> str:
    """
    Get the base environment instructions based on internet status.
    """
    if internet_available:
        return (
            "You have access to a set of provided tools to assist the user.\n"
            "PRIORITY RULE: For factual/public questions (e.g. news, stocks), use web search tools.\n"
            "PRIORITY RULE: For PERSONAL questions (e.g. 'my dog', 'I said'), use INTERNAL MEMORY first. DO NOT search the web for user-specific facts unless explicitly asked."
        )
    else:
        return (
            "NOTICE: The system is currently in LOCAL-ONLY mode because the internet is unavailable.\n"
            "Do NOT attempt to use web search tools (exa, tavily, perplexity, firecrawl). They will fail.\n"
            "Inform the user that you are operating offline if they ask for real-time information.\n"
            "Rely on your internal knowledge and the 'project-memory' and 'filesystem' tools."
        )

def get_service_alerts(open_breakers: list, memory_status_msg: str) -> str:
    """
    Construct service alert string.
    """
    alerts = ""
    if open_breakers:
        alerts = (
            # "\nSERVICE NOTICE:\n"
            # f"The following MCP servers are currently unavailable: {', '.join(open_breakers)}.\n"
            # "If the user's request requires these tools, attempt to use ALTERNATIVE tools (e.g. use 'tavily-search' if 'brave-search' is down) or internal knowledge first.\n"
            # "Only inform the user of the outage if NO viable alternatives exist."
            ""
        )
    
    if memory_status_msg:
        alerts += f"\n{memory_status_msg}"
        
    return alerts
