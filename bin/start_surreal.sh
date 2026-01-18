#!/bin/bash
# bin/start_surreal.sh

# Ensure logs dir exists
mkdir -p logs

# Root Dir resolution
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DATA_DIR="$ROOT_DIR/agent_data"

# Ensure data dir exists
mkdir -p "$DATA_DIR"

# Resolve Surreal binary
SURREAL_BIN="${SURREAL_BIN:-$HOME/.surrealdb/surreal}"
if [ ! -x "$SURREAL_BIN" ]; then
	if command -v surreal >/dev/null 2>&1; then
		SURREAL_BIN="$(command -v surreal)"
	elif [ -x "$HOME/.surrealdb/surreal" ]; then
		SURREAL_BIN="$HOME/.surrealdb/surreal"
	else
		echo "SurrealDB binary not found. Install it or set SURREAL_BIN to the executable path."
		exit 1
	fi
fi

echo "🚀 Starting SurrealDB..."
# Bind to all interfaces for flexibility, use file storage
# User/Pass hardcoded for dev environment as per config
nohup "$SURREAL_BIN" start --user root --pass root --bind 0.0.0.0:8000 "file://$DATA_DIR/surreal.db" > "$ROOT_DIR/logs/surreal.log" 2>&1 &

# Store PID? Or just let it run.
echo "✅ SurrealDB process launched."
