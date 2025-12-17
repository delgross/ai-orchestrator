#!/usr/bin/env bash
set -euo pipefail

U="$(id -u)"
GUI="gui/$U"
USR="user/$U"

RPL="$HOME/Library/LaunchAgents/local.ai.router.plist"
APL="$HOME/Library/LaunchAgents/local.ai.agent_runner.plist"

echo "== 1) bootout launchd jobs (both domains) =="
launchctl bootout "$GUI" "$RPL" 2>/dev/null || true
launchctl bootout "$GUI" "$APL" 2>/dev/null || true
launchctl bootout "$USR" "$RPL" 2>/dev/null || true
launchctl bootout "$USR" "$APL" 2>/dev/null || true

echo "== 2) kill anything holding ports 5455/5460 =="
lsof -ti tcp:5455 2>/dev/null | xargs -r kill -9 || true
lsof -ti tcp:5460 2>/dev/null | xargs -r kill -9 || true

echo "== 3) kill any stray uvicorns for these apps (covers races) =="
pkill -9 -f 'uvicorn .*router\.router:app' 2>/dev/null || true
pkill -9 -f 'uvicorn .*agent_runner:app' 2>/dev/null || true

sleep 1

echo "== 4) confirm ports are free =="
lsof -nP -iTCP:5455 -sTCP:LISTEN || echo "5455 free"
lsof -nP -iTCP:5460 -sTCP:LISTEN || echo "5460 free"

echo "Done."
