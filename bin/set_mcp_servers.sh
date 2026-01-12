#!/bin/zsh
# Configure MCP_SERVERS (and optional tokens) in agent_runner.env and restart agent-runner.
#
# Example:
#   set_mcp_servers.sh "local=http://127.0.0.1:7000,remote=https://mcp.example.com"
#
# Then set tokens separately:
#   echo 'MCP_TOKEN_LOCAL="secret"' >> agent_runner/agent_runner.env

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT_DIR/agent_runner/agent_runner.env"
SERVICE_SCRIPT="$ROOT_DIR/bin/run_agent_runner.sh"

if [ $# -ne 1 ]; then
  echo "Usage: $0 \"name=url[,name2=url2,...]\"" >&2
  exit 1
fi

SERVERS="$1"

if [ ! -f "$ENV_FILE" ]; then
  echo "Creating env file at $ENV_FILE"
  echo "# Agent runner environment" > "$ENV_FILE"
fi

if grep -q "^MCP_SERVERS=" "$ENV_FILE"; then
  sed -i '' "s|^MCP_SERVERS=.*|MCP_SERVERS=\"$SERVERS\"|" "$ENV_FILE"
else
  echo "MCP_SERVERS=\"$SERVERS\"" >> "$ENV_FILE"
fi

echo "Set MCP_SERVERS=\"$SERVERS\" in $ENV_FILE"
echo "Remember to add MCP_TOKEN_<NAME> vars for any server that needs a token."

if [ -x "$SERVICE_SCRIPT" ]; then
  echo "Restarting agent-runner via $SERVICE_SCRIPT"
  "$SERVICE_SCRIPT" restart 2>/dev/null || "$SERVICE_SCRIPT" 2>/dev/null || true
else
  echo "No restart performed (missing $SERVICE_SCRIPT). Please restart agent-runner manually."
fi

echo "Done."








