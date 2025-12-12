#!/usr/bin/env bash
set -euo pipefail

AI_DIR="$HOME/ai"
PORT="${AI_GATEWAY_PORT:-5455}"
HOST="${AI_GATEWAY_HOST:-127.0.0.1}"

cd "$AI_DIR"

export OLLAMA_BASE="${OLLAMA_BASE:-http://127.0.0.1:11434}"
export DEFAULT_FALLBACK_MODEL="${DEFAULT_FALLBACK_MODEL:-llama3:8b}"

exec "$AI_DIR/.venv/bin/python" -m uvicorn router.router:app \
  --host "$HOST" --port "$PORT" \
  --reload --log-level info
