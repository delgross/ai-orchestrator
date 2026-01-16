#!/bin/bash
# Model Pre-loading Script for AI Orchestrator
# Loads all required models at startup to eliminate first-request delays

set -e

echo "🚀 Starting AI Orchestrator Model Pre-loading..."
echo "==============================================="

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama service..."
until curl -s http://127.0.0.1:11434/api/tags > /dev/null 2>&1; do
    sleep 2
done
echo "✅ Ollama service ready"

# --- ZOMBIE KILLER PROTOCOL ---
# Explicitly unload models that might be hogging VRAM
ZOMBIES=("llama3.2:latest" "llama3.1:latest" "qwen3:30b" "qwq:latest")
echo "🧹 Cleaning Zombies..."
for zombie in "${ZOMBIES[@]}"; do
    curl -s -X POST "http://127.0.0.1:11434/api/generate" \
        -d "{\"model\": \"$zombie\", \"keep_alive\": 0}" > /dev/null 2>&1
done

# Define models to preload
# NOTE: qwen2.5:7b-instruct is the BODY (Router/Task/etc)
MODELS_TO_LOAD=(
    "llama3.3:70b-instruct-q8_0"
    "qwen2.5:7b-instruct"
    "llama3.2-vision:latest"
    "mxbai-embed-large:latest"
)

echo "📦 Pre-loading ${#MODELS_TO_LOAD[@]} models..."

load_model() {
    local model=$1
    local ctx_size=${2:-4096}
    
    echo "🔄 Loading $model (Context: $ctx_size)..."
    
    if curl -s -X POST "http://127.0.0.1:11434/api/generate" \
        -H "Content-Type: application/json" \
        -d "{\"model\": \"$model\", \"prompt\": \"Ready.\", \"keep_alive\": -1, \"stream\": false, \"options\": {\"num_ctx\": $ctx_size}}" > /dev/null 2>&1; then
        echo "✅ $model loaded successfully (Locked in VRAM, ${ctx_size} ctx)"
    else
        echo "❌ Failed to load $model"
    fi
}

export -f load_model

# Define models with their specific context requirements
# Format: "model_name|context_size"
MODELS_WITH_CTX=(
    "llama3.3:70b|32768"                  # AGENT (Needs Max Context)
    "qwen2.5:7b-instruct|16384"            # ROUTER / TASK / HEALER / MCP
    "llama3.2-vision:latest|8192"         # VISION
    "mxbai-embed-large:latest|2048"       # EMBEDDING
)

# Parallel execution with args parsing
printf '%s\n' "${MODELS_WITH_CTX[@]}" | xargs -n 1 -P 4 -I {} bash -c 'IFS="|" read -r m c <<< "{}"; load_model "$m" "$c"'

echo ""
echo "📊 MODEL LOADING COMPLETE"
echo "========================"

# Verify all models are loaded
echo "🔍 Verifying loaded models:"
LOADED_COUNT=$(curl -s "http://127.0.0.1:11434/api/ps" | jq '.models | length')
TOTAL_VRAM=$(curl -s "http://127.0.0.1:11434/api/ps" | jq '[.models[].size_vram] | add / 1000000000 | round')

echo "• Models loaded: $LOADED_COUNT"
echo "• Total VRAM: ${TOTAL_VRAM}GB"

if [ "$LOADED_COUNT" -eq "${#MODELS_TO_LOAD[@]}" ]; then
    echo "✅ All models pre-loaded successfully!"
    echo "🎉 System ready with zero loading delays"
else
    echo "⚠️ Some models may not have loaded properly"
fi

echo ""
echo "🚀 Starting AI Orchestrator services..."
