#!/bin/zsh
# Run or restart agent-runner with env sourced from agent_runner/agent_runner.env

set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT_DIR/agent_runner/agent_runner.env"
VENV_PYTHON="$ROOT_DIR/agent_runner/.venv/bin/python"
UVICORN_ARGS=(agent_runner:app --host 127.0.0.1 --port 5460)

load_env() {
  if [ -f "$ENV_FILE" ]; then
    # Source the env file, handling comments and empty lines properly
    set -a
    source "$ENV_FILE"
    set +a
  fi
}

start_app() {
  cd "$ROOT_DIR/agent_runner"
  load_env
  exec "$VENV_PYTHON" -m uvicorn "${UVICORN_ARGS[@]}"
}

case "${1:-start}" in
  start)
    start_app
    ;;
  restart)
    # naive restart: kill existing uvicorn on 5460 if present, then start
    if lsof -i :5460 -sTCP:LISTEN >/dev/null 2>&1; then
      kill -9 "$(lsof -t -i :5460 -sTCP:LISTEN)" >/dev/null 2>&1 || true
    fi
    start_app
    ;;
  *)
    # passthrough args to uvicorn
    cd "$ROOT_DIR/agent_runner"
    load_env
    exec "$VENV_PYTHON" -m uvicorn "$@"
    ;;
esac
