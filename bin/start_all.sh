#!/bin/bash
# bin/start_all.sh

# 1. Kill existing
pkill -f "python3 -m router.main"
pkill -f "python3 -m agent_runner.main"
pkill -f "python3 rag_server.py"

echo "🛑 Stopped existing services."
sleep 1

# 2. Start RAG (Dependency for others)
nohup ./bin/run_rag_server.sh > logs/rag_server.log 2>&1 &
echo "✅ RAG Server started."
sleep 2

# 3. Start Router
nohup ./bin/run_router.sh > logs/router.log 2>&1 &
echo "✅ Router started."
sleep 2

# 4. Start Agent Runner
nohup ./bin/run_agent_runner.sh > logs/agent_runner.log 2>&1 &
echo "✅ Agent Runner started."

echo "🚀 System is warming up..."
