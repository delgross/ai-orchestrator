#!/usr/bin/env bash
# AI Orchestrator Management Script
# Checks what's running and starts/stops services as needed

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

ROUTER_PORT=5455
AGENT_PORT=5460
ROUTER_LABEL="local.ai.router"
AGENT_LABEL="local.ai.agent_runner"
ROUTER_PLIST="$HOME/Library/LaunchAgents/${ROUTER_LABEL}.plist"
AGENT_PLIST="$HOME/Library/LaunchAgents/${AGENT_LABEL}.plist"

# Detect launchd domain
USER_UID="$(id -u)"
DOMAIN="gui/$USER_UID"
if ! launchctl print "$DOMAIN" >/dev/null 2>&1; then
  DOMAIN="user/$USER_UID"
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if a port is in use
port_in_use() {
  local port=$1
  lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1
}

# Check if a launchd job is loaded
job_loaded() {
  local label=$1
  launchctl print "$DOMAIN/$label" >/dev/null 2>&1
}

# Check if a service is responding via HTTP
service_responding() {
  local url=$1
  curl -sSf "$url" >/dev/null 2>&1
}

# Get PID using a port
get_port_pid() {
  local port=$1
  lsof -t -nP -iTCP:"$port" -sTCP:LISTEN 2>/dev/null || echo ""
}

# Check router status
check_router() {
  local port_ok=false
  local http_ok=false
  local launchd_ok=false
  local pid=""
  
  if port_in_use "$ROUTER_PORT"; then
    port_ok=true
    pid=$(get_port_pid "$ROUTER_PORT")
  fi
  
  if service_responding "http://127.0.0.1:$ROUTER_PORT/"; then
    http_ok=true
  fi
  
  if job_loaded "$ROUTER_LABEL"; then
    launchd_ok=true
  fi
  
  echo "$port_ok|$http_ok|$launchd_ok|$pid"
}

# Check agent-runner status
check_agent() {
  local port_ok=false
  local http_ok=false
  local launchd_ok=false
  local pid=""
  
  if port_in_use "$AGENT_PORT"; then
    port_ok=true
    pid=$(get_port_pid "$AGENT_PORT")
  fi
  
  if service_responding "http://127.0.0.1:$AGENT_PORT/"; then
    http_ok=true
  fi
  
  if job_loaded "$AGENT_LABEL"; then
    launchd_ok=true
  fi
  
  echo "$port_ok|$http_ok|$launchd_ok|$pid"
}

# Show status
show_status() {
  echo -e "${BLUE}=== AI Orchestrator Status ===${NC}\n"
  
  # Router
  local router_status=$(check_router)
  IFS='|' read -r router_port router_http router_launchd router_pid <<< "$router_status"
  
  echo -n "Router (port $ROUTER_PORT): "
  if [ "$router_http" = "true" ]; then
    echo -e "${GREEN}✓ Running${NC}"
    if [ -n "$router_pid" ]; then
      echo "  PID: $router_pid"
    fi
    if [ "$router_launchd" = "true" ]; then
      echo "  Managed by: launchd"
    else
      echo "  Managed by: direct process"
    fi
  elif [ "$router_port" = "true" ]; then
    echo -e "${YELLOW}⚠ Port in use but not responding${NC}"
    if [ -n "$router_pid" ]; then
      echo "  PID: $router_pid (may be stuck)"
    fi
  else
    echo -e "${RED}✗ Not running${NC}"
  fi
  
  # Agent-runner
  local agent_status=$(check_agent)
  IFS='|' read -r agent_port agent_http agent_launchd agent_pid <<< "$agent_status"
  
  echo -n "Agent-runner (port $AGENT_PORT): "
  if [ "$agent_http" = "true" ]; then
    echo -e "${GREEN}✓ Running${NC}"
    if [ -n "$agent_pid" ]; then
      echo "  PID: $agent_pid"
    fi
    if [ "$agent_launchd" = "true" ]; then
      echo "  Managed by: launchd"
    else
      echo "  Managed by: direct process"
    fi
  elif [ "$agent_port" = "true" ]; then
    echo -e "${YELLOW}⚠ Port in use but not responding${NC}"
    if [ -n "$agent_pid" ]; then
      echo "  PID: $agent_pid (may be stuck)"
    fi
  else
    echo -e "${RED}✗ Not running${NC}"
  fi
  
  echo ""
  
  # Health check
  if [ "$router_http" = "true" ] && [ "$agent_http" = "true" ]; then
    echo -e "${GREEN}✓ All services healthy${NC}"
    echo ""
    echo "Dashboard: http://127.0.0.1:$ROUTER_PORT/dashboard"
    echo "Router API: http://127.0.0.1:$ROUTER_PORT/"
    echo "Agent API: http://127.0.0.1:$AGENT_PORT/"
  elif [ "$router_http" = "true" ] || [ "$agent_http" = "true" ]; then
    echo -e "${YELLOW}⚠ Partial service availability${NC}"
  else
    echo -e "${RED}✗ Services not available${NC}"
  fi
}

# Start router
start_router() {
  if [ -f "$ROUTER_PLIST" ]; then
    echo "Starting router via launchd..."
    if ! job_loaded "$ROUTER_LABEL"; then
      launchctl bootstrap "$DOMAIN" "$ROUTER_PLIST" 2>/dev/null || true
    fi
    launchctl kickstart -k "$DOMAIN/$ROUTER_LABEL" 2>/dev/null || true
    sleep 2
  else
    echo -e "${YELLOW}Warning: launchd plist not found at $ROUTER_PLIST${NC}"
    echo "Run './setup_launchd.sh' first to create plists."
    return 1
  fi
}

# Start agent-runner
start_agent() {
  if [ -f "$AGENT_PLIST" ]; then
    echo "Starting agent-runner via launchd..."
    if ! job_loaded "$AGENT_LABEL"; then
      launchctl bootstrap "$DOMAIN" "$AGENT_PLIST" 2>/dev/null || true
    fi
    launchctl kickstart -k "$DOMAIN/$AGENT_LABEL" 2>/dev/null || true
    sleep 2
  else
    echo -e "${YELLOW}Warning: launchd plist not found at $AGENT_PLIST${NC}"
    echo "Run './setup_launchd.sh' first to create plists."
    return 1
  fi
}

# Stop router
stop_router() {
  local router_status=$(check_router)
  IFS='|' read -r router_port router_http router_launchd router_pid <<< "$router_status"
  
  if [ "$router_launchd" = "true" ]; then
    echo "Stopping router via launchd..."
    launchctl bootout "$DOMAIN" "$ROUTER_PLIST" 2>/dev/null || true
    sleep 1
  fi
  
  if [ "$router_port" = "true" ] && [ -n "$router_pid" ]; then
    echo "Killing router process (PID: $router_pid)..."
    kill "$router_pid" 2>/dev/null || true
    sleep 1
    if port_in_use "$ROUTER_PORT"; then
      echo "Force killing..."
      kill -9 "$router_pid" 2>/dev/null || true
    fi
  fi
}

# Stop agent-runner
stop_agent() {
  local agent_status=$(check_agent)
  IFS='|' read -r agent_port agent_http agent_launchd agent_pid <<< "$agent_status"
  
  if [ "$agent_launchd" = "true" ]; then
    echo "Stopping agent-runner via launchd..."
    launchctl bootout "$DOMAIN" "$AGENT_PLIST" 2>/dev/null || true
    sleep 1
  fi
  
  if [ "$agent_port" = "true" ] && [ -n "$agent_pid" ]; then
    echo "Killing agent-runner process (PID: $agent_pid)..."
    kill "$agent_pid" 2>/dev/null || true
    sleep 1
    if port_in_use "$AGENT_PORT"; then
      echo "Force killing..."
      kill -9 "$agent_pid" 2>/dev/null || true
    fi
  fi
}

# Start all services
start_all() {
  echo -e "${BLUE}Starting AI Orchestrator services...${NC}\n"
  
  local router_status=$(check_router)
  IFS='|' read -r router_port router_http router_launchd router_pid <<< "$router_status"
  
  local agent_status=$(check_agent)
  IFS='|' read -r agent_port agent_http agent_launchd agent_pid <<< "$agent_status"
  
  if [ "$router_http" = "true" ]; then
    echo -e "${GREEN}Router already running${NC}"
  else
    start_router
  fi
  
  if [ "$agent_http" = "true" ]; then
    echo -e "${GREEN}Agent-runner already running${NC}"
  else
    start_agent
  fi
  
  echo ""
  sleep 2
  show_status
}

# Stop all services
stop_all() {
  echo -e "${BLUE}Stopping AI Orchestrator services...${NC}\n"
  stop_router
  stop_agent
  echo ""
  sleep 1
  show_status
}

# Restart all services
restart_all() {
  echo -e "${BLUE}Restarting AI Orchestrator services...${NC}\n"
  stop_all
  sleep 2
  start_all
}

# Ensure all services are running (start what's missing)
ensure_running() {
  echo -e "${BLUE}Ensuring all services are running...${NC}\n"
  
  local router_status=$(check_router)
  IFS='|' read -r router_port router_http router_launchd router_pid <<< "$router_status"
  
  local agent_status=$(check_agent)
  IFS='|' read -r agent_port agent_http agent_launchd agent_pid <<< "$agent_status"
  
  if [ "$router_http" != "true" ]; then
    echo "Router not running, starting..."
    start_router
  else
    echo -e "${GREEN}Router already running${NC}"
  fi
  
  if [ "$agent_http" != "true" ]; then
    echo "Agent-runner not running, starting..."
    start_agent
  else
    echo -e "${GREEN}Agent-runner already running${NC}"
  fi
  
  echo ""
  sleep 2
  show_status
}

# Usage
usage() {
  cat <<EOF
Usage: $0 [command]

Commands:
  status       Show status of all services (default)
  start        Start all services
  stop         Stop all services
  restart      Restart all services
  ensure       Start any missing services (keeps running services running)
  start-router Start only the router
  stop-router  Stop only the router
  start-agent  Start only the agent-runner
  stop-agent   Stop only the agent-runner

Examples:
  $0              # Show status
  $0 ensure       # Start what's missing
  $0 restart      # Full restart
  $0 stop         # Stop everything
EOF
}

# Main
cmd="${1:-status}"
case "$cmd" in
  status)
    show_status
    ;;
  start)
    start_all
    ;;
  stop)
    stop_all
    ;;
  restart)
    restart_all
    ;;
  ensure)
    ensure_running
    ;;
  start-router)
    start_router
    show_status
    ;;
  stop-router)
    stop_router
    show_status
    ;;
  start-agent)
    start_agent
    show_status
    ;;
  stop-agent)
    stop_agent
    show_status
    ;;
  -h|--help|help)
    usage
    ;;
  *)
    echo "Unknown command: $cmd"
    echo ""
    usage
    exit 2
    ;;
esac






