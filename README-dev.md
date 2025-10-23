# EduMate Developer Guide - Single Container Deployment

This guide explains how to build and run EduMate as a single-container web host that packages the API, UI, and model together.

## Overview

The single-container deployment packages:
- **Backend API**: FastAPI application from `backend/`
- **Frontend UI**: Static build from `ui/build/`
- **Model**: Files from `models/` directory
- **Wrapper**: Unified FastAPI app in `app/main.py`

## Prerequisites

- Docker and Docker Compose installed
- OpenRouter API key (get free credits at https://openrouter.ai/)
- (Optional) Built UI in `ui/build/`
- (Optional) Model files in `models/`

## Quick Start

### 1. Set Environment Variables

Create a `.env` file in the project root:

```bash
# Required: OpenRouter API key
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Optional: Model configuration
MODEL_PATH=/app/models
OPENROUTER_MODEL=openai/gpt-3.5-turbo

# Optional: Performance tuning
FAST_MODE=1
MAX_ACTIVE_GENERATIONS=1
```

### 2. Build and Run with Docker Compose

```bash
# Build the image
docker-compose build

# Start the service
docker-compose up

# Or run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

The application will be available at http://localhost:8000

### 3. Access the Application

- **UI**: http://localhost:8000/ (if ui/build exists)
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health
- **Model Info**: http://localhost:8000/api/model-info

## Directory Structure

```
EduMate-local/
├── Dockerfile              # Container image definition
├── docker-compose.yml      # Local development orchestration
├── start.sh               # Startup script with Gunicorn+Uvicorn
├── requirements.txt       # Python dependencies
├── app/
│   └── main.py           # FastAPI wrapper (mounts backend & UI)
├── backend/              # Existing backend code
│   ├── main.py          # Backend FastAPI app
│   ├── config.py        # Configuration
│   └── ...              # Other backend modules
├── ui/
│   └── build/           # Built frontend (place here)
│       ├── index.html
│       └── static/
└── models/              # Model files (place here)
    └── your-model/
```

## Building UI

If you have a frontend application, build it and place the output in `ui/build/`:

```bash
# Example for React app
cd ui/your-frontend-app
npm install
npm run build
cp -r build ../build/

# Or for other frameworks, ensure the build output goes to ui/build/
```

## Adding Models

Place your model files in the `models/` directory:

```bash
models/
└── your-model/
    ├── config.json
    ├── pytorch_model.bin
    └── tokenizer.json
```

The `MODEL_PATH` environment variable points to `/app/models` by default.

## Development Workflow

The docker-compose setup mounts local directories for live editing:

1. **Edit code locally**: Changes in `backend/`, `app/`, `ui/build/`, `models/`
2. **Auto-reload**: Gunicorn watches for changes (depending on configuration)
3. **View logs**: `docker-compose logs -f edumate`
4. **Restart if needed**: `docker-compose restart edumate`

## Production Deployment

### Build for Production

```bash
# Build the image with a tag
docker build -t edumate:latest .

# Run the container
docker run -d \
  -p 8000:8000 \
  -e OPENROUTER_API_KEY=your-key \
  --name edumate \
  edumate:latest
```

### Environment Variables

Required:
- `OPENROUTER_API_KEY`: Your OpenRouter API key

Optional:
- `MODEL_PATH`: Path to model files (default: `/app/models`)
- `OPENROUTER_MODEL`: Model to use (default: `openai/gpt-3.5-turbo`)
- `OPENROUTER_BASE_URL`: API base URL (default: `https://openrouter.ai/api/v1`)
- `FAST_MODE`: Enable fast mode (default: `1`)
- `MAX_ACTIVE_GENERATIONS`: Max concurrent generations (default: `1`)

## Architecture

### Request Flow

1. **UI Requests**: 
   - Browser → `http://localhost:8000/` → Served from `ui/build/index.html`
   - Static assets → `http://localhost:8000/static/*` → Served from `ui/build/static/`

2. **API Requests**:
   - UI/Client → `http://localhost:8000/api/*` → Routed to backend FastAPI app
   - Backend uses existing modules: retrieval, models, memory, persona

3. **Model Loading**:
   - Lazy loading on first prediction request
   - Reads from `MODEL_PATH` environment variable
   - Currently uses OpenRouter API (no local model needed)

### Components

- **Gunicorn**: Production WSGI server
- **Uvicorn Workers**: Async support for FastAPI
- **FastAPI Wrapper** (`app/main.py`): Routes requests to backend and serves UI
- **Backend App** (`backend/main.py`): Existing EduMate API
- **Static Files**: Pre-built UI served directly

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs edumate

# Verify environment variables
docker-compose config

# Rebuild if needed
docker-compose build --no-cache
```

### API not responding

```bash
# Check health endpoint
curl http://localhost:8000/health

# Check if backend is mounted
curl http://localhost:8000/api/health

# Inspect container
docker-compose exec edumate ls -la /app
```

### UI not loading

1. Check if `ui/build/` exists and contains `index.html`
2. Check if static files are in `ui/build/static/`
3. View container logs: `docker-compose logs edumate`
4. Verify build was copied: `docker-compose exec edumate ls -la /app/ui/build`

### Model not found

1. Check `MODEL_PATH` environment variable
2. Verify model files exist in `models/` directory
3. Check logs for model loading errors
4. Note: Current implementation uses OpenRouter API, no local model needed

### Performance issues

- Adjust `MAX_ACTIVE_GENERATIONS` in `.env`
- Increase Gunicorn workers in `start.sh`
- Enable `FAST_MODE=1` for optimized settings
- Consider using a faster model: `OPENROUTER_MODEL=meta-llama/llama-3.1-8b-instruct:free`

## Advanced Configuration

### Customize Gunicorn Settings

Edit `start.sh`:

```bash
exec gunicorn app.main:app \
    --bind 0.0.0.0:8000 \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 2 \              # Adjust based on CPU cores
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
```

### Add Custom Dependencies

Edit `requirements.txt` and uncomment or add packages as needed:

```txt
# Uncomment for Hugging Face models
# transformers>=4.30.0
# accelerate>=0.20.0

# Add your custom dependencies
your-package==1.0.0
```

Then rebuild: `docker-compose build`

## Additional Resources

- [EduMate README](README.md) - Main project documentation
- [Cloud Deployment Guide](CLOUD_DEPLOYMENT.md) - Deploy to Fly.io and Streamlit Cloud
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review container logs: `docker-compose logs -f`
3. Open an issue on GitHub
4. See the main [README](README.md) for more help
