#!/bin/zsh
# Configure RAG backend env (RAG_BASE, RAG_QUERY_PATH) and restart router.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT_DIR/router.env"
SERVICE_SCRIPT="$ROOT_DIR/bin/run_router.sh"

if [ $# -lt 1 ] || [ $# -gt 2 ]; then
  echo "Usage: $0 <rag_base_url> [rag_query_path]" >&2
  echo "Example: $0 http://127.0.0.1:5555 /query" >&2
  exit 1
fi

RAG_BASE="$1"
RAG_QUERY_PATH="${2:-/query}"

if [ ! -f "$ENV_FILE" ]; then
  echo "Creating env file at $ENV_FILE"
  echo "# Router environment" > "$ENV_FILE"
fi

update_var() {
  local name="$1"
  local value="$2"
  if grep -q "^$name=" "$ENV_FILE"; then
    sed -i '' "s|^$name=.*|$name=\"$value\"|" "$ENV_FILE"
  else
    echo "$name=\"$value\"" >> "$ENV_FILE"
  fi
}

update_var "RAG_BASE" "$RAG_BASE"
update_var "RAG_QUERY_PATH" "$RAG_QUERY_PATH"

echo "Set RAG_BASE=$RAG_BASE and RAG_QUERY_PATH=$RAG_QUERY_PATH in $ENV_FILE"

if [ -x "$SERVICE_SCRIPT" ]; then
  echo "Restarting router via $SERVICE_SCRIPT"
  "$SERVICE_SCRIPT" restart 2>/dev/null || "$SERVICE_SCRIPT" 2>/dev/null || true
else
  echo "No restart performed (missing $SERVICE_SCRIPT). Please restart router manually."
fi

echo "Done."







