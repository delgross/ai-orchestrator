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

# Ports to clean
# 5455: Router
# 5460: Agent Runner
# 5555: RAG Server
# 8000: SurrealDB
PORTS=(5455 5460 5555 8000)

log "Scanning for zombie processes..."

killed_count=0

for port in "${PORTS[@]}"; do
    # Find PIDs using lsof
    # -t: terse (pid only)
    # -i: internet files
    pids=$(lsof -t -i :$port 2>/dev/null)
    
    if [ -n "$pids" ]; then
        for pid in $pids; do
            # Get process name for logging
            pname=$(ps -p $pid -o comm= 2>/dev/null)
            warn "Killing zombie on port $port (PID $pid): $pname"
            kill -9 $pid 2>/dev/null
            ((killed_count++))
        done
    fi
done

# Also cleanup by name just in case ports are weird
# This catches things that might be stuck looping but lost their port
pkill -9 -f "python3 -m router.main" 2>/dev/null || true
pkill -9 -f "python3 -m agent_runner.main" 2>/dev/null || true
pkill -9 -f "python3 rag_server.py" 2>/dev/null || true
# Do NOT pkill surreal by name here if we rely on port 8000. 
# But since we manage it now, we SHOULD kill it to force fresh restart.
pkill -9 -x "surreal" 2>/dev/null || true

if [ $killed_count -gt 0 ]; then
    log "Cleaned up $killed_count zombie processes."
    sleep 1 # Allow OS to reclaim resources
else
    log "System clean. No zombies found."
fi
