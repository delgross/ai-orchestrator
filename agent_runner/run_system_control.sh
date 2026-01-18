#!/bin/bash
# Wrapper to start system_control_server with the correct interpreter.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="$SCRIPT_DIR/../.venv/bin/python"
SERVER_SCRIPT="$SCRIPT_DIR/system_control_server.py"
exec "$PYTHON_BIN" "$SERVER_SCRIPT" "$@"
