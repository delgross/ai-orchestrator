#!/bin/bash
# Run RAG server with standardized environment handling

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Load shared startup library
source "$SCRIPT_DIR/startup_lib.sh"

start_app() {
  cd "$PROJECT_ROOT"

  # Load environment with standardized approach
  load_environment "$PROJECT_ROOT"

  # Ensure PATH includes required tools
  ensure_path

  # Check for database dependency in graceful degradation mode
  if [ "${GRACEFUL_DEGRADATION:-0}" != "1" ]; then
    if ! "$SCRIPT_DIR/service_discovery.sh" wait database 10; then
      warn "Database not available, but proceeding (graceful degradation enabled)"
    fi
  fi

  info "Starting RAG Server..."
  exec "$PROJECT_ROOT/.venv/bin/python3" rag_server.py
}

case "${1:-start}" in
  start)
    start_app
    ;;
  restart)
    # Clean up existing processes before restart
    cleanup_service "rag"
    start_app
    ;;
  *)
    # Passthrough args
    cd "$PROJECT_ROOT"
    load_environment "$PROJECT_ROOT"
    ensure_path
    exec "$PROJECT_ROOT/.venv/bin/python3" rag_server.py "$@"
    ;;
esac
