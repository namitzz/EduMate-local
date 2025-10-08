# EduMate Architecture

## System Overview

```
┌─────────────────┐
│  User Browser   │
└────────┬────────┘
         │
         │ HTTP
         ▼
┌─────────────────────────────┐
│   Streamlit UI (Local)      │
│   ui/app_simple.py          │
│   Port: 8501                │
└────────┬────────────────────┘
         │
         │ REST API
         │ https://edumate-local.fly.dev
         ▼
┌─────────────────────────────┐
│  FastAPI Backend (Fly.io)   │
│  backend/main.py            │
│  ┌─────────────────────┐   │
│  │  /chat endpoint     │   │
│  │  ┌───────────────┐  │   │
│  │  │ Retrieval     │  │   │
│  │  │ (ChromaDB)    │  │   │
│  │  └───────┬───────┘  │   │
│  │          │          │   │
│  │          ▼          │   │
│  │  ┌───────────────┐  │   │
│  │  │ LLM Provider  │  │   │
│  │  │ (OpenRouter)  │  │   │
│  │  └───────────────┘  │   │
│  └─────────────────────┘   │
└────────┬────────────────────┘
         │
         │ OpenAI-compatible API
         │ https://openrouter.ai/api/v1
         ▼
┌─────────────────────────────┐
│   OpenRouter API            │
│   ┌─────────────────────┐   │
│   │ GPT-3.5-turbo       │   │
│   │ (or other models)   │   │
│   └─────────────────────┘   │
└─────────────────────────────┘
```

## Data Flow

1. **User Query** → Streamlit UI
2. **API Request** → Fly.io Backend (`/chat` endpoint)
3. **Document Retrieval** → ChromaDB (finds relevant context)
4. **LLM Generation** → OpenRouter API (generates answer)
5. **Response** → Backend → UI → User

## Components

### Frontend (Streamlit)
- **Location**: `ui/app_simple.py`
- **Port**: 8501
- **Features**: 
  - Simple chat interface
  - Source citations
  - API health monitoring
  - Clean history

### Backend (FastAPI)
- **Location**: `backend/main.py`
- **Hosting**: Fly.io (https://edumate-local.fly.dev)
- **Features**:
  - `/health` - Health check
  - `/chat` - Main chat endpoint (non-streaming)
  - `/chat_stream` - Streaming endpoint
  - RAG (Retrieval Augmented Generation)
  - Fast Mode optimization

### LLM Provider (OpenRouter)
- **API**: https://openrouter.ai/api/v1
- **Model**: openai/gpt-3.5-turbo
- **Key**: Pre-configured
- **Features**:
  - OpenAI-compatible API
  - Multiple model options
  - Pay-per-use pricing

### Vector Database (ChromaDB)
- **Location**: `backend/chroma_db/`
- **Model**: sentence-transformers/all-MiniLM-L6-v2
- **Features**:
  - Document embeddings
  - Semantic search
  - Fast retrieval

## Configuration

### Environment Variables

**Backend (production)**:
```bash
USE_OPENAI=1
OPENAI_API_KEY=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
OPENAI_MODEL=openai/gpt-3.5-turbo
FAST_MODE=1
```

**Frontend**:
```python
API_BASE_URL = "https://edumate-local.fly.dev/"
```

## Deployment

### Backend (Fly.io)
```bash
cd backend
fly deploy
```

### Frontend (Local)
```bash
cd ui
streamlit run app_simple.py
```

## API Endpoints

### GET /health
Health check endpoint
```json
Response: {"ok": true}
```

### POST /chat
Main chat endpoint (non-streaming)
```json
Request: {
  "messages": [
    {"role": "user", "content": "question"}
  ]
}

Response: {
  "answer": "generated answer",
  "sources": ["source1", "source2"]
}
```

### POST /chat_stream
Streaming chat endpoint
```json
Request: {
  "messages": [...],
  "mode": "docs|coach|facts"
}

Response: Streaming text
```

## Performance

- **Fast Mode**: Enabled by default
- **Response Time**: 4-6 seconds (target)
- **Retrieval**: Top-3 chunks (optimized)
- **Generation**: 400 max tokens
- **Concurrency**: 1 (sequential)

## Security

- ✅ HTTPS enabled (Fly.io automatic)
- ✅ CORS configured
- ✅ API key in environment variables
- ⚠️ No authentication (add if needed)
- ⚠️ Rate limiting not configured
