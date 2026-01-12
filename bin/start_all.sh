#!/bin/bash
# bin/start_all.sh

# 1. Clean Slate (Zombie Protocol)
echo "🧹 Cleaning previous session..."
./bin/kill_zombies.sh
sleep 1

# 2. Start Infrastructure (Database)
./bin/start_surreal.sh
echo "⏳ Waiting for Database..."
sleep 2

# 3. Start RAG (Dependency for others)
nohup ./bin/run_rag_server.sh > logs/rag_server.log 2>&1 &
echo "✅ RAG Server started."
sleep 2

# 4. Start Router
nohup ./bin/run_router.sh > logs/router.log 2>&1 &
echo "✅ Router started."
sleep 2

# 5. Start Agent Runner
nohup ./bin/run_agent_runner.sh > logs/agent_runner.log 2>&1 &
echo "✅ Agent Runner started."

echo "🚀 System is warming up..."
