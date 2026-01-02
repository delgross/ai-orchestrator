#!/bin/bash
# Wrapper to run the MCP Stdio Bridge
# Configure Claude/Cursor to run this script.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export ROUTER_AUTH_TOKEN="9sYBjBLjAHKG8g8ZzzsUeBOvtzgQFHmX7oIeygdpzic" # Helper defaults if env not set
python3 "$SCRIPT_DIR/mcp_stdio_bridge.py" "$@"
