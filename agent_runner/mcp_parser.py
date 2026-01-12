import json
import logging
import yaml
from typing import Dict, Any, List
from agent_runner.state import AgentState
from agent_runner.db_utils import run_query

logger = logging.getLogger("agent_runner.mcp_parser")

MCP_PARSER_PROMPT = """
You are an expert at configuring Model Context Protocol (MCP) servers.
Your task is to parse the provided text and extract MCP server configurations.

The input may be:
- Claude Desktop JSON format
- Standard MCP JSON/YAML
- A plain text description of an MCP server (e.g. "Add a weather server that uses npx @package/name with API_KEY=123")

### Output Format
You MUST return a JSON object where keys are server names and values are their configurations.
IMPORTANT: Use the standard YAML-compatible format we use:
{
  "server_name": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@package/name"],
    "env": {"KEY": "VALUE"},
    "requires_internet": true
  }
}

If 'type' is not specified, assume 'stdio'.
If 'command' is not specified but it looks like an npx package, set command to 'npx' and args accordingly.

Return ONLY the JSON. No preamble, no explanation.
"""

async def parse_mcp_config_with_llm(state: AgentState, raw_content: str) -> Dict[str, Any]:
    """Use the system's task_model to parse raw MCP configuration text."""
    from agent_runner.engine import AgentEngine
    engine = AgentEngine(state) # We can use a lightweight engine call or direct router call
    
    messages = [
        {"role": "system", "content": MCP_PARSER_PROMPT},
        {"role": "user", "content": f"Parse this MCP configuration:\n\n{raw_content}"}
    ]
    
    try:
        # We use a lower temperature for extraction
        completion = await engine.agent_loop(
            messages, 
            model=state.task_model, 
            request_id="mcp-parse"
        )
        
        content = completion.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        
        # Strip markdown code blocks if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:].strip()
            content = content.strip()
            if content.endswith("```"):
                content = content[:-3].strip()
        
        parsed = json.loads(content)
        # Ensure it's a dict and specifically looks like server definitions
        if "mcpServers" in parsed:
            parsed = parsed["mcpServers"]
            
        return parsed
    except Exception as e:
        logger.error(f"Failed to parse MCP config with LLM: {e}")
        return {}
