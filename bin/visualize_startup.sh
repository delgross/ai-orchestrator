#!/bin/zsh

# System Startup Visualizer
# Monitors and displays the startup status of all AI Orchestrator services

set -uo pipefail
# Note: Removed -e flag to allow graceful error handling in check functions

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Service URLs
ROUTER_URL="http://localhost:5455"
AGENT_RUNNER_URL="http://localhost:5460"
DATABASE_URL="http://localhost:8000"
RAG_URL="http://localhost:5555"

# Status tracking (associative arrays - zsh supports these)
typeset -A STATUS

# Initialize status
STATUS[router]="⏳"
STATUS[agent_runner]="⏳"
STATUS[database]="⏳"
STATUS[rag]="⏳"

# Function to check service health
check_service() {
    local service=$1
    local url=$2
    local endpoint=${3:-"/health"}
    
    local full_url="${url}${endpoint}"
    local response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 "${full_url}" 2>/dev/null || echo "000")
    
    if [ "$response" = "200" ]; then
        STATUS[$service]="✅"
        return 0
    elif [ "$response" = "503" ]; then
        # 503 = service unavailable (starting up)
        STATUS[$service]="⏳"
        return 1
    else
        STATUS[$service]="❌"
        return 1
    fi
}

# Function to check database
check_database() {
    local response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 "${DATABASE_URL}/health" 2>/dev/null || echo "000")
    
    if [ "$response" = "200" ]; then
        STATUS[database]="✅"
        return 0
    elif [ "$response" = "503" ]; then
        STATUS[database]="⏳"
        return 1
    else
        STATUS[database]="❌"
        return 1
    fi
}

# Function to check RAG server
check_rag() {
    # RAG server might not have /health, try root or skip if unavailable
    local response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 "${RAG_URL}/" 2>/dev/null || echo "000")
    
    if [ "$response" = "200" ] || [ "$response" = "404" ]; then
        # 200 or 404 means server is responding
        STATUS[rag]="✅"
        return 0
    else
        STATUS[rag]="❌"
        return 1
    fi
}

# Function to get agent runner startup status
get_agent_status() {
    local response=$(curl -s --max-time 2 "${AGENT_RUNNER_URL}/api/admin/startup-status" 2>/dev/null || echo "")
    
    if [ -n "$response" ]; then
        local available=$(echo "$response" | grep -o '"available":[^,]*' | cut -d: -f2 | tr -d ' ')
        if [ "$available" = "true" ]; then
            echo "$response" | grep -o '"message":"[^"]*' | cut -d'"' -f4 | head -1
        fi
    fi
}

# Function to display status
display_status() {
    clear
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}  ${BLUE}AI Orchestrator - System Startup Monitor${NC}              ${CYAN}║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${YELLOW}Last Update: ${timestamp}${NC}"
    echo ""
    
    # Core Services
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}Core Services${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    echo -e "  ${STATUS[database]}  ${BLUE}SurrealDB${NC}          ${DATABASE_URL}"
    echo -e "  ${STATUS[router]}  ${BLUE}Router${NC}              ${ROUTER_URL}"
    echo -e "  ${STATUS[agent_runner]}  ${BLUE}Agent Runner${NC}        ${AGENT_RUNNER_URL}"
    echo -e "  ${STATUS[rag]}  ${BLUE}RAG Server${NC}          ${RAG_URL}"
    
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # Agent Runner Details
    if [ "${STATUS[agent_runner]}" = "✅" ]; then
        local agent_status=$(get_agent_status)
        if [ -n "$agent_status" ]; then
            echo ""
            echo -e "${GREEN}Agent Runner Status:${NC}"
            echo -e "  ${agent_status:0:70}"
        fi
    fi
    
    echo ""
    echo -e "${YELLOW}Press Ctrl+C to exit${NC}"
}

# Function to check all services
check_all() {
    # Use || true to prevent script from exiting on errors
    check_database || true
    check_service "router" "${ROUTER_URL}" "/health" || true
    check_rag || true
    
    # Check agent runner - try multiple endpoints
    local health_response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 "${AGENT_RUNNER_URL}/health" 2>/dev/null || echo "000")
    if [ "$health_response" = "200" ]; then
        STATUS[agent_runner]="✅"
    elif [ "$health_response" = "503" ]; then
        STATUS[agent_runner]="⏳"
    else
        # Try startup-status endpoint as fallback
        local startup_response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 "${AGENT_RUNNER_URL}/api/admin/startup-status" 2>/dev/null || echo "000")
        if [ "$startup_response" = "200" ] || [ "$startup_response" = "503" ]; then
            STATUS[agent_runner]="⏳"
        else
            STATUS[agent_runner]="❌"
        fi
    fi
}

# Main loop
main() {
    echo -e "${CYAN}Starting System Startup Monitor...${NC}"
    echo -e "${YELLOW}Checking services every 2 seconds...${NC}"
    echo ""
    sleep 2
    
    local iteration=0
    while true; do
        check_all
        display_status
        
        # Check if all services are up
        local all_up=true
        for service in router agent_runner database rag; do
            if [ "${STATUS[$service]}" != "✅" ]; then
                all_up=false
                break
            fi
        done
        
        if [ "$all_up" = true ]; then
            echo ""
            echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "${GREEN}🎉 All services are up and running!${NC}"
            echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo ""
            echo -e "${YELLOW}Monitor will continue running. Press Ctrl+C to exit.${NC}"
        fi
        
        sleep 2
        iteration=$((iteration + 1))
    done
}

# Handle Ctrl+C gracefully
trap 'echo -e "\n${YELLOW}Shutting down monitor...${NC}"; exit 0' INT

# Run main loop
main

