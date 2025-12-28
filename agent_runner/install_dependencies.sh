#!/bin/bash
# Install agent-runner dependencies

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Installing agent-runner dependencies..."
echo "Project root: $PROJECT_ROOT"

# Check for virtual environment (agent_runner uses .venv in agent_runner directory)
if [ -d "$SCRIPT_DIR/.venv" ]; then
    echo "Using .venv at $SCRIPT_DIR/.venv"
    source "$SCRIPT_DIR/.venv/bin/activate"
elif [ -d "$PROJECT_ROOT/venv" ]; then
    echo "Using venv at $PROJECT_ROOT/venv"
    source "$PROJECT_ROOT/venv/bin/activate"
elif [ -d "$PROJECT_ROOT/.venv" ]; then
    echo "Using .venv at $PROJECT_ROOT/.venv"
    source "$PROJECT_ROOT/.venv/bin/activate"
else
    echo "No virtual environment found. Creating one at $SCRIPT_DIR/.venv..."
    python3 -m venv "$SCRIPT_DIR/.venv"
    source "$SCRIPT_DIR/.venv/bin/activate"
    echo "Virtual environment created and activated"
fi

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing requirements from agent_runner/requirements.txt..."
pip install -r "$SCRIPT_DIR/requirements.txt"

# Verify installation
echo ""
echo "Verifying installation..."
python3 -c "import httpx; print('✓ httpx:', httpx.__version__)"
python3 -c "import fastapi; print('✓ fastapi:', fastapi.__version__)"
python3 -c "import uvicorn; print('✓ uvicorn:', uvicorn.__version__)"
python3 -c "import yaml; print('✓ pyyaml:', yaml.__version__)" 2>/dev/null || echo "⚠ pyyaml: optional (not installed)"

echo ""
echo "✓ Dependencies installed successfully!"

