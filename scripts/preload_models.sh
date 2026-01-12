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

# Define models to preload (including upgrades)
MODELS_TO_LOAD=(
    "llama3.3:70b-instruct-q8_0"    # AGENT_MODEL, TASK_MODEL (84GB)
    "qwq:latest"                     # HEALER_MODEL (20GB)
    "qwen3:30b"                      # AUDITOR_MODEL, CRITIC_MODEL, MCP_MODEL (19GB)
    "llama3:8b"                      # UPGRADED: FALLBACK_MODEL, FINALIZER_MODEL, INTENT_MODEL, PRUNER_MODEL (5GB)
    "llama3.2-vision:latest"         # VISION_MODEL (8GB)
    "llama3.1:latest"                # SUMMARIZATION_MODEL (5GB)
    "qwen2.5:7b-instruct"            # UPGRADED: ROUTER_MODEL (5GB)
    "mxbai-embed-large:latest"       # EMBEDDING_MODEL (1GB)
)

echo "📦 Pre-loading ${#MODELS_TO_LOAD[@]} upgraded models..."
echo "This may take several minutes..."

# Load models in parallel (limit to 3 concurrent to avoid overwhelming)
# Load models in parallel (limit to 6 concurrent to avoid overwhelming)
load_model() {
    local model=$1
    local ctx_size=${2:-4096} # Default to 4k for support models if not specified
    
    echo "🔄 Loading $model (Context: $ctx_size)..."
    
    # Use a simple prompt to trigger loading with infinite keep-alive and specific context
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
    "qwen2.5-coder:32b|8192"              # INTENT, TASK, MCP, CRITIC (Strong Coding & Logic)
    "llama3.1:latest|8192"                # UNIFIED SUPPORT (Fallback, Summarizer) - 8k
    "llama3.2-vision:latest|8192"         # VISION (8k for image handling)
    "mxbai-embed-large:latest|2048"       # EMBEDDING (Fixed 512/2k limit usually)
    "llama3.2:latest|2048"                # REFINER (3B model, robust rewriting)
)

# Parallel execution with args parsing
printf '%s\n' "${MODELS_WITH_CTX[@]}" | xargs -n 1 -P 6 -I {} bash -c 'IFS="|" read -r m c <<< "{}"; load_model "$m" "$c"'

echo ""
echo "📊 MODEL LOADING COMPLETE"
echo "========================"

# Verify all models are loaded
echo "🔍 Verifying loaded models:"
LOADED_COUNT=$(curl -s "http://127.0.0.1:11434/api/ps" | jq '.models | length')
TOTAL_VRAM=$(curl -s "http://127.0.0.1:11434/api/ps" | jq '[.models[].size_vram] | add / 1000000000 | round')

echo "• Models loaded: $LOADED_COUNT"
echo "• Total VRAM: ${TOTAL_VRAM}GB"
echo "• Expected: ${#MODELS_TO_LOAD[@]} models"

if [ "$LOADED_COUNT" -eq "${#MODELS_TO_LOAD[@]}" ]; then
    echo "✅ All models pre-loaded successfully!"
    echo "🎉 System ready with zero loading delays"
else
    echo "⚠️ Some models may not have loaded properly"
fi

echo ""
echo "🚀 Starting AI Orchestrator services..."
