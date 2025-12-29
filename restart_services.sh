#!/usr/bin/env bash
set -Eeuo pipefail

USER_UID="$(id -u)"
ROUTER_LABEL="local.ai.router"
AGENT_LABEL="local.ai.agent_runner"

ROUTER_PLIST="$HOME/Library/LaunchAgents/${ROUTER_LABEL}.plist"
AGENT_PLIST="$HOME/Library/LaunchAgents/${AGENT_LABEL}.plist"

LOGDIR="$HOME/ai/logs"
mkdir -p "$LOGDIR"
LOGFILE="$LOGDIR/restart_$(date +%Y%m%d-%H%M%S).log"
exec > >(tee -a "$LOGFILE") 2>&1
echo "LOG: $LOGFILE"

on_err() {
  local ec=$?
  echo
  echo "ERROR: exit=$ec at line $1"
  echo "See: $LOGFILE"
  exit "$ec"
}
trap 'on_err $LINENO' ERR

# Pick a domain that actually works in this session.
DOMAIN="gui/$USER_UID"
if ! launchctl print "$DOMAIN" >/dev/null 2>&1; then
  DOMAIN="user/$USER_UID"
fi
echo "launchd DOMAIN: $DOMAIN"

usage() {
  cat <<EOF
Usage: $(basename "$0") [status|restart|restart-router|restart-agent|stop|start|logs]
EOF
}

is_loaded() {
  local label="$1"
  launchctl print "$DOMAIN/$label" >/dev/null 2>&1
}

ensure_loaded() {
  local label="$1"
  local plist="$2"
  [ -f "$plist" ] || { echo "Missing plist: $plist"; return 1; }
  if ! is_loaded "$label"; then
    launchctl bootstrap "$DOMAIN" "$plist"
  fi
}

restart_one() {
  local label="$1"
  local plist="$2"
  ensure_loaded "$label" "$plist"
  launchctl kickstart -k "$DOMAIN/$label"
}

status() {
  echo "=== launchctl print ==="
  launchctl print "$DOMAIN/$ROUTER_LABEL" 2>/dev/null | head -n 60 || echo "router not loaded"
  launchctl print "$DOMAIN/$AGENT_LABEL"  2>/dev/null | head -n 60 || echo "agent_runner not loaded"

  echo "=== listeners 5455/5460 ==="
  lsof -nP -iTCP:5455 -sTCP:LISTEN || true
  lsof -nP -iTCP:5460 -sTCP:LISTEN || true

  echo "=== health ==="
  curl -sS http://127.0.0.1:5455/ 2>/dev/null | python -m json.tool || echo "router not responding"
  curl -sS http://127.0.0.1:5460/ 2>/dev/null | python -m json.tool || echo "agent_runner not responding"
}

restart_router() {
  echo "=== restarting router ==="
  restart_one "$ROUTER_LABEL" "$ROUTER_PLIST"
  sleep 1
  curl -sS -H "Accept: application/json" http://127.0.0.1:5455/ | python -m json.tool
}

restart_agent() {
  echo "=== restarting agent_runner ==="
  restart_one "$AGENT_LABEL" "$AGENT_PLIST"
  sleep 5
  curl -sS -H "Accept: application/json" http://127.0.0.1:5460/ | python -m json.tool
}

restart_both() {
  restart_router
  restart_agent
}

stop_both() {
  echo "=== stopping services (bootout) ==="
  # bootout must use the same domain we used to load them
  [ -f "$ROUTER_PLIST" ] && launchctl bootout "$DOMAIN" "$ROUTER_PLIST" 2>/dev/null || true
  [ -f "$AGENT_PLIST" ]  && launchctl bootout "$DOMAIN" "$AGENT_PLIST" 2>/dev/null || true
  sleep 1
  echo "Stopped."
}

start_both() {
  echo "=== starting services (bootstrap + kickstart) ==="
  [ -f "$ROUTER_PLIST" ] || { echo "Missing: $ROUTER_PLIST"; return 1; }
  [ -f "$AGENT_PLIST" ]  || { echo "Missing: $AGENT_PLIST"; return 1; }

  launchctl bootstrap "$DOMAIN" "$ROUTER_PLIST"
  launchctl bootstrap "$DOMAIN" "$AGENT_PLIST"

  launchctl kickstart -k "$DOMAIN/$ROUTER_LABEL"
  launchctl kickstart -k "$DOMAIN/$AGENT_LABEL"

  sleep 1
  status
}

logs() {
  echo "=== launchd stderr logs ==="
  echo "--- router.err ---"
  tail -n 200 "$HOME/Library/Logs/ai/router.err.log" 2>/dev/null || true
  echo "--- agent_runner.err ---"
  tail -n 200 "$HOME/Library/Logs/ai/agent_runner.err.log" 2>/dev/null || true
}

cmd="${1:-restart}"
case "$cmd" in
  status) status ;;
  restart) restart_both ;;
  restart-router) restart_router ;;
  restart-agent) restart_agent ;;
  stop) stop_both ;;
  start) start_both ;;
  logs) logs ;;
  -h|--help|help) usage ;;
  *) echo "Unknown command: $cmd"; usage; exit 2 ;;
esac
