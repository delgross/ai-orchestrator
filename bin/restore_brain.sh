#!/bin/bash
set -euo pipefail

# Configuration
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SYNC_DIR="$ROOT_DIR/../_brain_state"

# Check argument or find latest
ARCHIVE=""
if [ -n "${1:-}" ]; then
    ARCHIVE="$1"
else
    # Find latest in sync dir
    ARCHIVE=$(ls -t "$SYNC_DIR"/brain_backup_*.tar.gz 2>/dev/null | head -n1 || true)
fi

if [ -z "$ARCHIVE" ]; then
    echo "❌ No backup archives found in $SYNC_DIR"
    exit 1
fi

echo "🧠 Starting Brain Restore..."
echo "   Archive: $ARCHIVE"
echo "⚠️  WARNING: THIS WILL OVERWRITE YOUR CURRENT DATABASE AND FILES."
read -p "   Are you sure? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborting."
    exit 1
fi

# 1. Stop Services (to unlock DB files and prevent writes)
echo "   - Stopping Services..."
"$ROOT_DIR/manage.sh" stop

# 2. Extract Archive
echo "   - Extracting Files..."
# We backup the current config just in case
cp "$ROOT_DIR/.env" "$ROOT_DIR/.env.bak" || true

tar -xzf "$ARCHIVE" -C "$ROOT_DIR"

# 3. Restore Database
echo "   - Restoring Knowledge Graph..."
# Start SurrealDB standalone for import
SURREAL_BIN="$HOME/.surrealdb/surreal"
SURREAL_PORT=8000
nohup "$SURREAL_BIN" start --user root --pass root --bind 127.0.0.1:$SURREAL_PORT "file:$HOME/ai/agent_data/surreal_db" > /dev/null 2>&1 &
SURREAL_PID=$!

# Wait for it to allow connection
echo "     Waiting for DB..."
sleep 5

# Import
"$SURREAL_BIN" import --user root --pass root --ns orchestrator --db knowledge "$ROOT_DIR/temp_export.sql"

# Kill the temporary DB process
kill "$SURREAL_PID" || true
rm "$ROOT_DIR/temp_export.sql"

# 4. Cleanup/Restart
echo "   - Restarting Services..."
"$ROOT_DIR/manage.sh" start

echo "✅ Restore Complete. System is now a clone of validation timestamp."
