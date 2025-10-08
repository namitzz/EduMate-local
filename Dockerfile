# Root-level Dockerfile for EduMate Backend API
# 
# This Dockerfile builds the backend API service for deployment platforms
# that expect a Dockerfile in the root directory.
# 
# For full multi-service deployment (ollama + backend + ui), use:
#   docker compose up --build
# 
# For standalone backend deployment:
#   docker build -t edumate-backend .
#   docker run -p 8000:8000 -e OLLAMA_HOST=<your-ollama-host> edumate-backend

FROM python:3.11-slim

WORKDIR /app

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install dependencies
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Copy corpus directory for document ingestion
COPY corpus/ ./corpus/

# Fly.io will set PORT env var, default to 8000 for local development
ENV PORT=8000
EXPOSE 8000

CMD uvicorn main:app --host 0.0.0.0 --port ${PORT}
