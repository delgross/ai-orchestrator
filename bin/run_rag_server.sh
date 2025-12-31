#!/bin/bash
# bin/run_rag_server.sh
cd "$(dirname "$0")/.."
source .venv/bin/activate 2>/dev/null || true
echo "Starting RAG Server..."
python3 rag_server.py
