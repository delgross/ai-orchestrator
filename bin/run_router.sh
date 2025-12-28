#!/usr/bin/env bash
set -euo pipefail
# Resolve directory of this script (bin/)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Project root is one level up
PROJECT_ROOT="$(dirname "$DIR")"
cd "$PROJECT_ROOT"

# load service config first (non-secret)
if [ -f "$PROJECT_ROOT/router.env" ]; then
  set -a
  . "$PROJECT_ROOT/router.env"
  set +a
fi

# load provider keys second
if [ -f "$PROJECT_ROOT/providers.env" ]; then
  set -a
  . "$PROJECT_ROOT/providers.env"
  set +a
fi

# Use the venv from the project root
# Auto-reload in development (set DEV_MODE=1 to enable)
if [ "${DEV_MODE:-0}" = "1" ]; then
  exec "$PROJECT_ROOT/.venv/bin/python3" -m uvicorn router.router:app \
    --host 127.0.0.1 --port 5455 --log-level info --reload
else
  exec "$PROJECT_ROOT/.venv/bin/python3" -m uvicorn router.router:app \
    --host 127.0.0.1 --port 5455 --log-level info
fi
