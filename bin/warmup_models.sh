#!/bin/bash
# Warmup script to pin critical models to VRAM forever.

MODEL="ollama:qwen2.5:7b-instruct"

# Strip "ollama:" prefix for API call if needed, but usually works with full name if mapped.
# Ollama API expects just the model name "qwen2.5:7b-instruct" usually.
API_MODEL="qwen2.5:7b-instruct"

echo "🔥 Warming up $API_MODEL (keep_alive: -1)..."
curl -s -X POST http://localhost:11434/api/generate -d "{
  \"model\": \"$API_MODEL\",
  \"keep_alive\": -1,
  \"options\": {
    \"num_ctx\": 32768
  }
}" > /dev/null &

echo "✅ $API_MODEL pinned to VRAM."

# --- Maître d' (70B) ---
HEAD_MODEL="llama3.3:70b"
echo "🔥 Warming up $HEAD_MODEL (keep_alive: -1)..."
curl -s -X POST http://localhost:11434/api/generate -d "{
  \"model\": \"$HEAD_MODEL\",
  \"keep_alive\": -1,
  \"options\": {
    \"num_ctx\": 32768
  }
}" > /dev/null &

echo "✅ $HEAD_MODEL pinned to VRAM."
