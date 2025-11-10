FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Optional system deps for building wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
COPY backend/requirements.txt backend-requirements.txt

RUN pip install --upgrade pip && \
    pip install -r requirements.txt -r backend-requirements.txt || \
    pip install -r requirements.txt && echo "backend/requirements.txt missing, proceeding"

COPY . .

# Default port: 8080 (ensure fly.toml internal_port matches)
# Run the FastAPI app from the app module
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
