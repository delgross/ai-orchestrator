#!/bin/zsh

# Install backup alias for easy access to GitHub backup script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_SCRIPT="$SCRIPT_DIR/backup_to_github.sh"

# Check if script exists and is executable
if [[ ! -x "$BACKUP_SCRIPT" ]]; then
    echo "Error: Backup script not found or not executable: $BACKUP_SCRIPT"
    exit 1
fi

# Determine shell config file
if [[ -n "$ZSH_VERSION" ]]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [[ -n "$BASH_VERSION" ]]; then
    SHELL_CONFIG="$HOME/.bashrc"
else
    SHELL_CONFIG="$HOME/.profile"
fi

# Backup existing config
if [[ -f "$SHELL_CONFIG" ]]; then
    cp "$SHELL_CONFIG" "$SHELL_CONFIG.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Add alias to shell config
cat >> "$SHELL_CONFIG" << EOF

# Antigravity AI - GitHub Backup Alias
# Added on $(date)
alias backup-ai="$BACKUP_SCRIPT"
alias backup-full="$BACKUP_SCRIPT -t full"
alias backup-config="$BACKUP_SCRIPT -t config"
alias backup-data="$BACKUP_SCRIPT -t data"

EOF

echo "✅ Backup aliases installed!"
echo ""
echo "Available commands:"
echo "  backup-ai        # Incremental backup (default)"
echo "  backup-full      # Full codebase backup"
echo "  backup-config    # Configuration files backup"
echo "  backup-data      # Data and logs backup"
echo ""
echo "Additional options:"
echo "  backup-ai -m 'Custom message'    # Custom commit message"
echo "  backup-ai -n                     # Commit locally only"
echo "  backup-ai -s                     # Show git status"
echo ""
echo "Restart your shell or run: source $SHELL_CONFIG"
echo ""
echo "To uninstall, remove the alias lines from $SHELL_CONFIG"