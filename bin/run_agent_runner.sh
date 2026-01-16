#!/bin/zsh
# Run or restart agent-runner with env sourced from agent_runner/agent_runner.env

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Load shared startup library
source "$SCRIPT_DIR/startup_lib.sh"

VENV_PYTHON="$PROJECT_ROOT/.venv/bin/python"
UVICORN_ARGS=(agent_runner.main:app --host 127.0.0.1 --port 5460)

start_app() {
  cd "$PROJECT_ROOT"

  # Load environment with standardized approach
  load_environment "$PROJECT_ROOT" "agent_runner"

  # Ensure PATH includes required tools
  ensure_path

  # Check for database dependency in graceful degradation mode
  if [ "${GRACEFUL_DEGRADATION:-0}" != "1" ]; then
    if ! "$SCRIPT_DIR/service_discovery.sh" wait database 10; then
      warn "Database not available, but proceeding (graceful degradation disabled)"
    fi
  fi

  RELOAD_ARGS=""
  if [ "${DEV_MODE:-0}" = "1" ]; then
    RELOAD_ARGS="--reload --reload-exclude 'logs/*' --reload-exclude '.gemini/*'"
    info "Starting in development mode with auto-reload"
  fi

  exec "$VENV_PYTHON" -m uvicorn $RELOAD_ARGS "${UVICORN_ARGS[@]}"
}


case "${1:-start}" in
  start)
    start_app
    ;;
  restart)
    # Clean up zombies and existing processes before restart
    cleanup_service "agent_runner" 5460
    start_app
    ;;
  *)
    # passthrough args to uvicorn
    cd "$PROJECT_ROOT"
    load_environment "$PROJECT_ROOT" "agent_runner"
    ensure_path
    exec "$VENV_PYTHON" -m uvicorn "$@"
    ;;
esac
