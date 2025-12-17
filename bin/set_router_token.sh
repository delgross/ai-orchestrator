#!/bin/zsh
# Set ROUTER_AUTH_TOKEN in router.env (or create it) and restart router if possible.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT_DIR/router.env"
SERVICE_SCRIPT="$ROOT_DIR/bin/run_router.sh"

if [ $# -ne 1 ]; then
  echo "Usage: $0 <token>" >&2
  exit 1
fi

TOKEN="$1"

if [ ! -f "$ENV_FILE" ]; then
  echo "Creating env file at $ENV_FILE"
  echo "# Router environment" > "$ENV_FILE"
fi

# Update or add ROUTER_AUTH_TOKEN line.
if grep -q "^ROUTER_AUTH_TOKEN=" "$ENV_FILE"; then
  sed -i '' "s|^ROUTER_AUTH_TOKEN=.*|ROUTER_AUTH_TOKEN=\"$TOKEN\"|" "$ENV_FILE"
else
  echo "ROUTER_AUTH_TOKEN=\"$TOKEN\"" >> "$ENV_FILE"
fi

echo "Set ROUTER_AUTH_TOKEN in $ENV_FILE"

# Restart router if a run script exists.
if [ -x "$SERVICE_SCRIPT" ]; then
  echo "Restarting router via $SERVICE_SCRIPT"
  "$SERVICE_SCRIPT" restart 2>/dev/null || "$SERVICE_SCRIPT" 2>/dev/null || true
else
  echo "No restart performed (missing $SERVICE_SCRIPT). Please restart router manually."
fi

echo "Done."






