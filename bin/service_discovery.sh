#!/bin/bash
# bin/service_discovery.sh
# Service discovery utilities for startup scripts

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/startup_lib.sh"

# Service discovery functions
get_service_port() {
    local service_name="$1"
    case "$service_name" in
        database) echo "8000" ;;
        rag) echo "5555" ;;
        router) echo "5455" ;;
        agent_runner) echo "5460" ;;
        *) error "Unknown service: $service_name"; return 1 ;;
    esac
}

get_service_health_path() {
    local service_name="$1"
    case "$service_name" in
        database) echo "/health" ;;
        rag) echo "/health" ;;
        router) echo "/admin/system-status" ;;
        agent_runner) echo "/health" ;;
        *) error "Unknown service: $service_name"; return 1 ;;
    esac
}

# Check if a service is discoverable
service_discoverable() {
    local service_name="$1"
    local port
    local health_path

    port=$(get_service_port "$service_name") || return 1
    health_path=$(get_service_health_path "$service_name") || return 1

    if curl -s --max-time 3 "http://127.0.0.1:$port$health_path" > /dev/null 2>&1; then
        log "Service $service_name discovered at http://127.0.0.1:$port"
        return 0
    else
        warn "Service $service_name not available at http://127.0.0.1:$port"
        return 1
    fi
}

# Wait for service discovery with timeout
wait_for_service_discovery() {
    local service_name="$1"
    local timeout="${2:-30}"

    log "Waiting for $service_name to become discoverable..."

    local start_time=$(date +%s)
    while (( $(date +%s) - start_time < timeout )); do
        if service_discoverable "$service_name"; then
            log "$service_name is now discoverable"
            return 0
        fi
        sleep 2
    done

    error "$service_name discovery timed out after ${timeout}s"
    return 1
}

# Get service endpoint
get_service_endpoint() {
    local service_name="$1"
    local path="${2:-}"
    local port

    port=$(get_service_port "$service_name") || return 1
    echo "http://127.0.0.1:$port$path"
}

# Export service environment variables
export_service_env() {
    local service_name="$1"
    local port

    port=$(get_service_port "$service_name") || return 1

    # Export common environment variables
    case "$service_name" in
        database)
            export SURREALDB_URL="http://127.0.0.1:$port"
            export DATABASE_URL="http://127.0.0.1:$port"
            ;;
        rag)
            export RAG_URL="http://127.0.0.1:$port"
            ;;
        router)
            export ROUTER_URL="http://127.0.0.1:$port"
            ;;
        agent_runner)
            export AGENT_RUNNER_URL="http://127.0.0.1:$port"
            ;;
    esac

    log "Exported environment for $service_name"
}

# Check all critical services
check_critical_services() {
    local critical_services=("database" "router" "agent_runner")
    local all_healthy=true

    log "Checking critical services..."

    for service in "${critical_services[@]}"; do
        if ! service_discoverable "$service"; then
            error "Critical service $service is not available"
            all_healthy=false
        fi
    done

    if $all_healthy; then
        log "All critical services are healthy"
        return 0
    else
        error "Some critical services are unhealthy"
        return 1
    fi
}

# Graceful degradation - try to start system even if some services fail
check_optional_services() {
    local optional_services=("rag")
    local available_services=()

    log "Checking optional services..."

    for service in "${optional_services[@]}"; do
        if service_discoverable "$service"; then
            available_services+=("$service")
        else
            warn "Optional service $service not available - system will run in degraded mode"
        fi
    done

    # Export available services info
    export AVAILABLE_SERVICES="${available_services[*]}"

    log "Optional services available: ${available_services[*]:-none}"
}

# Main discovery function
discover_services() {
    log "🔍 Starting service discovery..."

    # First check critical services
    if ! check_critical_services; then
        error "Critical service discovery failed"
        return 1
    fi

    # Then check optional services
    check_optional_services

    # Export service environment variables for all known services
    for service in database rag router agent_runner; do
        if service_discoverable "$service"; then
            export_service_env "$service"
        fi
    done

    log "✅ Service discovery complete"
    return 0
}

# Test function for development
test_discovery() {
    echo "Testing service discovery..."

    for service in database rag router agent_runner; do
        echo -n "Testing $service: "
        if service_discoverable "$service"; then
            endpoint=$(get_service_endpoint "$service")
            echo "✅ $endpoint"
        else
            echo "❌ Not available"
        fi
    done
}

# Command line interface
case "${1:-}" in
    discover)
        discover_services
        ;;
    test)
        test_discovery
        ;;
    endpoint)
        shift
        get_service_endpoint "$@"
        ;;
    wait)
        shift
        wait_for_service_discovery "$@"
        ;;
    *)
        cat <<EOF
Usage: $0 <command> [args...]

Commands:
  discover              Discover all services and export environment
  test                  Test service availability
  endpoint <service>    Get service endpoint URL
  wait <service> [timeout]  Wait for service to become available

Services: ${!SERVICES[*]}
EOF
        exit 1
        ;;
esac