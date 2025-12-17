#!/usr/bin/env bash
set -euo pipefail
U="$(id -u)"
GUI="gui/$U"
LA="$HOME/Library/LaunchAgents"
RPL="$LA/local.ai.router.plist"
APL="$LA/local.ai.agent_runner.plist"

status() {
  echo "== launchd jobs (local.ai / ai) =="
  launchctl list | egrep '^(.*\t)?(local\.ai\.|ai\.)' || true
  echo
  echo "== ports 5455/5460 =="
  lsof -nP -iTCP:5455 -sTCP:LISTEN || echo "5455 free"
  lsof -nP -iTCP:5460 -sTCP:LISTEN || echo "5460 free"
}

conflicts() {
  echo "== conflicting live plists that mention 5455/5460/router/agent_runner =="
  grep -RIlE --binary-files=without-match \
    '5455|5460|router\.router:app|agent_runner:app' \
    "$LA" /Library/LaunchAgents /Library/LaunchDaemons 2>/dev/null \
    | egrep '\.plist$' || true
}

stop_all() {
  # stop both stacks (safe)
  launchctl bootout "$GUI/local.ai.router" 2>/dev/null || true
  launchctl bootout "$GUI/local.ai.agent_runner" 2>/dev/null || true
  launchctl bootout "$GUI/ai.gateway" 2>/dev/null || true
  launchctl bootout "$GUI/ai.agent_runner" 2>/dev/null || true
  launchctl bootout "user/$U/local.ai.router" 2>/dev/null || true
  launchctl bootout "user/$U/local.ai.agent_runner" 2>/dev/null || true
  launchctl bootout "user/$U/ai.gateway" 2>/dev/null || true
  launchctl bootout "user/$U/ai.agent_runner" 2>/dev/null || true

  lsof -ti tcp:5455 2>/dev/null | xargs -r kill -9 || true
  lsof -ti tcp:5460 2>/dev/null | xargs -r kill -9 || true
}

start_local() {
  # refuse to start if something already owns ports; print who
  for p in 5455 5460; do
    if lsof -ti tcp:$p >/dev/null 2>&1; then
      echo "ERROR: port $p already in use:"
      lsof -nP -iTCP:$p -sTCP:LISTEN || true
      exit 48
    fi
  done

  launchctl bootstrap "$GUI" "$RPL"
  launchctl bootstrap "$GUI" "$APL"
  launchctl kickstart -k "$GUI/local.ai.router"
  launchctl kickstart -k "$GUI/local.ai.agent_runner"
}

restart_local() {
  launchctl kickstart -k "$GUI/local.ai.router" || true
  launchctl kickstart -k "$GUI/local.ai.agent_runner" || true
}

case "${1:-}" in
  status) status ;;
  conflicts) conflicts ;;
  stop) stop_all; status ;;
  start) stop_all; start_local; status ;;
  restart) restart_local; status ;;
  *) echo "Usage: $0 {status|conflicts|stop|start|restart}"; exit 2 ;;
esac
