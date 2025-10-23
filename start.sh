#!/bin/bash
# Startup script for EduMate single-container web host
# Runs Gunicorn with Uvicorn workers for optimal FastAPI performance

set -e

echo "Starting EduMate web host..."
echo "Environment:"
echo "  - MODEL_PATH: ${MODEL_PATH:-/app/models}"
echo "  - OPENROUTER_MODEL: ${OPENROUTER_MODEL:-openai/gpt-3.5-turbo}"
echo "  - FAST_MODE: ${FAST_MODE:-1}"

# Start Gunicorn with Uvicorn workers
# - Bind to all interfaces on port 8000
# - Use Uvicorn worker class for async support
# - 4 workers for production (adjust based on CPU cores)
# - Timeout set to 120s for long-running model inference
exec gunicorn app.main:app \
    --bind 0.0.0.0:8000 \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
