#!/bin/bash
# Restart Antigravity System
# Wrapper for stop_all + start_all

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

echo "🔄 Triggering full system restart..."
./bin/stop_all.sh

echo "⏳ Waiting 3 seconds..."
sleep 3

./bin/start_all.sh
echo "✅ Restart command passed to start_all.sh (detached)"
