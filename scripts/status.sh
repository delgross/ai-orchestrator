#!/usr/bin/env bash
set -euo pipefail

echo "== Ports =="
echo "-- Gateway (5455) --"
lsof -nP -iTCP:5455 -sTCP:LISTEN || true
echo
echo "-- Ollama (11434) --"
lsof -nP -iTCP:11434 -sTCP:LISTEN || true
