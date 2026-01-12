#!/bin/zsh
# Set AGENT_MODEL in agent_runner/agent_runner.env and restart the agent-runner service.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT_DIR/agent_runner/agent_runner.env"
SERVICE_SCRIPT="$ROOT_DIR/bin/run_agent_runner.sh"

if [ $# -ne 1 ]; then
  echo "Usage: $0 <provider:model>" >&2
  echo "Example: $0 openai:gpt-4.1-mini" >&2
  exit 1
fi

MODEL="$1"

if [ ! -f "$ENV_FILE" ]; then
  echo "Creating env file at $ENV_FILE"
  echo "# Agent runner environment" > "$ENV_FILE"
fi

# Update or add AGENT_MODEL line.
if grep -q "^AGENT_MODEL=" "$ENV_FILE"; then
  sed -i '' "s|^AGENT_MODEL=.*|AGENT_MODEL=\"$MODEL\"|" "$ENV_FILE"
else
  echo "AGENT_MODEL=\"$MODEL\"" >> "$ENV_FILE"
fi

echo "Set AGENT_MODEL to '$MODEL' in $ENV_FILE"

# Restart agent-runner if a run script exists.
if [ -x "$SERVICE_SCRIPT" ]; then
  echo "Restarting agent-runner via $SERVICE_SCRIPT"
  "$SERVICE_SCRIPT" restart 2>/dev/null || "$SERVICE_SCRIPT" 2>/dev/null || true
else
  echo "No restart performed (missing $SERVICE_SCRIPT). Please restart agent-runner manually."
fi

echo "Done."







