#!/usr/bin/env bash
set -euo pipefail

PORT=5460

echo "Checking for processes on port ${PORT}..."
PIDS=$(lsof -ti tcp:${PORT} || true)

if [ -n "${PIDS}" ]; then
  echo "Killing existing processes on port ${PORT}: ${PIDS}"
  kill ${PIDS} || true
  sleep 1
fi

# Optionally, double-check after a brief pause
PIDS_STILL=$(lsof -ti tcp:${PORT} || true)
if [ -n "${PIDS_STILL}" ]; then
  echo "Processes still on port ${PORT} after kill: ${PIDS_STILL}"
  echo "Sending SIGKILL..."
  kill -9 ${PIDS_STILL} || true
  sleep 1
fi

echo "Starting agent_runner on port ${PORT}..."

cd ~/ai
# activate venv
source .venv/bin/activate
# load env
if [ -f agent_runner/agent_runner.env ]; then
  source agent_runner/agent_runner.env
fi

exec uvicorn agent_runner.agent_runner:app \
  --host 127.0.0.1 \
  --port ${PORT} \
  --log-level info
