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
1) Install Ollama and pull a model on your host:
```bash
ollama pull mistral
```

2) From project root:
```bash
docker compose up --build
```

Then open http://localhost:8501.

## How it works
- `backend/ingest.py` parses files in `./corpus` (PDF/DOCX/PPTX/TXT/HTML)
- Chunks (~1000 tokens, 200 overlap) → embeddings → ChromaDB
- `/chat` uses HyDE + multi-query and a light keyword-scoring on top of vector results
- Streamlit shows answers with inline citations and a sources panel

## Config
See `backend/config.py`.



