import asyncio
import logging
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent_runner.registry import ServiceRegistry
from agent_runner.tools.mcp import tool_mcp_proxy
from agent_runner.agent_runner import get_shared_state

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_fetch")

async def main():
    print("--- Verifying Fetch MCP Tool ---")
    
    # 1. Initialize State (Load MCP Servers)
    state = get_shared_state()
    from agent_runner.config import load_mcp_servers
    await load_mcp_servers(state)
    
    if "fetch" not in state.mcp_servers:
        print("❌ Error: 'fetch' server not found in configuration.")
        print("Available servers:", list(state.mcp_servers.keys()))
        return

    print("✅ 'fetch' server loaded.")

    # 2. Call Fetch Tool
    target_url = "https://example.com"
    print(f"Testing fetch of: {target_url}")
    
    # Arguments: server, tool, arguments
    # Note: 'fetch' server usually has a tool named 'fetch' taking 'url'
    try:
        result = await tool_mcp_proxy(
            state=state,
            server="fetch",
            tool="fetch",
            arguments={"url": target_url}
        )
        
        if result.get("ok"):
            print("✅ Success! Content retrieved.")
            content = result.get("result", {}).get("content", [])
            if content:
                preview = str(content[0].get("text", ""))[:100]
                print(f"Preview: {preview}...")
            else:
                print("Result ok, but content empty?", result)
        else:
            print("❌ Failed:", result.get("error"))

    except Exception as e:
        print(f"❌ CRITICAL EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
