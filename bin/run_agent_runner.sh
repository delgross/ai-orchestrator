#!/bin/zsh
# Run or restart agent-runner with env sourced from agent_runner/agent_runner.env

set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT_DIR/agent_runner/agent_runner.env"
VENV_PYTHON="$ROOT_DIR/.venv/bin/python"
UVICORN_ARGS=(agent_runner.main:app --host 127.0.0.1 --port 5460)

load_env() {
  if [ -f "$ENV_FILE" ]; then
    # Source the env file, handling comments and empty lines properly
    set -a
    source "$ENV_FILE"
    set +a
  fi
}

ensure_path() {
  # launchd often provides a minimal PATH; make common tool locations available.
  # Explicitly include the user's NVM and Homebrew paths discovered during investigation.
  export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:${PATH:-}"
  
  # Add known specific tool paths for this machine
  export PATH="/Users/bee/.nvm/versions/node/v22.21.1/bin:$PATH"
  export PATH="/opt/homebrew/bin:$PATH"

  # Fallback for dynamic NVM discovery
  if ! command -v npx >/dev/null 2>&1; then
    local nvm_dir="${NVM_DIR:-$HOME/.nvm}"
    if [ -d "$nvm_dir/versions/node" ]; then
      local newest_npx
      newest_npx="$(ls -1d "$nvm_dir"/versions/node/*/bin/npx 2>/dev/null | sort -V | tail -n 1 || true)"
      if [ -n "$newest_npx" ] && [ -x "$newest_npx" ]; then
        export PATH="$(dirname "$newest_npx"):$PATH"
      fi
    fi
  fi
}

start_app() {
  cd "$ROOT_DIR"
  load_env
  ensure_path
  RELOAD="--reload --reload-exclude 'logs/*' --reload-exclude '.gemini/*'" # in development (set DEV_MODE=1 to enable)
  if [ "${DEV_MODE:-0}" = "1" ]; then
    exec "$VENV_PYTHON" -m uvicorn $RELOAD "${UVICORN_ARGS[@]}"
  else
    exec "$VENV_PYTHON" -m uvicorn "${UVICORN_ARGS[@]}"
  fi
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
    cd "$ROOT_DIR"
    load_env
    ensure_path
    exec "$VENV_PYTHON" -m uvicorn "$@"
    ;;
esac
