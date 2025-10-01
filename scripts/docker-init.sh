#!/usr/bin/env bash
# This script initializes the Docker setup:
# 1. Waits for Ollama to be ready
# 2. Pulls the required model
# 3. Runs ingestion to build the vector index

set -e

OLLAMA_HOST="${OLLAMA_HOST:-http://ollama:11434}"
MODEL="${OLLAMA_MODEL:-mistral}"

echo "======================================"
echo "EduMate Docker Initialization"
echo "======================================"

# Wait for Ollama to be available
echo "Waiting for Ollama service at $OLLAMA_HOST..."
for i in {1..30}; do
    if curl -s "$OLLAMA_HOST/api/tags" > /dev/null 2>&1; then
        echo "✓ Ollama is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "✗ Ollama service not available after 30 attempts"
        exit 1
    fi
    echo "  Attempt $i/30: waiting..."
    sleep 2
done

# Check if model is already pulled
echo ""
echo "Checking for model: $MODEL"
if curl -s "$OLLAMA_HOST/api/tags" | grep -q "\"name\":\"$MODEL\""; then
    echo "✓ Model $MODEL is already available"
else
    echo "Pulling model $MODEL (this may take several minutes)..."
    curl -X POST "$OLLAMA_HOST/api/pull" -d "{\"name\":\"$MODEL\"}" 2>&1 | \
        grep -E "status|total|completed" || true
    echo "✓ Model $MODEL pulled successfully"
fi

# Run ingestion
echo ""
echo "Running ingestion to build vector index..."
cd /app
python ingest.py
echo "✓ Ingestion complete"

echo ""
echo "======================================"
echo "Initialization complete!"
echo "======================================"
