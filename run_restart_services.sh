#!/usr/bin/env bash
set -euo pipefail

cd "$HOME/ai"

# Run the requested action (default: restart)
./restart_services.sh "${1:-restart}" || true

echo
echo "Leaving shell open so you can read output/logs."
echo "Log directory: $HOME/ai/logs"
echo "Type: exit  (to close)"
echo

# Replace this process with an interactive login shell
exec "$SHELL" -l
