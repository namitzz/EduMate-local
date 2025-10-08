# EduMate Architecture

## System Overview

```
┌─────────────────┐
│  User Browser   │
└────────┬────────┘
         │
         │ HTTP
         ▼
┌─────────────────────────────────────┐
│   Streamlit UI (Local)              │
│   ui/app_simple.py                  │
│   Port: 8501                        │
│   ┌─────────────────────────────┐   │
│   │ Mode Selector:              │   │
│   │ - Convenor (Recommended)    │   │
│   │ - Document Q&A              │   │
│   │ - Study Coach               │   │
│   │ - Quick Facts               │   │
│   └─────────────────────────────┘   │
└────────┬────────────────────────────┘
         │
         │ REST API (with session_id & mode)
         │ https://edumate-local.fly.dev
         ▼
┌──────────────────────────────────────────┐
│  FastAPI Backend (Fly.io)                │
│  backend/main.py                         │
│  ┌──────────────────────────────────┐   │
│  │  /chat & /chat_stream endpoints  │   │
│  │  ┌────────────────────────────┐  │   │
│  │  │ Session Memory             │  │   │
│  │  │ (session_memory.py)        │  │   │
│  │  │ - Tracks conversation      │  │   │
│  │  │ - 1-hour timeout           │  │   │
│  │  └────────────────────────────┘  │   │
│  │  ┌────────────────────────────┐  │   │
│  │  │ Assignment Context Analyzer│  │   │
│  │  │ (convenor_helper.py)       │  │   │
│  │  │ - Detects intent           │  │   │
│  │  │ - Extracts assignment type │  │   │
│  │  └────────────────────────────┘  │   │
│  │  ┌────────────────────────────┐  │   │
│  │  │ Retrieval (ChromaDB)       │  │   │
│  │  │ (retrieval.py)             │  │   │
│  │  └────────┬───────────────────┘  │   │
│  │           │                      │   │
│  │           ▼                      │   │
│  │  ┌────────────────────────────┐  │   │
│  │  │ Prompt Composer            │  │   │
│  │  │ - Module Convenor style    │  │   │
│  │  │ - Session context          │  │   │
│  │  │ - Assignment guidance      │  │   │
│  │  └────────┬───────────────────┘  │   │
│  │           │                      │   │
│  │           ▼                      │   │
│  │  ┌────────────────────────────┐  │   │
│  │  │ LLM Provider               │  │   │
│  │  │ (OpenRouter/Ollama)        │  │   │
│  │  └────────────────────────────┘  │   │
│  └──────────────────────────────────┘   │
└────────┬─────────────────────────────────┘
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

### Standard Document Q&A Flow:
1. **User Query** → Streamlit UI
2. **API Request** → Fly.io Backend (`/chat` endpoint with mode="docs")
3. **Document Retrieval** → ChromaDB (finds relevant context)
4. **Prompt Building** → Standard RAG prompt with citations
5. **LLM Generation** → OpenRouter API (generates answer)
6. **Response** → Backend → UI → User

### Enhanced Convenor Mode Flow:
1. **User Query** → Streamlit UI (e.g., "Help with my essay")
2. **API Request** → Backend (`/chat` endpoint with mode="convenor", session_id)
3. **Context Analysis** → Assignment Context Analyzer
   - Detects: assignment type (essay), intent (needs help)
4. **Memory Retrieval** → Session Memory
   - Fetches previous conversation context
5. **Document Retrieval** → ChromaDB (RAG)
6. **Prompt Enhancement** → Convenor Helper
   - Adds Module Convenor personality
   - Includes assignment guidance context
   - Incorporates session history
7. **LLM Generation** → OpenRouter (personalized guidance)
8. **Memory Update** → Save response to session
9. **Response** → Backend → UI → User

## Components

### Frontend (Streamlit)
- **Location**: `ui/app_simple.py`
- **Port**: 8501
- **Features**: 
  - Mode selector (Convenor, Docs, Coach, Facts)
  - Session ID tracking (UUID-based)
  - Source citations display
  - API health monitoring
  - Clear conversation button

### Backend (FastAPI)
- **Location**: `backend/main.py`
- **Hosting**: Fly.io (https://edumate-local.fly.dev)
- **Endpoints**:
  - `/health` - Health check
  - `/chat` - Main chat endpoint (non-streaming)
  - `/chat_stream` - Streaming endpoint
- **Features**:
  - RAG (Retrieval Augmented Generation)
  - Session-based memory
  - Multiple modes (convenor, docs, coach, facts)
  - Assignment context understanding
  - Fast Mode optimization

### Session Memory
- **Location**: `backend/session_memory.py`
- **Features**:
  - Tracks conversation history per session
  - 1-hour session timeout
  - Context summary generation
  - Automatic cleanup of old sessions
  - Max 10 messages per session (configurable)

### Assignment Context Analyzer
- **Location**: `backend/convenor_helper.py`
- **Features**:
  - Intent detection (help, feedback, explanation, deadline)
  - Assignment type extraction (essay, report, lab, etc.)
  - Guidance context generation
  - Module Convenor system prompt
  - Prompt enhancement with context awareness

### LLM Provider (OpenRouter)
- **API**: https://openrouter.ai/api/v1
- **Model**: openai/gpt-3.5-turbo
- **Key**: Pre-configured
- **Features**:
  - OpenAI-compatible API
  - Multiple model options
  - Pay-per-use pricing
  - Streaming support

### Vector Database (ChromaDB)
- **Location**: `backend/chroma_db/`
- **Model**: sentence-transformers/all-MiniLM-L6-v2
- **Features**:
  - Document embeddings
  - Semantic search
  - Fast retrieval
  - BM25-like re-ranking

## Configuration

### Environment Variables

**Backend (production)**:
```bash
USE_OPENAI=1
OPENAI_API_KEY=sk-or-v1-...
OPENAI_MODEL=openai/gpt-3.5-turbo
FAST_MODE=1
ENABLE_SESSION_MEMORY=1
MAX_SESSION_MESSAGES=10
CONVENOR_NAME=Prof. Zeng
CONVENOR_STYLE=friendly and supportive, like a dedicated module convenor
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
  ],
  "mode": "convenor|docs|coach|facts",
  "session_id": "unique-session-id"
}

Response: {
  "answer": "generated answer with guidance",
  "sources": ["source1", "source2"]
}
```

### POST /chat_stream
Streaming chat endpoint
```json
Request: {
  "messages": [...],
  "mode": "convenor|docs|coach|facts",
  "session_id": "unique-session-id"
}

Response: Streaming text
```

## Modes Explained

### 🎓 Convenor Mode
- **Purpose**: Intelligent academic guidance
- **Retrieval**: Yes (RAG with course materials)
- **Memory**: Yes (session-based)
- **Context**: Assignment type, student intent, conversation history
- **Style**: Module convenor mentorship (Prof. Zeng)
- **Use Cases**: 
  - Assignment help and guidance
  - Feedback requests
  - Concept explanations with academic context
  - Personalized learning support

### 📚 Document Q&A Mode
- **Purpose**: Direct questions about course materials
- **Retrieval**: Yes (RAG)
- **Memory**: No
- **Context**: Document content only
- **Style**: Concise and factual
- **Use Cases**:
  - Finding specific information
  - Quick lookups
  - Citation-based answers

### 💪 Study Coach Mode
- **Purpose**: General study advice
- **Retrieval**: No
- **Memory**: No
- **Context**: None
- **Style**: Encouraging and practical
- **Use Cases**:
  - Study tips
  - Motivation
  - Time management advice

### ⚡ Quick Facts Mode
- **Purpose**: Brief factual answers
- **Retrieval**: No
- **Memory**: No
- **Context**: None
- **Style**: Very concise
- **Use Cases**:
  - Quick questions
  - Yes/no answers
  - Simple definitions

## Performance

- **Fast Mode**: Enabled by default
- **Response Time**: 4-6 seconds (target)
- **Retrieval**: Top-3 chunks (optimized)
- **Generation**: 400 max tokens
- **Concurrency**: 1 (sequential)
- **Session Memory**: In-memory with 1-hour timeout

## Security

- ✅ HTTPS enabled (Fly.io automatic)
- ✅ CORS configured
- ✅ API key in environment variables
- ✅ Session-based isolation
- ⚠️ No authentication (add if needed)
- ⚠️ Rate limiting not configured

## Key Improvements

### From Basic Q&A to Intelligent Assistant

**Before:**
- Simple question answering
- No context awareness
- Generic responses
- No conversation memory

**After:**
- Intelligent academic guidance
- Assignment context understanding
- Personalized mentorship style
- Session-based conversation memory
- Multiple specialized modes
- Enhanced prompt engineering
