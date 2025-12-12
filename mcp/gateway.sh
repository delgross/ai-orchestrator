#!/bin/zsh

echo "Starting MCP Provider..."

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
source .venv/bin/activate

uvicorn router.router:app \
  --host 127.0.0.1 \
  --port 5455 \
  --reload
