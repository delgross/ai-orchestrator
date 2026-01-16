#!/bin/bash
# bin/kill_zombies.sh
# Aggressively clean up processes holding critical system ports.
# This runs BEFORE startup to ensure a clean slate.

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[ZOMBIE]${NC} $1"
}

warn() {
    echo -e "${RED}[ZOMBIE]${NC} $1"
}

# Default to Agent Runner ports if no arg
SERVICE="${1:-agent}"

log "Cleaning zombies for service: $SERVICE"

declare -a PORTS
declare -a NAMES

case "$SERVICE" in
  agent)
    PORTS=(5460 5555 8000) # Agent, RAG, SurrealDB
    NAMES=("python3 -m agent_runner.main" "uvicorn agent_runner.main" "python3 rag_server.py")
    ;;
  router)
    PORTS=(5455) # Router
    NAMES=("python3 -m router.main" "uvicorn router.main")
    ;;
  all)
    PORTS=(5455 5460 5555 8000)
    NAMES=("python3 -m agent_runner.main" "python3 -m router.main" "python3 rag_server.py" "uvicorn")
    ;;
  *)
    warn "Unknown service: $SERVICE"
    exit 1
    ;;
esac

killed_count=0

for port in "${PORTS[@]}"; do
    # Find PIDs using lsof (restrict to LISTEN to avoid killing clients like Router)
    pids=$(lsof -t -i :$port -sTCP:LISTEN 2>/dev/null)
    
    if [ -n "$pids" ]; then
        for pid in $pids; do
            pname=$(ps -p $pid -o comm= 2>/dev/null)
            warn "Killing zombie on port $port (PID $pid): $pname"
            kill -9 $pid 2>/dev/null
            ((killed_count++))
        done
    fi
done

# Cleanup by name
for name in "${NAMES[@]}"; do
    if pkill -0 -f "$name" >/dev/null 2>&1; then
        warn "Killing zombie by name: $name"
        pkill -9 -f "$name" 2>/dev/null || true
        ((killed_count++))
    fi
done

# Special handling for SurrealDB (only if cleaning agent/all)
if [[ "$SERVICE" == "agent" || "$SERVICE" == "all" ]]; then
     pkill -9 -x "surreal" 2>/dev/null || true
fi

if [ $killed_count -gt 0 ]; then
    log "Cleaned up $killed_count zombie processes."
    sleep 1 # Allow OS to reclaim resources
else
    log "System clean. No zombies found."
fi
