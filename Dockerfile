# Multi-stage Dockerfile for EduMate single-container web host
# Packages API + UI + model in one image

FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/ ./backend/

# Copy app wrapper
COPY app/ ./app/

# Copy UI build (if present)
# The ui/build folder should contain the built static files
COPY ui/build/ ./ui/build/ 2>/dev/null || mkdir -p ./ui/build

# Copy model folder (if present)
# Place your model files in the models/ directory
COPY models/ ./models/ 2>/dev/null || mkdir -p ./models

# Copy startup script
COPY start.sh .
RUN chmod +x start.sh

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV MODEL_PATH=/app/models

# Run the application
CMD ["./start.sh"]
