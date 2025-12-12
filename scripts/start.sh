#!/usr/bin/env bash
set -euo pipefail

AI_DIR="$HOME/ai"
PORT="${AI_GATEWAY_PORT:-5455}"
HOST="${AI_GATEWAY_HOST:-127.0.0.1}"

cd "$AI_DIR"

if [[ ! -x "$AI_DIR/.venv/bin/python" ]]; then
  echo "ERROR: venv not found at $AI_DIR/.venv"
  exit 1
fi

if lsof -ti tcp:"$PORT" >/dev/null 2>&1; then
  echo "ERROR: Port $PORT is already in use."
  echo "Run: $AI_DIR/scripts/stop.sh"
  exit 1
fi

export OLLAMA_BASE="${OLLAMA_BASE:-http://127.0.0.1:11434}"
export DEFAULT_FALLBACK_MODEL="${DEFAULT_FALLBACK_MODEL:-llama3:8b}"

exec "$AI_DIR/.venv/bin/python" -m uvicorn router.router:app \
  --host "$HOST" --port "$PORT" \
  --log-level info
