# EduMate - AI Study Assistant

A lightweight RAG chatbot for students, deployed on **Streamlit** and **Fly.io** using **OpenRouter**.

## Architecture

- **UI**: Streamlit (simple chat interface)
- **Backend**: FastAPI (deployed on Fly.io)
- **Vector DB**: ChromaDB (for document retrieval)
- **Embeddings**: SentenceTransformers (`all-MiniLM-L6-v2`)
- **LLM**: OpenRouter API (`gpt-3.5-turbo`)

## Live Demo

- **Frontend**: Run locally with `streamlit run ui/app_simple.py`
- **Backend API**: https://edumate-local.fly.dev

## Quick Start

### 1. Run Streamlit UI Locally

```bash
cd ui
pip install -r requirements.txt
streamlit run app_simple.py
```

The UI is pre-configured to connect to the Fly.io backend at `https://edumate-local.fly.dev`

### 2. Deploy Backend to Fly.io

If you need to redeploy the backend:

```bash
cd backend
fly deploy
```

The backend is configured with:
- OpenRouter API key (pre-configured)
- Fast Mode enabled (4-6 second responses)
- GPT-3.5-turbo model

## Configuration

The app is pre-configured for OpenRouter. Configuration in `backend/config.py`:

- `USE_OPENAI=1` - Uses OpenRouter by default
- `OPENAI_API_KEY` - Pre-configured API key
- `OPENAI_MODEL=openai/gpt-3.5-turbo` - Default model
- `FAST_MODE=1` - Optimized for speed

## Adding Documents

Place your course materials in `backend/corpus/` directory:
- Supported formats: PDF, DOCX, PPTX, TXT, HTML

Then run:
```bash
cd backend
python ingest.py
```

This will build the vector index from your documents.

## How It Works

1. User asks a question via Streamlit UI
2. UI sends request to Fly.io backend
3. Backend retrieves relevant chunks from ChromaDB
4. OpenRouter generates answer based on retrieved context
5. Answer is displayed in UI with source citations



