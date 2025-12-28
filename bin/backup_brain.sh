#!/bin/bash
set -euo pipefail

# Configuration
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SYNC_DIR="$ROOT_DIR/../_brain_state" # Parent folder (Sync/Antigravity/_brain_state)
BACKUP_NAME="brain_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
LATEST_LINK="$SYNC_DIR/latest_brain.tar.gz"

echo "🧠 Starting Brain Backup..."

# 1. Ensure Sync Dir exists
mkdir -p "$SYNC_DIR"

# 2. Export SurrealDB
# We export to a temporary SQL file
echo "   - Exporting Knowledge Graph..."
SURREAL_PORT=8000
# Ensure DB is reachable
if ! curl -s "http://127.0.0.1:$SURREAL_PORT/health" > /dev/null; then
    echo "❌ Error: SurrealDB is not running. Cannot export."
    exit 1
fi

# Export using surreal tool (assumes installed) or curl
# Since 'surreal export' is a CLI command, we try to use the binary if available
SURREAL_BIN="$HOME/.surrealdb/surreal"
if [ -f "$SURREAL_BIN" ]; then
    "$SURREAL_BIN" export --user root --pass root --ns orchestrator --db knowledge "$ROOT_DIR/temp_export.sql"
else
    # Fallback to simple file copy of the data dir if possible (only if process stopped)
    # But usually we must use export. 
    echo "❌ Error: SurrealDB binary not found. export failed."
    exit 1
fi

# 3. Create Archive
# We bundle: the SQL export + the agent_fs_root (files) + .env (config)
echo "   - Compressing Archive..."
tar -czf "$SYNC_DIR/$BACKUP_NAME" \
    -C "$ROOT_DIR" \
    "temp_export.sql" \
    "agent_fs_root" \
    ".env"

# 4. Cleanup
rm "$ROOT_DIR/temp_export.sql"

# 5. Update Latest Link
ln -sf "$BACKUP_NAME" "$LATEST_LINK"

echo "✅ Backup Complete: $SYNC_DIR/$BACKUP_NAME"
echo "   (Size: $(du -h "$SYNC_DIR/$BACKUP_NAME" | cut -f1))"
