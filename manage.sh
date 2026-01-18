#!/usr/bin/env bash
# AI Orchestrator Management Script
# Checks what's running and starts/stops services as needed

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# Prefer project venv for python utilities (e.g., get_config needs PyYAML)
if [ -x "$ROOT_DIR/.venv/bin/python3" ]; then
  export PATH="$ROOT_DIR/.venv/bin:$PATH"
fi

# [SOVEREIGN] Retrieve Ports from Registry
ROUTER_PORT=$(python3 bin/get_config.py network.router_port 5455)
AGENT_PORT=$(python3 bin/get_config.py network.agent_port 5460)
SURREAL_PORT=$(python3 bin/get_config.py network.surreal_port 8000)
RAG_PORT=$(python3 bin/get_config.py network.rag_port 5555)

ROUTER_LABEL="local.ai.router"
AGENT_LABEL="local.ai.agent_runner"
SURREAL_LABEL="local.ai.surrealdb"
ROUTER_PLIST="$HOME/Library/LaunchAgents/${ROUTER_LABEL}.plist"
AGENT_PLIST="$HOME/Library/LaunchAgents/${AGENT_LABEL}.plist"
SURREAL_PLIST="$HOME/Library/LaunchAgents/${SURREAL_LABEL}.plist"
SURREAL_BIN="$HOME/.surrealdb/surreal"
SURREAL_DATA_DIR="$HOME/ai/agent_data/surreal_db"

RAG_LABEL="local.ai.rag_server"
RAG_PLIST="$HOME/Library/LaunchAgents/${RAG_LABEL}.plist"

# Detect launchd domain
USER_UID="$(id -u)"
DOMAIN="gui/$USER_UID"
if ! launchctl print "$DOMAIN" >/dev/null 2>&1; then
  DOMAIN="user/$USER_UID"
fi

# Detect if we're in a sandbox environment (check for common restrictions)
detect_sandbox() {
  # Check if we can access system launchd
  if ! launchctl print "$DOMAIN" >/dev/null 2>&1; then
    return 0  # In sandbox
  fi

  # Check if we can bootstrap services (common sandbox restriction)
  if ! launchctl bootstrap "$DOMAIN" /dev/null 2>/dev/null; then
    return 0  # In sandbox
  fi

  # Check for other sandbox indicators
  if [ -n "$SANDBOXED" ] || [ "$USER" != "bee" ] || ! pgrep -x "Finder" >/dev/null 2>&1; then
    return 0  # In sandbox
  fi

  return 1  # Not in sandbox
}

# Check if we're in sandbox
IN_SANDBOX=false
if detect_sandbox; then
  IN_SANDBOX=true
  echo "🔒 Sandbox environment detected - using direct process management"
else
  echo "🖥️  Production environment detected - using launchd service management"
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if a port is in use
port_in_use() {
  local port=$1
  if [ "$IN_SANDBOX" = "true" ]; then
    # In sandbox, just check if service responds (simpler approach)
    curl -s --max-time 1 "http://127.0.0.1:$port/health" >/dev/null 2>&1
  else
    lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1
  fi
}

# Check if a launchd job is loaded
job_loaded() {
  local label=$1
  launchctl print "$DOMAIN/$label" >/dev/null 2>&1
}

# Check if a service is responding via HTTP
service_responding() {
  local url=$1
  local timeout=${2:-2}  # Default 2 second timeout, can be overridden
  curl -sSf --max-time "$timeout" "$url" >/dev/null 2>&1
}

# Wait for a service to become healthy
wait_for_health() {
  local url=$1
  local name=$2
  local max_attempts=${3:-30} # Default 30 attempts (30s)
  
  echo -n "⏳ Waiting for $name to be ready..."
  local attempts=0
  while [ $attempts -lt $max_attempts ]; do
    if service_responding "$url" 1; then
      echo -e "${GREEN} Done.${NC}"
      return 0
    fi
    sleep 1
    attempts=$((attempts + 1))
    echo -n "."
  done
  
  echo -e "${RED} Timeout!${NC}"
  return 1
}

# Get PID using a port
get_port_pid() {
  local port=$1
  if [ "$IN_SANDBOX" = "true" ]; then
    echo ""  # PID not available in sandbox mode
  else
    lsof -t -nP -iTCP:"$port" -sTCP:LISTEN 2>/dev/null || echo ""
  fi
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
  
  if service_responding "http://127.0.0.1:$AGENT_PORT/health" 3; then
    http_ok=true
  fi
  
  if job_loaded "$AGENT_LABEL"; then
    launchd_ok=true
  fi
  
  echo "$port_ok|$http_ok|$launchd_ok|$pid"
}

# Check SurrealDB status
check_surreal() {
  local port_ok=false
  local http_ok=false
  local launchd_ok=false
  local pid=""
  
  if port_in_use "$SURREAL_PORT"; then
    port_ok=true
    pid=$(get_port_pid "$SURREAL_PORT")
  fi
  
  if service_responding "http://127.0.0.1:$SURREAL_PORT/health"; then
    http_ok=true
  fi
  
  if job_loaded "$SURREAL_LABEL"; then
    launchd_ok=true
  fi
  
  echo "$port_ok|$http_ok|$launchd_ok|$pid"
}

# Check RAG status
check_rag() {
  local port_ok=false
  local http_ok=false
  local launchd_ok=false
  local pid=""

  if port_in_use "$RAG_PORT"; then
    port_ok=true
    pid=$(get_port_pid "$RAG_PORT")
  fi

  if service_responding "http://127.0.0.1:$RAG_PORT/health"; then
    http_ok=true
  fi

  if job_loaded "$RAG_LABEL"; then
    launchd_ok=true
  fi

  echo "$port_ok|$http_ok|$launchd_ok|$pid"
}

# Check Ollama status
check_ollama() {
  local http_ok=false
  local pid=""

  # Check if Ollama API is responding
  if service_responding "http://127.0.0.1:11434/api/tags" 3; then
    http_ok=true
  fi

  # Try to find Ollama process (this is a best effort in sandbox)
  pid=$(pgrep -f "ollama serve" 2>/dev/null || echo "")

  echo "true|$http_ok|true|$pid"  # Always consider port "true" since it's not a fixed port check
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

  # SurrealDB
  local surreal_status=$(check_surreal)
  IFS='|' read -r surreal_port surreal_http surreal_launchd surreal_pid <<< "$surreal_status"
  
  echo -n "SurrealDB (port $SURREAL_PORT): "
  if [ "$surreal_http" = "true" ]; then
    echo -e "${GREEN}✓ Running${NC}"
    if [ -n "$surreal_pid" ]; then
      echo "  PID: $surreal_pid"
    fi
    if [ "$surreal_launchd" = "true" ]; then
      echo "  Managed by: launchd"
    else
      echo "  Managed by: direct process"
    fi
  elif [ "$surreal_port" = "true" ]; then
    echo -e "${YELLOW}⚠ Port in use but not responding${NC}"
    if [ -n "$surreal_pid" ]; then
      echo "  PID: $surreal_pid (may be stuck)"
    fi
  else
    echo -e "${RED}✗ Not running${NC}"
  fi

  # RAG-server
  local rag_status=$(check_rag)
  IFS='|' read -r rag_port rag_http rag_launchd rag_pid <<< "$rag_status"
  
  echo -n "RAG-server (port $RAG_PORT): "
  if [ "$rag_http" = "true" ]; then
    echo -e "${GREEN}✓ Running${NC}"
    if [ -n "$rag_pid" ]; then
      echo "  PID: $rag_pid"
    fi
  elif [ "$rag_port" = "true" ]; then
    echo -e "${YELLOW}⚠ Port in use but not responding${NC}"
  else
    echo -e "${RED}✗ Not running${NC}"
  fi

  # Ollama
  local ollama_status=$(check_ollama)
  IFS='|' read -r ollama_port ollama_http ollama_launchd ollama_pid <<< "$ollama_status"

  echo -n "Ollama (port 11434): "
  if [ "$ollama_http" = "true" ]; then
    echo -e "${GREEN}✓ Running${NC}"
    if [ -n "$ollama_pid" ]; then
      echo "  PID: $ollama_pid"
    fi
  else
    echo -e "${RED}✗ Not running${NC}"
  fi

  echo ""
  
  # Health check
  if [ "$router_http" = "true" ] && [ "$agent_http" = "true" ] && [ "$surreal_http" = "true" ] && [ "$ollama_http" = "true" ]; then
    echo -e "${GREEN}✓ All services healthy${NC}"
    
    # Check if dashboard is reachable (check HTTP status code)
    if curl -sf -o /dev/null -w "%{http_code}" "http://127.0.0.1:$ROUTER_PORT/v2/index.html" | grep -q "200" 2>/dev/null; then
      echo -e "Dashboard: ${GREEN}✓ Available${NC} (http://127.0.0.1:$ROUTER_PORT/v2/index.html)"
    else
      echo -e "Dashboard: ${RED}✗ Not responding correctly${NC}"
    fi
    
    echo "Router API: http://127.0.0.1:$ROUTER_PORT/"
    echo "Agent API: http://127.0.0.1:$AGENT_PORT/"
    echo "SurrealDB: http://127.0.0.1:$SURREAL_PORT/"
  elif [ "$router_http" = "true" ] || [ "$agent_http" = "true" ] || [ "$surreal_http" = "true" ]; then
    echo -e "${YELLOW}⚠ Partial service availability${NC}"
  else
    echo -e "${RED}✗ Services not available${NC}"
  fi
}

# Start router
start_router() {
  if [ "$IN_SANDBOX" = "true" ]; then
    # SANDBOX MODE: Start router directly
    echo "Starting router (sandbox mode)..."
    if service_responding "http://127.0.0.1:$ROUTER_PORT/health" 1; then
      echo -e "${GREEN}Router already running${NC}"
      return 0
    fi

    # Ensure logs directory exists
    mkdir -p logs

    # Start router in background
    PYTHONPATH=. nohup python -m uvicorn router.main:app --host 127.0.0.1 --port 5455 --log-level info > logs/router.log 2>&1 &
    local router_pid=$!
    echo $router_pid > /tmp/ai_router.pid 2>/dev/null || true

    # Wait for startup (longer timeout for sandbox)
    local attempts=0
    while [ $attempts -lt 15 ]; do
      if curl -s http://127.0.0.1:5455/health > /dev/null 2>&1; then
        echo -e "${GREEN}Router started successfully (PID: $router_pid)${NC}"
        return 0
      fi
      sleep 1
      attempts=$((attempts + 1))
    done

    echo -e "${RED}Router failed to start within 15 seconds${NC}"
    return 1
  else
    # PRODUCTION MODE: Try launchd first, fallback to direct
    echo "Starting router via launchd..."
    if [ -f "$ROUTER_PLIST" ]; then
      if ! job_loaded "$ROUTER_LABEL"; then
        launchctl bootstrap "$DOMAIN" "$ROUTER_PLIST" 2>/dev/null || {
          echo "Launchd failed, falling back to direct start..."
          start_router_direct
          return $?
        }
      fi
      launchctl kickstart -k "$DOMAIN/$ROUTER_LABEL" 2>/dev/null || {
        echo "Launchd kickstart failed, falling back to direct start..."
        start_router_direct
        return $?
      }
      sleep 2
    else
      echo -e "${YELLOW}Warning: launchd plist not found, using direct start${NC}"
      start_router_direct
    fi
  fi
}

# Direct router start (fallback)
start_router_direct() {
  if [ "$IN_SANDBOX" = "true" ]; then
    if service_responding "http://127.0.0.1:$ROUTER_PORT/health" 1; then
      echo -e "${GREEN}Router already running${NC}"
      return 0
    fi
  else
    if pgrep -f "uvicorn.*router.*5455" > /dev/null; then
      echo -e "${GREEN}Router already running${NC}"
      return 0
    fi
  fi

  mkdir -p logs
  PYTHONPATH=. nohup python -m uvicorn router.main:app --host 127.0.0.1 --port 5455 --log-level info > logs/router.log 2>&1 &
  local router_pid=$!
  echo $router_pid > /tmp/ai_router.pid 2>/dev/null || true

  # Wait for startup
  local attempts=0
  while [ $attempts -lt 10 ]; do
    if curl -s http://127.0.0.1:5455/health > /dev/null 2>&1; then
      echo -e "${GREEN}Router started successfully (PID: $router_pid)${NC}"
      return 0
    fi
    sleep 1
    attempts=$((attempts + 1))
  done

  echo -e "${RED}Router failed to start within 10 seconds${NC}"
  return 1
}

# Start agent-runner
start_agent() {
  if [ "$IN_SANDBOX" = "true" ]; then
    # SANDBOX MODE: Start agent-runner directly
    echo "Starting agent-runner (sandbox mode)..."
    if service_responding "http://127.0.0.1:$AGENT_PORT/health" 1; then
      echo -e "${GREEN}Agent-runner already running${NC}"
      return 0
    fi

    # Ensure logs directory exists
    mkdir -p logs

    # Start agent-runner in background
    PYTHONPATH="$ROOT_DIR${PYTHONPATH:+:$PYTHONPATH}" nohup python -m agent_runner.main > logs/agent_runner.log 2>&1 &
    local agent_pid=$!
    echo $agent_pid > /tmp/ai_agent.pid 2>/dev/null || true

    # Wait for startup (agent takes longer to initialize)
    local attempts=0
    while [ $attempts -lt 30 ]; do
      if curl -s http://127.0.0.1:5460/health > /dev/null 2>&1; then
        echo -e "${GREEN}Agent-runner started successfully (PID: $agent_pid)${NC}"
        return 0
      fi
      sleep 1
      attempts=$((attempts + 1))
    done

    echo -e "${RED}Agent-runner failed to start within 30 seconds${NC}"
    return 1
  else
    # PRODUCTION MODE: Try launchd first, fallback to direct
    echo "Starting agent-runner via launchd..."
    if [ -f "$AGENT_PLIST" ]; then
      if ! job_loaded "$AGENT_LABEL"; then
        launchctl bootstrap "$DOMAIN" "$AGENT_PLIST" 2>/dev/null || {
          echo "Launchd failed, falling back to direct start..."
          start_agent_direct
          return $?
        }
      fi
      launchctl kickstart -k "$DOMAIN/$AGENT_LABEL" 2>/dev/null || {
        echo "Launchd kickstart failed, falling back to direct start..."
        start_agent_direct
        return $?
      }
      sleep 5  # Agent takes longer to start
    else
      echo -e "${YELLOW}Warning: launchd plist not found, using direct start${NC}"
      start_agent_direct
    fi
  fi
}

# Direct agent-runner start (fallback)
start_agent_direct() {
  if [ "$IN_SANDBOX" = "true" ]; then
    if service_responding "http://127.0.0.1:$AGENT_PORT/health" 1; then
      echo -e "${GREEN}Agent-runner already running${NC}"
      return 0
    fi
  else
    if pgrep -f "agent_runner.*main" > /dev/null; then
      echo -e "${GREEN}Agent-runner already running${NC}"
      return 0
    fi
  fi

  PYTHONPATH="$ROOT_DIR${PYTHONPATH:+:$PYTHONPATH}" nohup python -m agent_runner.main > logs/agent_runner.log 2>&1 &
  local agent_pid=$!
  echo $agent_pid > /tmp/ai_agent.pid 2>/dev/null || true

  # Wait for startup
  local attempts=0
  while [ $attempts -lt 25 ]; do
    if curl -s http://127.0.0.1:5460/health > /dev/null 2>&1; then
      echo -e "${GREEN}Agent-runner started successfully (PID: $agent_pid)${NC}"
      return 0
    fi
    sleep 1
    attempts=$((attempts + 1))
  done

  echo -e "${RED}Agent-runner failed to start within 25 seconds${NC}"
  return 1
}

# Start RAG-server
start_rag() {
  echo "Starting RAG-server..."
  # Use the shared project venv
  nohup "$ROOT_DIR/.venv/bin/python3" rag_server.py > "$ROOT_DIR/logs/rag.log" 2>&1 &
  sleep 2
}

# Start Ollama
start_ollama() {
  echo "Starting Ollama..."
  if command -v ollama >/dev/null 2>&1; then
    if [ "$IN_SANDBOX" = "true" ]; then
      # SANDBOX MODE: Start Ollama directly
      if pgrep -f "ollama serve" > /dev/null; then
        echo -e "${GREEN}Ollama already running${NC}"
        return 0
      fi

      echo "Starting Ollama directly (sandbox mode)..."
      nohup ollama serve > "$ROOT_DIR/logs/ollama.log" 2>&1 &
      sleep 3

      # Verify Ollama is responding
      if service_responding "http://127.0.0.1:11434/api/tags" 5; then
        echo -e "${GREEN}Ollama started successfully${NC}"
        return 0
      else
        echo -e "${YELLOW}Ollama started but not yet responding, continuing...${NC}"
        return 0
      fi
    else
      # PRODUCTION MODE: Try launchd first
      if [ -f "$HOME/Library/LaunchAgents/homebrew.mxcl.ollama.plist" ]; then
        echo "Starting Ollama via launchd..."
        launchctl load "$HOME/Library/LaunchAgents/homebrew.mxcl.ollama.plist" 2>/dev/null || {
          echo "Launchd failed, falling back to direct start..."
          start_ollama_direct
          return $?
        }
        sleep 3
      else
        start_ollama_direct
      fi

      # Verify Ollama is responding
      if service_responding "http://127.0.0.1:11434/api/tags" 3; then
        echo -e "${GREEN}Ollama started successfully${NC}"
        return 0
      else
        echo -e "${YELLOW}Ollama started but not yet responding, continuing...${NC}"
        return 0
      fi
    fi
  else
    echo -e "${RED}Ollama command not found${NC}"
    return 1
  fi
}

# Direct Ollama start (fallback)
start_ollama_direct() {
  if pgrep -f "ollama serve" > /dev/null; then
    echo -e "${GREEN}Ollama already running${NC}"
    return 0
  fi

  nohup ollama serve > "$ROOT_DIR/logs/ollama.log" 2>&1 &
  sleep 3
}

# Stop Ollama
stop_ollama() {
  echo "Stopping Ollama..."
  if [ -f "$HOME/Library/LaunchAgents/homebrew.mxcl.ollama.plist" ]; then
    echo "Stopping Ollama via launchd..."
    launchctl unload "$HOME/Library/LaunchAgents/homebrew.mxcl.ollama.plist" 2>/dev/null || true
  fi

  # Kill any running Ollama processes
  pkill -f "ollama serve" 2>/dev/null || true
  sleep 2
}

# Start SurrealDB
start_surreal() {
  # Resolve Surreal binary location
  if [ ! -x "$SURREAL_BIN" ]; then
    if command -v surreal >/dev/null 2>&1; then
      SURREAL_BIN="$(command -v surreal)"
    elif [ -x "$HOME/.surrealdb/surreal" ]; then
      SURREAL_BIN="$HOME/.surrealdb/surreal"
    else
      echo "SurrealDB binary not found. Install it or set SURREAL_BIN to the executable path."
      return 1
    fi
  fi

  if [ -f "$SURREAL_PLIST" ]; then
    echo "Starting SurrealDB via launchd..."
    if ! job_loaded "$SURREAL_LABEL"; then
      launchctl bootstrap "$DOMAIN" "$SURREAL_PLIST" 2>/dev/null || true
    fi
    launchctl kickstart -k "$DOMAIN/$SURREAL_LABEL" 2>/dev/null || true
    sleep 2
  else
    echo "Starting SurrealDB directly..."
    mkdir -p "$SURREAL_DATA_DIR"
    "$SURREAL_BIN" start --user root --pass root "file:$SURREAL_DATA_DIR" --bind 127.0.0.1:$SURREAL_PORT > "$ROOT_DIR/logs/surreal.log" 2>&1 &
    sleep 2
  fi
}

# Stop router
# Stop router
stop_router() {
  # MANUAL MANAGEMENT: Stop router directly
  echo "Stopping router manually..."

  # Check if PID file exists and kill that process
  if [ -f "/tmp/ai_router.pid" ]; then
    local saved_pid=$(cat /tmp/ai_router.pid)
    if kill -0 "$saved_pid" 2>/dev/null; then
      echo "Stopping router (PID: $saved_pid)..."
      kill "$saved_pid" 2>/dev/null || true
      rm -f /tmp/ai_router.pid
    else
      rm -f /tmp/ai_router.pid
    fi
  fi

  # Fallback: Kill any router processes
  local pids=$(pgrep -f "uvicorn.*router.*5455" || true)
  if [ -n "$pids" ]; then
    echo "Force killing remaining router processes..."
    echo "$pids" | xargs kill -9 2>/dev/null || true
  fi

  # Wait for port to be free
  local attempts=0
  while [ $attempts -lt 5 ]; do
    if ! port_in_use "$ROUTER_PORT"; then
      echo -e "${GREEN}Router stopped successfully${NC}"
      return 0
    fi
    sleep 1
    attempts=$((attempts + 1))
  done

  echo -e "${RED}Router may still be running${NC}"
}

# Stop agent-runner
# Stop agent-runner
stop_agent() {
  local agent_status=$(check_agent)
  IFS='|' read -r agent_port agent_http agent_launchd agent_pid <<< "$agent_status"
  
  # 1. Try launchd stop
  if [ "$agent_launchd" = "true" ]; then
    echo "Stopping agent-runner via launchd..."
    launchctl bootout "$DOMAIN" "$AGENT_PLIST" 2>/dev/null || true
    # Wait for it to die (up to 5s)
    for i in {1..10}; do
      if ! port_in_use "$AGENT_PORT"; then break; fi
      sleep 0.5
    done
  fi
  
  # 2. Check if still alive (Zombie or Manual Process)
  if port_in_use "$AGENT_PORT"; then
    local current_pid=$(get_port_pid "$AGENT_PORT")
    if [ -n "$current_pid" ]; then
      echo "Process still running (PID: $current_pid). Sending SIGTERM..."
      kill "$current_pid" 2>/dev/null || true
      
      # Wait again
      for i in {1..6}; do
        if ! port_in_use "$AGENT_PORT"; then break; fi
        sleep 0.5
      done
      
      # 3. Force Kill
      if port_in_use "$AGENT_PORT"; then
        echo "Force killing stuck process..."
        kill -9 "$current_pid" 2>/dev/null || true
      fi
    fi
  fi
}

# Stop SurrealDB
stop_surreal() {
  local surreal_status=$(check_surreal)
  IFS='|' read -r surreal_port surreal_http surreal_launchd surreal_pid <<< "$surreal_status"
  
  if [ "$surreal_launchd" = "true" ]; then
    echo "Stopping SurrealDB via launchd..."
    launchctl bootout "$DOMAIN" "$SURREAL_PLIST" 2>/dev/null || true
    sleep 1
  fi
  
  if [ "$surreal_port" = "true" ] && [ -n "$surreal_pid" ]; then
    echo "Killing SurrealDB process (PID: $surreal_pid)..."
    kill "$surreal_pid" 2>/dev/null || true
    sleep 1
    if port_in_use "$SURREAL_PORT"; then
      echo "Force killing..."
      kill -9 "$surreal_pid" 2>/dev/null || true
    fi
  fi
}

# Stop RAG-server
stop_rag() {
  local rag_status=$(check_rag)
  IFS='|' read -r rag_port rag_http rag_launchd rag_pid <<< "$rag_status"
  
  if [ -n "$rag_pid" ]; then
    echo "Stopping RAG-server (PID: $rag_pid)..."
    kill "$rag_pid" 2>/dev/null || true
    sleep 1
  fi
}

# Temporarily disable KeepAlive for clean restarts
disable_keepalive() {
  local plist=$1
  if [ -f "$plist" ]; then
    echo "Temporarily disabling KeepAlive for $plist..."
    # Remove KeepAlive key temporarily
    plutil -remove KeepAlive "$plist" 2>/dev/null || true
    launchctl unload "$plist" 2>/dev/null || true
    launchctl load "$plist" 2>/dev/null || true
  fi
}

# Restore KeepAlive after restart
restore_keepalive() {
  local plist=$1
  if [ -f "$plist" ]; then
    echo "Restoring KeepAlive for $plist..."
    plutil -insert KeepAlive -bool YES "$plist" 2>/dev/null || true
    launchctl unload "$plist" 2>/dev/null || true
    launchctl load "$plist" 2>/dev/null || true
  fi
}

# Warm key models so Ollama keeps them hot (honors ~/.ollama/config keep_alive)
warm_models() {
  # Skip if Ollama unavailable
  if ! command -v ollama >/dev/null 2>&1; then
    echo "Skipping warm: ollama not installed"
    return 0
  fi

  # Wait (short) for Ollama API readiness so we don't silently skip warming
  local ready=false
  for _ in {1..30}; do
    if service_responding "http://127.0.0.1:11434/api/tags" 2; then
      ready=true
      break
    fi
    sleep 1
  done

  if [ "$ready" != "true" ]; then
    echo "Skipping warm: ollama API not responding"
    return 0
  fi

  # Keep warm logs inside repo so we can inspect from tooling
  local warm_log_dir="$ROOT_DIR/logs/warm"
  mkdir -p "$warm_log_dir"

  echo "Warming models (qwen2.5:32b, qwen2.5-coder:32b, llama3.3:70b)..."

  local keepalive="${OLLAMA_KEEP_ALIVE:-2h}"

  # Background warm for the 32B models (fast enough, non-blocking)
  local bg_models=("qwen2.5:32b" "qwen2.5-coder:32b")
  for m in "${bg_models[@]}"; do
    local log_path="$warm_log_dir/ollama_warm_${m//[:]/_}.log"
    echo "[$(date)] pull+warm $m (keepalive=$keepalive)" > "$log_path"
    (
      OLLAMA_KEEP_ALIVE="$keepalive" ollama pull "$m" >> "$log_path" 2>&1 &&
      printf 'hi\n' | OLLAMA_KEEP_ALIVE="$keepalive" ollama run "$m" >> "$log_path" 2>&1
    ) &
  done

  # Block on the 70B warm so we know it actually loads
  local big_model="llama3.3:70b"
  local big_log="$warm_log_dir/ollama_warm_${big_model//[:]/_}.log"
  echo "[$(date)] pull+warm $big_model (blocking, keepalive=$keepalive)" > "$big_log"
  OLLAMA_KEEP_ALIVE="$keepalive" ollama pull "$big_model" >> "$big_log" 2>&1
  # Use stdin pipe to avoid TTY spinner quirks
  printf 'hi\n' | OLLAMA_KEEP_ALIVE="$keepalive" ollama run "$big_model" >> "$big_log" 2>&1
  echo "[$(date)] completed warm for $big_model" >> "$big_log"
  echo "[$(date)] ollama ps after warm:" >> "$big_log"
  OLLAMA_KEEP_ALIVE="$keepalive" ollama ps >> "$big_log" 2>&1
}

# Start all services
start_all() {
  echo -e "${BLUE}Starting AI Orchestrator services...${NC}\n"

  # CONFIG VALIDATION: Check critical configuration (non-blocking for development)
  echo -e "${CYAN}🔍 Validating configuration...${NC}"
  if [ -f "scripts/validate_config.py" ]; then
    if python3 scripts/validate_config.py; then
      echo -e "${GREEN}✅ Configuration validation passed${NC}"
    else
      if [ "$IN_SANDBOX" = "true" ]; then
        echo -e "${YELLOW}⚠️  Configuration issues detected but continuing in sandbox mode${NC}"
        echo -e "${YELLOW}    (Some optional services may not be available)${NC}"
      else
        echo -e "${RED}❌ Configuration validation failed. Please fix critical issues before starting services.${NC}"
        return 1
      fi
    fi
  else
    echo -e "${YELLOW}⚠️  Configuration validator not found. Skipping validation.${NC}"
  fi

  # OPTIMIZATION: Only clear cache on dev-start, not normal start
  # Cache clearing is expensive and should only be done when explicitly requested
  if [[ "${1:-}" == "dev" ]]; then
    echo -e "${CYAN}🧹 Clearing Python bytecode cache for development...${NC}"
    if [ -f "scripts/clear_cache.py" ]; then
      python3 scripts/clear_cache.py > /dev/null 2>&1
    fi
  fi

  # Development workflow aliases
  echo -e "${CYAN}💡 Development aliases available:${NC}"
  echo -e "  ${GREEN}./manage.sh dev-start${NC}    - Start all services with fresh cache"
  echo -e "  ${GREEN}./manage.sh dev-debug${NC}   - Start router + agent-runner for debugging"
  echo -e "  ${GREEN}./manage.sh clear-cache${NC} - Clear cache manually"

  local router_status=$(check_router)
  IFS='|' read -r router_port router_http router_launchd router_pid <<< "$router_status"
  
  local agent_status=$(check_agent)
  IFS='|' read -r agent_port agent_http agent_launchd agent_pid <<< "$agent_status"

  local surreal_status=$(check_surreal)
  IFS='|' read -r surreal_port surreal_http surreal_launchd surreal_pid <<< "$surreal_status"
  
  if [ "$surreal_http" = "true" ]; then
    echo -e "${GREEN}SurrealDB already running${NC}"
  else
    start_surreal
  fi

  # Check Ollama status
  local ollama_status=$(check_ollama)
  IFS='|' read -r ollama_port ollama_http ollama_launchd ollama_pid <<< "$ollama_status"

  if [ "$ollama_http" = "true" ]; then
    echo -e "${GREEN}Ollama already running${NC}"
  else
    start_ollama
  fi

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

  warm_models

  # [UNIFIED LIFECYCLE] RAG Server is now spawned by Agent Runner
  # local rag_status=$(check_rag)
  # IFS='|' read -r rag_port rag_http rag_launchd rag_pid <<< "$rag_status"
  # if [ "$rag_http" = "true" ]; then
  #   echo -e "${GREEN}RAG Server already running${NC}"
  # else
  #   start_rag
  # fi
  
  echo ""
  sleep 2
  show_status
}

# Stop all services
stop_all() {
  echo -e "${BLUE}Stopping AI Orchestrator services...${NC}\n"
  stop_router
  stop_agent
  stop_rag
  stop_surreal
  echo ""
  sleep 1
  show_status
}

# Restart all services
restart_all() {
# Pre-load all models at startup
./scripts/preload_models.sh

  echo -e "${BLUE}Restarting AI Orchestrator services...${NC}\n"

  # Create temporary plist files without KeepAlive
  create_temp_plists

  # Stop all services
  stop_all
  sleep 2

  # Kill any remaining processes
  ./bin/kill_zombies.sh

  # Start with temp plists (no KeepAlive)
  start_with_temp_plists

  # Restore original plists with KeepAlive
  restore_original_plists

  echo ""
  
  # Wait for services to actually come up (prevent false negatives in status)
  wait_for_health "http://127.0.0.1:$ROUTER_PORT/health" "Router" 10 || true
  wait_for_health "http://127.0.0.1:$AGENT_PORT/health" "Agent Runner" 30 || true  # Agent takes longer (~13s) due to imports
  
  sleep 2
  show_status
}

# Create temporary plist files without KeepAlive
create_temp_plists() {
  echo "Creating temporary plist files without KeepAlive..."

  # Router
  cp "$ROUTER_PLIST" "${ROUTER_PLIST}.temp"
  plutil -remove KeepAlive "${ROUTER_PLIST}.temp" 2>/dev/null || true

  # Agent
  cp "$AGENT_PLIST" "${AGENT_PLIST}.temp"
  plutil -remove KeepAlive "${AGENT_PLIST}.temp" 2>/dev/null || true

  # SurrealDB
  cp "$SURREAL_PLIST" "${SURREAL_PLIST}.temp"
  plutil -remove KeepAlive "${SURREAL_PLIST}.temp" 2>/dev/null || true
}

# Start services with temporary plists
start_with_temp_plists() {
  echo "Starting services with temporary plists (no KeepAlive)..."

  # Load temp plists
  launchctl load "${ROUTER_PLIST}.temp" 2>/dev/null || true
  launchctl load "${AGENT_PLIST}.temp" 2>/dev/null || true
  launchctl load "${SURREAL_PLIST}.temp" 2>/dev/null || true

  # Wait for startup
  sleep 5
}

# Restore original plists with KeepAlive
restore_original_plists() {
  echo "Restoring original plists with KeepAlive..."

  # Unload temp plists
  launchctl unload "${ROUTER_PLIST}.temp" 2>/dev/null || true
  launchctl unload "${AGENT_PLIST}.temp" 2>/dev/null || true
  launchctl unload "${SURREAL_PLIST}.temp" 2>/dev/null || true

  # Load original plists
  launchctl load "$ROUTER_PLIST" 2>/dev/null || true
  launchctl load "$AGENT_PLIST" 2>/dev/null || true
  launchctl load "$SURREAL_PLIST" 2>/dev/null || true

  # Clean up temp files
  rm -f "${ROUTER_PLIST}.temp" "${AGENT_PLIST}.temp" "${SURREAL_PLIST}.temp"
}

# Ensure all services are running (start what's missing)
ensure_running() {
  echo -e "${BLUE}Ensuring all services are running...${NC}\n"
  
  local router_status=$(check_router)
  IFS='|' read -r router_port router_http router_launchd router_pid <<< "$router_status"
  
  local agent_status=$(check_agent)
  IFS='|' read -r agent_port agent_http agent_launchd agent_pid <<< "$agent_status"

  local surreal_status=$(check_surreal)
  IFS='|' read -r surreal_port surreal_http surreal_launchd surreal_pid <<< "$surreal_status"

  local rag_status=$(check_rag)
  IFS='|' read -r rag_port rag_http rag_launchd rag_pid <<< "$rag_status"
  
  if [ "$surreal_http" != "true" ]; then
    echo "SurrealDB not running, starting..."
    start_surreal
  else
    echo -e "${GREEN}SurrealDB already running${NC}"
  fi

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

  if [ "$rag_http" != "true" ]; then
    echo "RAG-server not running, starting..."
    start_rag
  else
    echo -e "${GREEN}RAG-server already running${NC}"
  fi
  
  echo ""
  sleep 2
  show_status
}

# Sync project to Git
sync_git() {
  echo -e "${BLUE}Syncing project to Git...${NC}"
  git add .
  if git commit -m "Automated Sync: $(date)"; then
    echo "Changes committed."
  else
    echo "Nothing to commit (or commit failed)."
  fi
  
  if git push origin main; then
    echo -e "${GREEN}✓ Push successful${NC}"
  else
    echo -e "${RED}✗ Push failed (check internet/auth)${NC}"
  fi
}

# Run database backup
run_backup() {
  echo -e "${BLUE}Running memory database backup...${NC}"
  ./bin/backup_memory.sh
}

# Tail logs
logs() {
  local service=${1:-all}
  case "$service" in
    router) tail -f "$ROOT_DIR/logs/router.log" ;;
    agent) tail -f "$ROOT_DIR/logs/agent_runner.log" ;;
    rag) tail -f "$ROOT_DIR/logs/rag.log" ;;
    surreal) tail -f "$ROOT_DIR/logs/surreal.log" ;;
    all) tail -f "$ROOT_DIR/logs/"*.log ;;
    *) echo "Unknown log service: $service. Options: router, agent, rag, surreal, all" ;;
  esac
}

# Usage
usage() {
  cat <<EOF
Usage: $0 [command]
Commands:
  status        Show status of all services (default)
  start         Start all services
  stop          Stop all services
  restart       Restart all services
  ensure        Start any missing services (keeps running services running)
  logs [svc]    Tail logs for a service (router, agent, rag, surreal, all)
  start-router  Start only the router
  stop-router   Stop only the router
  restart-router Restart only the router
  start-agent   Start only the agent-runner
  stop-agent    Stop only the agent-runner
  restart-agent Restart only the agent-runner
  start-surreal Start only SurrealDB
  stop-surreal  Stop only SurrealDB
  start-rag     Start only RAG Server
  stop-rag      Stop only RAG Server
  restart-rag   Restart only RAG Server
  start-ollama  Start only Ollama
  stop-ollama   Stop only Ollama
  restart-ollama Restart only Ollama
  sync          Sync all code changes to Git
  backup        Trigger a manual memory backup
  dashboard     High-density system status overview
  pack          Full Brain Backup (DB + Files) to Sync Folder
  unpack        Full Brain Restore from Sync Folder
EOF
}

# Main
case "${1:-status}" in
  status) show_status ;;
  start) start_all ;;
  stop) stop_all ;;
  restart) restart_all ;;
  ensure) ensure_running ;;
  logs) logs "${2:-all}" ;;
  pack) ./bin/backup_brain.sh ;;
  unpack) ./bin/restore_brain.sh "${2:-}" ;;
  start-router) start_router; show_status ;;
  stop-router) stop_router; show_status ;;
  restart-router)
    echo "Restarting router manually..."
    stop_router
    sleep 2
    start_router
    show_status
    ;;
  dev-start) echo "Starting all services with fresh cache..."; start_all dev ;;
  dev-debug)
    echo "Starting router + agent-runner for debugging..."
    python3 scripts/clear_cache.py > /dev/null 2>&1
    start_surrealdb
    start_router
    start_agent
    show_status
    ;;
  clear-cache)
    echo "Clearing Python bytecode cache..."
    python3 scripts/clear_cache.py
    ;;
  start-agent) start_agent; show_status ;;
  stop-agent) stop_agent; show_status ;;
  restart-agent)
    if job_loaded "$AGENT_LABEL"; then
      echo "Restarting agent-runner via launchd..."
      launchctl kickstart -k "$DOMAIN/$AGENT_LABEL" 2>/dev/null || true
      sleep 2
    else
      echo "Agent-runner not loaded in launchd, starting..."
      start_agent
    fi
    warm_models
    show_status
    ;;
  start-surreal) start_surreal; show_status ;;
  stop-surreal) stop_surreal; show_status ;;
  start-rag) start_rag; show_status ;;
  stop-rag) stop_rag; show_status ;;
  restart-rag)
    if job_loaded "$RAG_LABEL"; then
      echo "Restarting RAG via launchd..."
      launchctl kickstart -k "$DOMAIN/$RAG_LABEL" 2>/dev/null || true
      sleep 2
    else
      echo "RAG not loaded in launchd, starting..."
      start_rag
    fi
    show_status
    ;;
  start-ollama) start_ollama; show_status ;;
  stop-ollama) stop_ollama; show_status ;;
  restart-ollama) stop_ollama; sleep 2; start_ollama; show_status ;;
  sync) sync_git ;;
  backup) run_backup ;;
  dashboard)
    echo -e "${BLUE}=== Antigravity Terminal Dashboard ===${NC}"
    echo -e "Time: $(date)"
    echo -e "--------------------------------------"
    
    # 1. Budget Stats
    if [ -f "$HOME/ai/budget.json" ]; then
        spend=$(cat "$HOME/ai/budget.json" | python3 -c "import sys, json; print(json.load(sys.stdin).get('current_spend', 0))")
        limit=$(cat "$HOME/ai/budget.json" | python3 -c "import sys, json; print(json.load(sys.stdin).get('daily_limit_usd', 0))")
        perc=$(python3 -c "print(f'{$spend/$limit*100:.1f}%') if $limit > 0 else print('0%')")
        echo -e "Budget: ${YELLOW}\$${spend} / \$${limit}${NC} (${perc})"
    fi
    
    # 2. Service Health (Concise)
    router_http=$(service_responding "http://127.0.0.1:$ROUTER_PORT/" && echo "true" || echo "false")
    agent_http=$(service_responding "http://127.0.0.1:$AGENT_PORT/" && echo "true" || echo "false")
    surreal_http=$(service_responding "http://127.0.0.1:$SURREAL_PORT/health" && echo "true" || echo "false")
    rag_http=$(service_responding "http://127.0.0.1:$RAG_PORT/health" && echo "true" || echo "false")
    
    echo -n "Services: "
    [ "$router_http" = "true" ] && echo -ne "${GREEN}Router ${NC}" || echo -ne "${RED}Router ${NC}"
    [ "$agent_http" = "true" ] && echo -ne "${GREEN}Agent ${NC}" || echo -ne "${RED}Agent ${NC}"
    [ "$surreal_http" = "true" ] && echo -ne "${GREEN}Surreal ${NC}" || echo -ne "${RED}Surreal ${NC}"
    [ "$rag_http" = "true" ] && echo -ne "${GREEN}RAG ${NC}" || echo -ne "${RED}RAG ${NC}"
    echo ""
    
    # 3. Model Status (from Agent API)
    if [ "$agent_http" = "true" ]; then
        model=$(curl -s "http://127.0.0.1:$AGENT_PORT/" | python3 -c "import sys, json; print(json.load(sys.stdin).get('model', 'unknown'))")
        echo -e "Active Model: ${BLUE}${model}${NC}"
    fi
    
    # 4. RAG Stats
    if [ "$rag_http" = "true" ]; then
        rag_stats=$(curl -s "http://127.0.0.1:$RAG_PORT/stats")
        total_chunks=$(echo "$rag_stats" | python3 -c "import sys, json; print(json.load(sys.stdin).get('total_chunks', 0))")
        total_ents=$(echo "$rag_stats" | python3 -c "import sys, json; print(json.load(sys.stdin).get('total_entities', 0))")
        kb_count=$(echo "$rag_stats" | python3 -c "import sys, json; print(json.load(sys.stdin).get('knowledge_bases', {}).__len__())")
        echo -e "RAG Content: ${GREEN}${total_chunks} chunks${NC} across ${GREEN}${kb_count} KBs${NC} (${total_ents} entities)"
    fi
    
    echo -e "--------------------------------------"
    echo -e "${BLUE}Logs: tail -f logs/agent_runner.log${NC}"
    ;;
  -h|--help|help) usage ;;
  *) echo "Unknown command: $1"; usage; exit 2 ;;
esac







