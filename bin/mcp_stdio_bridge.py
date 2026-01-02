#!/usr/bin/env python3
"""
Antigravity MCP Bridge (Stdio -> SSE)
Allows Stdio-based MCP clients (like Claude Desktop) to connect to Antigravity.

Usage:
    python3 mcp_stdio_bridge.py [--url http://localhost:5460]
"""

import asyncio
import sys
import json
import logging
import httpx
import os
import argparse

# Configure logging to stderr (stdout is for JSON-RPC)
logging.basicConfig(level=logging.INFO, stream=sys.stderr, format="[Bridge] %(message)s")
logger = logging.getLogger("mcp_bridge")

async def forward_stdio_to_sse(session_url: str, auth_token: str):
    """Read stdin line-by-line and POST to SSE endpoint."""
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)

    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            # MCP Stdio uses JSON-RPC lines
            line = await reader.readline()
            if not line:
                break
            
            try:
                msg = json.loads(line)
                # Post to server
                await client.post(
                    session_url, 
                    json=msg, 
                    headers={"Authorization": f"Bearer {auth_token}"}
                )
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received on stdin: {line}")
            except Exception as e:
                logger.error(f"Failed to forward message: {e}")

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:5460", help="Base URL of Agent Runner")
    args = parser.parse_args()

    base_url = args.url.rstrip("/")
    sse_url = f"{base_url}/mcp/sse"
    auth_token = os.getenv("ROUTER_AUTH_TOKEN", "dev_token_123")

    logger.info(f"Connecting to {sse_url}...")

    # WE Need to handle the SSE stream and Stdio concurrently.
    # AND we need the session URL from the first SSE event.

    endpoint_future = asyncio.Future()

    async def sse_worker():
        retry_delay = 1
        while True:
            try:
                async with httpx.AsyncClient(timeout=None) as client:
                    async with client.stream("GET", sse_url, headers={"Authorization": f"Bearer {auth_token}", "X-Client-Name": "StdioBridge"}) as response:
                        logger.info("SSE Connected.")
                        async for line in response.aiter_lines():
                            if not line.startswith("data:"): continue
                            try:
                                data = json.loads(line[5:])
                                
                                if "type" in data and data["type"] == "endpoint":
                                    if not endpoint_future.done():
                                        endpoint_future.set_result(data["uri"])
                                elif "jsonrpc" in data:
                                    sys.stdout.write(json.dumps(data) + "\n")
                                    sys.stdout.flush()
                            except Exception as parse_err:
                                logger.error(f"SSE Parse Error: {parse_err}")
                                
            except Exception as e:
                logger.error(f"SSE Disconnected: {e}. Retrying in {retry_delay}s...")
                await asyncio.sleep(retry_delay)

    # Start SSE
    asyncio.create_task(sse_worker())

    # Wait for Endpoint URL
    try:
        session_message_url = await asyncio.wait_for(endpoint_future, timeout=10.0)
        logger.info(f"Session Active. POST URL: {session_message_url}")
    except asyncio.TimeoutError:
        logger.error("Timed out waiting for SSE Handshake.")
        return

    # Start Stdio Forwarder
    await forward_stdio_to_sse(session_message_url, auth_token)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
