#!/bin/bash
# Quick test of model pre-loading

echo "🧪 Testing model pre-loading with 2 models..."

# Test loading just 2 models quickly
TEST_MODELS=("qwen2.5:7b-instruct" "llama3:8b")

for model in "${TEST_MODELS[@]}"; do
    echo "🔄 Testing $model..."
    if curl -s -X POST "http://127.0.0.1:11434/api/generate" \
        -H "Content-Type: application/json" \
        -d "{\"model\": \"$model\", \"prompt\": \"Test load.\", \"stream\": false}" > /dev/null 2>&1; then
        echo "✅ $model loaded successfully"
    else
        echo "❌ Failed to load $model"
    fi
done

echo "📊 Final loaded count:"
curl -s "http://127.0.0.1:11434/api/ps" | jq '.models | length'
EOF && chmod +x scripts/test_preload.sh && ./scripts/test_preload.sh