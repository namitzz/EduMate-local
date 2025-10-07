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
streamlit run app.py
```

Open http://localhost:8501. The bot answers only from your docs in `corpus/`.

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
EduMate now includes an **opt-in Fast Mode** and a **public-friendly UI** designed for small pilots (6 students, zero cost). Fast Mode optimizes retrieval and generation for lower latency while the public UI provides a cleaner interface with streaming responses.

### Features
- **Fast Mode**: Smaller chunks, fewer retrievals (top-k=3), context trimming for faster responses
- **Public UI**: Clean interface with streaming, mode selector (Course Docs/Study Coach/Quick Facts)
- **Evidence Mode**: Optional toggle to show when answers lack source citations
- **Concurrency Control**: Semaphore-based limiting to prevent overload

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

# Generation settings
TEMP=0.3
NUM_PREDICT=448
```

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

**With Fast Mode (`FAST_MODE=1`):**
- Top-K reduced from 8 to 3 chunks
- Context trimmed to 8000 chars max
- Uses smaller embedding model (all-MiniLM-L6-v2)
- First token typically arrives in 2-6 seconds

**With small model (qwen2.5:1.5b-instruct):**
- Significantly faster generation
- Still coherent for course Q&A
- Better for real-time pilot scenarios

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



