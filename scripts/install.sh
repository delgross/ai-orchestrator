#!/bin/zsh

echo "=== Installing AI Gateway ==="

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "Creating venv with uv..."
uv venv .venv

echo "Installing dependencies..."
uv pip install fastapi uvicorn httpx pyyaml

echo "=== Installation complete ==="
