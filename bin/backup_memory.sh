#!/usr/bin/env bash
# SurrealDB Memory Backup Script
# Creates a SQL export of the memory database

set -euo pipefail

# Robust paths relative to project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Data and Binaries
BACKUP_DIR="$ROOT_DIR/agent_data/backups"
SURREAL_BIN="$HOME/.surrealdb/surreal"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/memory_backup_$TIMESTAMP.sql"

mkdir -p "$BACKUP_DIR"

echo "Starting SurrealDB backup to $BACKUP_FILE..."

# Perform export
if "$SURREAL_BIN" export --conn "http://127.0.0.1:8000" --user root --pass root --ns orchestrator --db memory "$BACKUP_FILE"; then
    echo "Backup successful: $BACKUP_FILE"
    
    # Compress the backup
    gzip "$BACKUP_FILE"
    COMPRESSED_FILE="${BACKUP_FILE}.gz"
    echo "Compressed: $COMPRESSED_FILE"
    
    # Push to Git (Optional: only if the user wants backups tracked)
    # Note: We usually ignore agent_data/, but if the user wants it 'pushing to git',
    # we can specifically add this file or commit from this script.
    if [ -d "$ROOT_DIR/.git" ]; then
        echo "Updating git with new backup entry..."
        # We don't necessarily want to force-add a .gitignored file every time,
        # but if the user asked to 'pushing to git', we can commit a 'backup_manifest.txt'
        echo "$TIMESTAMP: $COMPRESSED_FILE" >> "$ROOT_DIR/agent_data/backup_log.txt"
        cd "$ROOT_DIR"
        git add .
        git commit -m "Automated Memory Backup: $TIMESTAMP" || true
        git push origin main || echo "Git push failed (possibly no internet or auth issue)"
    fi

    # Rotate: Keep last 7 days of backups
    echo "Cleaning up backups older than 7 days..."
    find "$BACKUP_DIR" -name "memory_backup_*.sql.gz" -mtime +7 -delete
    
    echo "Backup rotation complete."
else
    echo "Error: Backup failed!"
    exit 1
fi

