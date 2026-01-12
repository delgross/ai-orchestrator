#!/bin/bash
# bin/start_surreal.sh

# Ensure logs dir exists
mkdir -p logs

# Root Dir resolution
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DATA_DIR="$ROOT_DIR/agent_data"

# Ensure data dir exists
mkdir -p "$DATA_DIR"

echo "🚀 Starting SurrealDB..."
# Bind to all interfaces for flexibility, use file storage
# User/Pass hardcoded for dev environment as per config
nohup surreal start --user root --pass root --bind 0.0.0.0:8000 "file://$DATA_DIR/surreal.db" > "$ROOT_DIR/logs/surreal.log" 2>&1 &

# Store PID? Or just let it run.
echo "✅ SurrealDB process launched."
