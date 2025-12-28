#!/bin/zsh
# Antigravity AI Orchestrator - Interactive Control Menu

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Get directory of this script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

show_menu() {
    clear
    echo -e "${BLUE}${BOLD}==========================================${NC}"
    echo -e "${CYAN}${BOLD}   ANTIGRAVITY AI ORCHESTRATOR MENU   ${NC}"
    echo -e "${BLUE}${BOLD}==========================================${NC}"
    echo -e "1) ${GREEN}Status${NC}      - Check health of all services"
    echo -e "2) ${GREEN}Start${NC}       - Boot up the full orchestrator"
    echo -e "3) ${YELLOW}Restart${NC}     - Quick cycle for code changes"
    echo -e "4) ${RED}Stop${NC}        - Shut down all components"
    echo -e "5) ${CYAN}Run Tests${NC}   - Execute automated test suite"
    echo -e "6) ${CYAN}View Logs${NC}   - Tail agent-runner error logs"
    echo -e "7) ${CYAN}Dashboard${NC}   - Open web UI in browser"
    echo -e "q) ${BOLD}Exit${NC}"
    echo -e "${BLUE}------------------------------------------${NC}"
    echo -n "Select an option: "
}

while true; do
    show_menu
    read -r opt
    case $opt in
        1)
            echo -e "\n${BLUE}Checking service status...${NC}"
            ./manage.sh status
            echo -e "\n${BOLD}Press any key to return to menu...${NC}"
            read -k1 -s
            ;;
        2)
            echo -e "\n${GREEN}Starting Antigravity...${NC}"
            ./manage.sh start
            echo -e "\n${BOLD}Press any key to return to menu...${NC}"
            read -k1 -s
            ;;
        3)
            echo -e "\n${YELLOW}Restarting all services...${NC}"
            ./manage.sh restart
            echo -e "\n${BOLD}Press any key to return to menu...${NC}"
            read -k1 -s
            ;;
        4)
            echo -e "\n${RED}Stopping all services...${NC}"
            ./manage.sh stop
            echo -e "\n${BOLD}Press any key to return to menu...${NC}"
            read -k1 -s
            ;;
        5)
            echo -e "\n${CYAN}Running automated tests...${NC}"
            ./test.sh
            echo -e "\n${BOLD}Press any key to return to menu...${NC}"
            read -k1 -s
            ;;
        6)
            echo -e "\n${CYAN}Tailing Agent-Runner logs (Ctrl+C to stop)...${NC}"
            tail -f ~/Library/Logs/ai/agent_runner.err.log
            ;;
        7)
            echo -e "\n${CYAN}Opening Dashboard...${NC}"
            open http://127.0.0.1:5455/dashboard
            sleep 1
            ;;
        q|Q)
            echo -e "\n${BLUE}Goodbye!${NC}"
            exit 0
            ;;
        *)
            echo -e "\n${RED}Invalid option: $opt${NC}"
            sleep 1
            ;;
    esac
done
