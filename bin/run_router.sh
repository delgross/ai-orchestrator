#!/bin/bash
# Run or restart router with standardized environment handling

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Load shared startup library
source "$SCRIPT_DIR/startup_lib.sh"

# Default to port 5455 if not in env
ROUTER_PORT="${ROUTER_PORT:-5455}"

start_app() {
  cd "$PROJECT_ROOT"

  # Load environment with standardized approach
  load_environment "$PROJECT_ROOT" "router"

  # Ensure PATH includes required tools
  ensure_path

  # Check for database dependency in graceful degradation mode
  if [ "${GRACEFUL_DEGRADATION:-0}" != "1" ]; then
    if ! "$SCRIPT_DIR/service_discovery.sh" wait database 10; then
      warn "Database not available, but proceeding (graceful degradation disabled)"
    fi
  fi

  if [ "${DEV_MODE:-0}" = "1" ]; then
    info "Starting router in development mode with auto-reload"
    exec "$PROJECT_ROOT/.venv/bin/python3" -m uvicorn router.main:app \
      --host 127.0.0.1 --port $ROUTER_PORT --log-level info --reload
  else
    exec "$PROJECT_ROOT/.venv/bin/python3" -m uvicorn router.main:app \
      --host 127.0.0.1 --port $ROUTER_PORT --log-level info
  fi
}

case "${1:-start}" in
  start)
    start_app
    ;;
  restart)
    # Clean up existing processes before restart
    cleanup_service "router"
    start_app
    ;;
  *)
    # Passthrough args to uvicorn
    cd "$PROJECT_ROOT"
    load_environment "$PROJECT_ROOT" "router"
    ensure_path
    exec "$PROJECT_ROOT/.venv/bin/python3" -m uvicorn router.main:app "$@"
    ;;
esac
