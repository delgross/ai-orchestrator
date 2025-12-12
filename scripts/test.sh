#!/usr/bin/env bash
set -euo pipefail

PORT="${AI_GATEWAY_PORT:-5455}"
BASE="http://127.0.0.1:${PORT}"

echo "== Health =="
curl -sS "${BASE}/health" | python -m json.tool

echo
echo "== Models (first 20 lines) =="
curl -sS "${BASE}/v1/models" | python -m json.tool | head -n 20

echo
echo "== Chat (non-stream) =="
curl -sS "${BASE}/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{"model":"llama3:8b","messages":[{"role":"user","content":"Say OK"}]}' \
  | python -m json.tool

echo
echo "== Chat (stream: show first 15 lines) =="
curl -sS -N http://127.0.0.1:5455/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"llama3:8b","stream":true,"messages":[{"role":"user","content":"Reply with exactly: 1 2 3"}]}'
