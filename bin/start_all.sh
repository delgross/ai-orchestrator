#!/bin/bash
# bin/start_all.sh - Orchestrated system startup with health checks

set -euo pipefail

# Load shared startup library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/startup_lib.sh"

PROJECT_ROOT="$(get_project_root)"
LOG_DIR="$PROJECT_ROOT/logs"
START_TIME=$(date +%s)

# Trap for cleanup on failure
cleanup_on_failure() {
    local exit_code=$?
    error "Startup failed with exit code $exit_code"
    error "Check logs in $LOG_DIR for details"

    # Kill any processes we started
    ./bin/kill_zombies.sh all 2>/dev/null || true

    exit $exit_code
}
trap cleanup_on_failure ERR

main() {
    log "🚀 Starting Antigravity AI System..."
    log "Project root: $PROJECT_ROOT"
    log "Log directory: $LOG_DIR"

    # Create log directory
    mkdir -p "$LOG_DIR"

    # Validate system requirements
    validate_system || exit 1

    # 1. Clean Slate (Zombie Protocol)
    log "🧹 Cleaning previous session..."
    cleanup_service "all"

    # 2. Start Infrastructure (Database) - Critical dependency
    log "🏗️ Starting infrastructure services..."

    if ! ./bin/start_surreal.sh; then
        error "Failed to start SurrealDB"
        exit 1
    fi

    if ! wait_for_service 8000 "Database" 30 2; then
        error "Database failed health check"
        exit 1
    fi

    # 3. Start RAG Server (depends on database)
    log "🔍 Starting RAG Server..."
    local rag_command="./bin/run_rag_server.sh start > \"$LOG_DIR/rag_server.log\" 2>&1"
    if ! start_service_with_retry "RAG Server" "$rag_command" 5555 2 3; then
        warn "RAG Server failed, continuing without it (degraded mode)"
    fi

    # 4. Start Router (depends on database)
    log "🚪 Starting Router..."
    local router_command="./bin/run_router.sh start > \"$LOG_DIR/router.log\" 2>&1"
    if ! start_service_with_retry "Router" "$router_command" 5455 3 8; then
        error "Router failed to start - aborting startup"
        exit 1
    fi

    # 5. Start Agent Runner (depends on router and database)
    log "🤖 Starting Agent Runner..."
    local agent_command="./bin/run_agent_runner.sh start > \"$LOG_DIR/agent_runner.log\" 2>&1"
    if ! start_service_with_retry "Agent Runner" "$agent_command" 5460 3 10; then
        error "Agent Runner failed to start - aborting startup"
        exit 1
    fi

    # 6. Service Discovery and Final Health Check
    log "🔍 Performing service discovery and final health check..."

    # Run service discovery to export environment variables
    if "$SCRIPT_DIR/service_discovery.sh" discover; then
        log "✅ Service discovery successful"
    else
        warn "⚠️ Service discovery had issues - system may run in degraded mode"
    fi

    # Final comprehensive health check
    local critical_healthy=true
    local optional_healthy=true

    # Check critical services with longer timeouts
    if ! check_port_health 5455 "Router" 10; then critical_healthy=false; fi
    if ! check_port_health 5460 "Agent Runner" 10; then critical_healthy=false; fi
    if ! check_database_health 8000 10; then critical_healthy=false; fi

    # Check optional services
    if ! check_port_health 5555 "RAG Server" 10; then
        warn "RAG Server not available - running in degraded mode"
        optional_healthy=false
    fi

    # Report results
    local duration=$(( $(date +%s) - START_TIME ))

    if $critical_healthy; then
        log "✅ System startup completed successfully in ${duration}s!"
        log "🌐 Critical services available:"
        log "   📊 Router:        $(./bin/service_discovery.sh endpoint router)"
        log "   🤖 Agent Runner:  $(./bin/service_discovery.sh endpoint agent_runner)"
        log "   🗄️  Database:      $(./bin/service_discovery.sh endpoint database)"

        if $optional_healthy; then
            log "   🔍 RAG Server:    $(./bin/service_discovery.sh endpoint rag)"
        else
            warn "   🔍 RAG Server:    Degraded (not available)"
        fi
    else
        error "❌ Critical services failed to start properly"
        exit 1
    fi

    # Optional: Start model preloader in background
    if [ -f "$PROJECT_ROOT/scripts/preload_models.sh" ]; then
        log "🚀 Starting model preloader in background..."
        nohup "$PROJECT_ROOT/scripts/preload_models.sh" > "$LOG_DIR/model_preloader.log" 2>&1 &
        log "✅ Model preloader started"
    fi

    log "🎉 Startup complete! System is ready."
}

# Run main function
main "$@"
