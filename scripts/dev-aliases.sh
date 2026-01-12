#!/bin/bash
# Development workflow aliases for AI Orchestrator
# Source this file in your shell: source scripts/dev-aliases.sh

# Quick start with fresh cache
alias ai-start='./manage.sh dev-start'
alias ai-debug='./manage.sh dev-debug'
alias ai-stop='./manage.sh stop all'
alias ai-status='./manage.sh status'
alias ai-restart='./manage.sh restart all'

# Cache management
alias ai-clear-cache='./manage.sh clear-cache'
alias ai-health='curl -s http://127.0.0.1:5455/health | jq'

# Development testing
alias ai-test-router='curl -s -X POST http://127.0.0.1:5455/v1/chat/completions -H "Authorization: Bearer 9sYBjBLjAHKG8g8ZzzsUeBOvtzgQFHmX7oIeygdpzic" -d "{\"model\": \"agent:mcp\", \"messages\": [{\"role\": \"user\", \"content\": \"hello\"}]} " | jq -r ".choices[0].message.content"'
alias ai-logs-router='tail -f logs/router.log'
alias ai-logs-agent='tail -f logs/agent_runner.log'

echo "🤖 AI Orchestrator development aliases loaded!"
echo "Available commands:"
echo "  ai-start      - Start all services with fresh cache"
echo "  ai-debug      - Start router + agent for debugging"
echo "  ai-stop       - Stop all services"
echo "  ai-status     - Show service status"
echo "  ai-clear-cache - Clear Python bytecode cache"
echo "  ai-health     - Check router health"
echo "  ai-test-router - Test router with chat request"
echo "  ai-logs-router - Tail router logs"
echo "  ai-logs-agent  - Tail agent logs"