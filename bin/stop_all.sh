#!/bin/bash
# bin/stop_all.sh

# Function to gracefully stop a process by name or port
stop_service() {
    local name="$1"
    local pattern="$2"
    local port="$3"

    echo "🛑 Stopping $name..."
    
    # Find PIDs
    local pids=$(pgrep -f "$pattern")
    
    if [ -n "$pids" ]; then
        echo "   Found PIDs: $pids. Sending SIGTERM..."
        kill $pids 2>/dev/null
        
        # Wait up to 5 seconds for graceful shutdown
        for i in {1..5}; do
            if ! pgrep -f "$pattern" > /dev/null; then
                echo "   ✅ $name stopped gracefully."
                return
            fi
            sleep 1
        done
        
        # If still running, force kill
        echo "   ⚠️ $name refused to stop. Force killing (SIGKILL)..."
        pkill -9 -f "$pattern"
    else
        echo "   $name not running (process check)."
    fi

    # Final Port Sweep (Nuclear Backup)
    if [ -n "$port" ]; then
        local port_pid=$(lsof -ti:$port)
        if [ -n "$port_pid" ]; then
             echo "   Cleaning up port $port (PID $port_pid)..."
             kill -9 $port_pid 2>/dev/null
        fi
    fi
}

start_time=$(date +%s)

stop_service "Agent Runner" "python3 -m agent_runner.main" "5460"
# Also clean up the shell wrapper
pkill -f "run_agent_runner.sh"

stop_service "Router" "python3 -m router.main" "5455"
pkill -f "run_router.sh"

stop_service "RAG Server" "python3 rag_server.py" "5555"
pkill -f "run_rag_server.sh"

end_time=$(date +%s)
duration=$((end_time - start_time))

echo "✅ All services stopped in ${duration}s."
