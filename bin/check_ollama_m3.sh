#!/bin/bash

# Define colors for readability
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "--- Ollama M3 Ultra Performance Check ---"

# 1. Check System Memory Limit (wired_limit_mb)
echo -n "Checking GPU Memory Limit (wired_limit_mb): "
LIMIT=$(sysctl -n iogpu.wired_limit_mb 2>/dev/null)
if [ "$LIMIT" -ge 240000 ]; then
    echo -e "${GREEN}PASS ($LIMIT MB)${NC}"
else
    echo -e "${RED}FAIL ($LIMIT MB)${NC} - Should be ~245760"
fi

# 2. Check LaunchAgent persistence for environment variables
echo -n "Checking LaunchAgent Persistence: "
if [ -f "$HOME/Library/LaunchAgents/setenv.ollama.plist" ]; then
    echo -e "${GREEN}PASS (File exists)${NC}"
else
    echo -e "${RED}FAIL${NC} - Plist file missing."
fi

# 3. Check specific Ollama environment variables
echo "--- Environment Variables ---"
check_env() {
    VAL=$(launchctl getenv $1)
    if [ "$VAL" == "$2" ]; then
        echo -e "$1: ${GREEN}$VAL${NC}"
    else
        echo -e "$1: ${RED}$VAL${NC} (Expected $2)"
    fi
}

check_env "OLLAMA_KEEP_ALIVE" "-1"
check_env "OLLAMA_NUM_PARALLEL" "4"
check_env "OLLAMA_CONTEXT_LENGTH" "32768"
check_env "OLLAMA_KV_CACHE_TYPE" "q8_0"

# 4. Check active Ollama Server status
echo "--- Active Server Status ---"
if curl -s http://localhost:11434 > /dev/null; then
    echo -e "Ollama Server: ${GREEN}RUNNING${NC}"
    
    # Check if a model is loaded and on GPU
    RUNNING_MODELS=$(ollama ps | grep -v "NAME")
    if [ -z "$RUNNING_MODELS" ]; then
        echo "No models currently loaded. Run a model to see processor split."
    else
        echo "Current Load Split:"
        ollama ps
    fi
else
    echo -e "Ollama Server: ${RED}NOT RUNNING${NC}"
fi

echo "----------------------------------------"
