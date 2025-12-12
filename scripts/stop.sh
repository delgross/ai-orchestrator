#!/usr/bin/env bash
set -euo pipefail

PORT="${AI_GATEWAY_PORT:-5455}"

PIDS="$(lsof -ti tcp:"$PORT" || true)"
if [[ -z "${PIDS}" ]]; then
  echo "No process listening on port ${PORT}"
  exit 0
fi

echo "Killing PIDs on port ${PORT}: ${PIDS}"
kill ${PIDS} || true
sleep 1

PIDS2="$(lsof -ti tcp:"$PORT" || true)"
if [[ -n "${PIDS2}" ]]; then
  echo "Force killing remaining PIDs: ${PIDS2}"
  kill -9 ${PIDS2} || true
fi
