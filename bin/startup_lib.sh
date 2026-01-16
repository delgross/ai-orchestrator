#!/bin/bash
# bin/startup_lib.sh
# Shared library for startup scripts - provides common functionality

set -euo pipefail

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${GREEN}[STARTUP]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[STARTUP]${NC} $1"
}

error() {
    echo -e "${RED}[STARTUP]${NC} $1"
}

info() {
    echo -e "${BLUE}[STARTUP]${NC} $1"
}

# Get project root directory
get_project_root() {
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    echo "$(dirname "$script_dir")"
}

# Load environment files in priority order
load_environment() {
    local project_root="$1"
    local service_name="${2:-}"

    # 1. Load system-wide .env (lowest priority)
    if [ -f "$project_root/.env" ]; then
        set -a
        source "$project_root/.env"
        set +a
        log "Loaded system .env"
    fi

    # 2. Load providers.env (API keys)
    if [ -f "$project_root/providers.env" ]; then
        set -a
        source "$project_root/providers.env"
        set +a
        log "Loaded providers.env"
    fi

    # 3. Load service-specific env file (highest priority)
    if [ -n "$service_name" ]; then
        local service_env="$project_root/${service_name}.env"
        if [ -f "$service_env" ]; then
            set -a
            source "$service_env"
            set +a
            log "Loaded ${service_name}.env"
        fi

        # For agent_runner, also load agent_runner/agent_runner.env
        if [ "$service_name" = "agent_runner" ]; then
            local agent_env="$project_root/agent_runner/agent_runner.env"
            if [ -f "$agent_env" ]; then
                set -a
                source "$agent_env"
                set +a
                log "Loaded agent_runner/agent_runner.env"
            fi
        fi
    fi
}

# Ensure PATH includes common tool locations
ensure_path() {
    # Add Homebrew and system paths
    export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:${PATH:-}"

    # Add NVM paths if available
    if [ -d "$HOME/.nvm/versions/node" ]; then
        local nvm_bin
        nvm_bin="$(ls -1d "$HOME/.nvm/versions/node"/*/bin 2>/dev/null | sort -V | tail -n 1 || true)"
        if [ -n "$nvm_bin" ]; then
            export PATH="$nvm_bin:$PATH"
        fi
    fi

    # Add project-specific paths
    export PATH="$(get_project_root)/.venv/bin:$PATH"
}

# Health check functions
check_port_health() {
    local port="$1"
    local service_name="$2"
    local timeout="${3:-5}"

    if curl -s --max-time "$timeout" "http://127.0.0.1:$port/health" > /dev/null 2>&1; then
        log "$service_name is healthy on port $port"
        return 0
    else
        warn "$service_name not responding on port $port"
        return 1
    fi
}

check_database_health() {
    local port="${1:-8000}"
    local timeout="${2:-5}"

    if curl -s --max-time "$timeout" "http://127.0.0.1:$port/health" > /dev/null 2>&1; then
        log "Database is healthy on port $port"
        return 0
    else
        warn "Database not responding on port $port"
        return 1
    fi
}

wait_for_service() {
    local port="$1"
    local service_name="$2"
    local max_attempts="${3:-30}"
    local attempt_delay="${4:-1}"

    log "Waiting for $service_name on port $port..."

    for ((i=1; i<=max_attempts; i++)); do
        if check_port_health "$port" "$service_name" 2; then
            log "$service_name ready after ${i}s"
            return 0
        fi

        if [ $i -lt $max_attempts ]; then
            sleep "$attempt_delay"
        fi
    done

    error "$service_name failed to start after $((max_attempts * attempt_delay))s"
    return 1
}

# Process management
cleanup_service() {
    local service_name="$1"
    local script_dir="$(get_project_root)/bin"

    if [ -f "$script_dir/kill_zombies.sh" ]; then
        log "Cleaning up $service_name processes..."
        "$script_dir/kill_zombies.sh" "$service_name" || true
    else
        warn "kill_zombies.sh not found, skipping cleanup"
    fi
}

# Service startup with error handling
start_service_with_retry() {
    local service_name="$1"
    local start_command="$2"
    local health_check_port="$3"
    local max_retries="${4:-3}"
    local initial_wait="${5:-5}"

    for ((attempt=1; attempt<=max_retries; attempt++)); do
        log "Starting $service_name (attempt $attempt/$max_retries)..."

        # Clean up any existing processes on the port first
        if [ -n "$health_check_port" ]; then
            local existing_pid
            existing_pid=$(lsof -t -i :"$health_check_port" -sTCP:LISTEN 2>/dev/null || true)
            if [ -n "$existing_pid" ]; then
                warn "Killing existing process on port $health_check_port (PID $existing_pid)"
                kill -9 "$existing_pid" 2>/dev/null || true
                sleep 2
            fi
        fi

        # Start the service
        log "Executing: $start_command"
        eval "$start_command" &
        local script_pid=$!

        # Wait for initial startup
        log "Waiting ${initial_wait}s for $service_name to initialize..."
        sleep "$initial_wait"

        # For services that exec (like uvicorn), the script PID dies but service continues
        # So we only check if script failed immediately, then rely on health checks
        if kill -0 "$script_pid" 2>/dev/null; then
            # Script is still running (didn't exec), check if it's healthy
            if [ -n "$health_check_port" ] && wait_for_service "$health_check_port" "$service_name" 15 1; then
                log "$service_name started successfully"
                return 0
            else
                warn "$service_name health check failed, killing script process..."
                kill -9 "$script_pid" 2>/dev/null || true
                sleep 2
            fi
        else
            # Script exited (likely exec'd), check if service is actually running
            if [ -n "$health_check_port" ] && check_port_health "$health_check_port" "$service_name" 3; then
                log "$service_name started successfully (script exec'd)"
                return 0
            else
                warn "$service_name appears to have failed after exec"
            fi
        fi

        if [ $attempt -eq $max_retries ]; then
            error "$service_name failed to start after $max_retries attempts"
            return 1
        fi
    done
}

# Validate system requirements
validate_system() {
    local project_root
    project_root="$(get_project_root)"

    # Check Python version
    if ! command -v python3 >/dev/null 2>&1; then
        error "Python 3 not found in PATH"
        return 1
    fi

    # Check virtual environment
    if [ ! -f "$project_root/.venv/bin/python" ]; then
        error "Virtual environment not found at $project_root/.venv"
        return 1
    fi

    # Check required directories
    local required_dirs=("logs" "data")
    for dir in "${required_dirs[@]}"; do
        if [ ! -d "$project_root/$dir" ]; then
            warn "Creating missing directory: $dir"
            mkdir -p "$project_root/$dir"
        fi
    done

    log "System validation passed"
    return 0
}