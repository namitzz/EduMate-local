A lightweight, RAG chatbot for students. Runs **entirely locally** using:
- **Streamlit** UI
- **FastAPI** backend
- **ChromaDB** (persisted locally)
- **SentenceTransformers** (`all-MiniLM-L6-v2`) for embeddings
- **Ollama** (e.g., `mistral` or `llama3`) for generation

## Quick Start (Local, no Docker)
1) Install [Ollama](https://ollama.com) and pull a small model:
```bash
ollama pull mistral
```

or:
```bash
ollama pull llama3
```

2) Terminal 1 (backend):
```bash
cd backend
python -m venv .venv && source .venv/Scripts/activate # Git Bash on Windows
pip install -r requirements.txt
python ingest.py # builds the vector index from ../corpus
uvicorn main:app --reload --port 8000
```

3) Terminal 2 (UI):
```bash
cd ui
python -m venv .venv && source .venv/Scripts/activate
pip install -r requirements.txt
# Choose one of these:
streamlit run app_simple.py  # Simple, beginner-friendly UI (recommended for learning)
# OR
streamlit run app.py         # Original UI with sources panel
# OR
streamlit run app_public.py  # Advanced UI with streaming and modes
```

Open http://localhost:8501. The bot answers only from your docs in `corpus/`.

### UI Options

EduMate provides three Streamlit interfaces:

1. **`app_simple.py`** ⭐ - Simple, beginner-friendly interface (NEW!)
   - ⭐ Best for learning and understanding the basics
   - Clean chat UI with source citations
   - API health monitoring in sidebar
   - Clear chat history button
   - Easy to read and modify (~180 lines)
   - Comprehensive documentation with examples
   - See [ui/INDEX.md](ui/INDEX.md) for complete documentation guide
   - See [ui/README_SIMPLE.md](ui/README_SIMPLE.md) for details

2. **`app.py`** - Original interface
   - Basic RAG functionality
   - Sources displayed in sidebar
   - Good for general use

3. **`app_public.py`** - Advanced production interface
   - Streaming responses
   - Three modes (docs/coach/facts)
   - Custom styling
   - Performance metrics
   - Best for production deployments

**Quick Start with Simple UI:**
```bash
cd ui
streamlit run app_simple.py
```

**Documentation:** See [ui/INDEX.md](ui/INDEX.md) for the complete documentation index.

## Quick Start (Docker)

**Recommended for the easiest setup!** Everything runs in containers - no manual installation needed.

1) Make sure you have [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed.

2) From the project root, run:
```bash
docker compose up --build
```

This will:
- Start an Ollama container and automatically pull the `mistral` model
- Build the vector index from documents in `./corpus`
- Start the FastAPI backend
- Start the Streamlit UI

3) Open http://localhost:8501 in your browser.

**Note:** The first run takes longer (5-10 minutes) because it downloads the Ollama model and builds embeddings. Subsequent runs are much faster as everything is cached.

To change the model, edit `OLLAMA_MODEL` in `docker-compose.yml` (under the `init` service) before running `docker compose up`.

To stop all services:
```bash
docker compose down
```

## How it works
- `backend/ingest.py` parses files in `./corpus` (PDF/DOCX/PPTX/TXT/HTML)
- Chunks (~1000 tokens, 200 overlap) → embeddings → ChromaDB
- `/chat` uses HyDE + multi-query and a light keyword-scoring on top of vector results
- Streamlit shows answers with inline citations and a sources panel

## Config
See `backend/config.py`.

## Pilot Mode (Fast Mode + Public UI)

### Overview
EduMate includes an **optimized Fast Mode** and a **public-friendly UI** designed for rapid responses (4-6 seconds). Fast Mode is **enabled by default** and optimizes retrieval and generation for lower latency while the public UI provides a cleaner interface with streaming responses.

### ✨ Recent Improvements
- **⚡ 4-6 Second Responses**: Optimized for fast replies with Fast Mode enabled by default
- **🎯 Enhanced Greeting Detection**: Responds to hi, hello, hey, and many greeting variations
- **🔍 Fuzzy Synonym Matching**: Better understands synonyms and finds closest matches in course materials
- **💫 Improved UI**: Cleaner design with better loading indicators and performance metrics
- **📦 Deployment Ready**: Complete deployment guide for GitHub and cloud platforms

### Features
- **Fast Mode**: Enabled by default - smaller chunks, fewer retrievals (top-k=3), optimized context
- **Smart Retrieval**: Fuzzy matching and synonym expansion for better results
- **Public UI**: Clean interface with streaming, mode selector (Course Docs/Study Coach/Quick Facts)
- **Evidence Mode**: Optional toggle to show when answers lack source citations
- **Concurrency Control**: Semaphore-based limiting to prevent overload
- **Performance Metrics**: Real-time response time tracking

### Quick Start (Fast Mode Enabled)

#### Prerequisites
```bash
# Optional: Pull a smaller, faster model for the pilot
ollama pull qwen2.5:1.5b-instruct

# OR use the default mistral
ollama pull mistral
```

#### Running with Fast Mode

**Terminal 1 (Backend with Fast Mode):**
```bash
cd backend
export FAST_MODE=1
export MAX_ACTIVE_GENERATIONS=1
# Optional: Use smaller model for faster responses
# export OLLAMA_MODEL=qwen2.5:1.5b-instruct
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 (Public UI):**
```bash
cd ui
export EDUMATE_API_URL=http://localhost:8000
streamlit run app_public.py --server.address 0.0.0.0 --server.port 8501
```

#### Access
- **Public UI**: http://localhost:8501 (clean interface, streaming)
- **Original UI**: Still available via `streamlit run app.py`
- **API**: http://localhost:8000

### Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
# Enable Fast Mode
FAST_MODE=1

# Model selection (use smaller model for faster pilot)
OLLAMA_MODEL=qwen2.5:1.5b-instruct  # or mistral:latest

# Concurrency (1 = sequential, good for 6 students)
MAX_ACTIVE_GENERATIONS=1

# Generation settings (optimized for 4-6s responses)
TEMP=0.3
NUM_PREDICT=400
```

### Deployment

For detailed deployment instructions including cloud deployment and Fly.io free tier, see [DEPLOYMENT.md](DEPLOYMENT.md).

**Quick Options:**

1. **Docker Compose (Full Stack - Recommended):**
   ```bash
   docker compose up --build
   ```
   Deploys Ollama + Backend + UI together.

2. **Root Dockerfile (Backend Only - Cloud Platforms):**
   ```bash
   docker build -t edumate-backend .
   docker run -p 8000:8000 -e OLLAMA_HOST=<your-ollama-host> edumate-backend
   ```
   For platforms like Railway, Render, or any service that auto-detects Dockerfiles in the root.

3. **Fly.io Free Tier (Cloud):**
   ```bash
   cd backend
   fly launch
   # Follow prompts, set billing limit to $0
   # Update frontend with: export API_BASE=https://edumate-local.fly.dev
   ```
   See [DEPLOYMENT.md](DEPLOYMENT.md) for complete Fly.io instructions.

Access at http://localhost:8501

### LAN Access for Students

To allow students on the same network to access EduMate:

1. **Find your machine's IP address:**
   ```bash
   # Linux/Mac
   hostname -I
   
   # Windows
   ipconfig
   ```

2. **Share the URL with students:**
   - Public UI: `http://YOUR_IP:8501`
   - API: `http://YOUR_IP:8000`

3. **Optional: Use Cloudflare Tunnel for remote access:**
   ```bash
   # Install cloudflared
   # See: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
   
   cloudflare tunnel --url http://localhost:8501
   ```

### Performance Notes

**With Fast Mode (enabled by default):**
- Top-K reduced from 8 to 3 chunks
- Context trimmed to 6000 chars max (optimized)
- MAX_TOKENS reduced to 400 for faster generation
- Uses smaller embedding model (all-MiniLM-L6-v2)
- Enhanced fuzzy matching and synonym support
- **Target: 4-6 seconds for first response**
- First token typically arrives in 2-4 seconds

**With small model (qwen2.5:1.5b-instruct):**
- Significantly faster generation
- Still coherent for course Q&A
- Better for real-time pilot scenarios

**Performance Tips:**
- Greetings get instant responses (< 1s)
- Use Fast Mode for optimal speed
- Check logs for performance metrics
- Reduce NUM_PREDICT if responses are still slow

### Rollback to Standard Mode

To return to the original behavior:
1. Unset or set `FAST_MODE=0` in your environment
2. Use the original UI: `streamlit run app.py`
3. Restart the backend

The `/chat` endpoint remains unchanged and works exactly as before.

### New Endpoints

- **POST `/chat`**: Original endpoint (unchanged)
- **POST `/chat_stream`**: New streaming endpoint
  - Accepts `{"messages": [...], "mode": "docs|coach|facts"}`
  - Returns streamed text tokens
  - Uses semaphore for concurrency control

### Modes in Public UI

1. **📚 Ask Course Docs** (docs): RAG mode with retrieval from course materials
2. **💡 Study Coach** (coach): General study tips without retrieval
3. **⚡ Quick Facts** (facts): Concise factual answers without retrieval



