FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Optional system deps for building wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

# Default port: 8080 (ensure fly.toml internal_port matches)
# Replace main:app below if your module/variable are different (e.g. app:app)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
