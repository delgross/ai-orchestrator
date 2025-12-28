#!/bin/zsh
# Foolproof test runner for Antigravity AI Orchestrator

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Ensure we're using the project's virtual environment
VENV_PYTHON="./.venv/bin/python"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: Virtual environment not found at ./.venv"
    echo "Please run 'uv sync' in the ai/ directory first."
    exit 1
fi

echo "🚀 Running Antigravity Automated Tests..."
echo "----------------------------------------"

# Run pytest using the venv python to avoid globally installed issues
# We set PYTHONPATH to project root to ensure imports work correctly
PYTHONPATH=. "$VENV_PYTHON" -m pytest tests/unit tests/integration "$@"
