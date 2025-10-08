# EduMate - AI Module Convenor Assistant

An intelligent RAG-based Module Convenor Assistant that provides personalized academic guidance — not just a Q&A bot, but an AI guide inspired by Prof. Zeng's mentorship style.

## 🎯 What Makes EduMate Special

Unlike basic chatbots, EduMate acts as a **mini version of your module convenor**, providing:

- **Intelligent Guidance**: Understands assignment context, deadlines, and academic intent
- **Personalized Support**: Maintains conversation memory for tailored responses
- **Academic Mentorship**: Friendly and supportive style inspired by Prof. Zeng
- **RAG-Powered**: Retrieves and cites relevant course materials
- **Multiple Modes**: Convenor (recommended), Docs Q&A, Study Coach, Quick Facts

## Architecture

- **UI**: Streamlit (simple chat interface with mode selection)
- **Backend**: FastAPI (deployed on Fly.io)
- **Vector DB**: ChromaDB (for document retrieval)
- **Memory**: Session-based conversation tracking
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
- Session memory enabled

## Configuration

The app is pre-configured for OpenRouter. Configuration in `backend/config.py`:

- `USE_OPENAI=1` - Uses OpenRouter by default
- `OPENAI_API_KEY` - Pre-configured API key
- `OPENAI_MODEL=openai/gpt-3.5-turbo` - Default model
- `FAST_MODE=1` - Optimized for speed
- `ENABLE_SESSION_MEMORY=1` - Conversation memory enabled
- `CONVENOR_NAME=Prof. Zeng` - Convenor persona
- `MAX_SESSION_MESSAGES=10` - Recent conversation history

## Modes

### 🎓 Convenor Mode (Recommended)
The intelligent Module Convenor mode that:
- Understands assignment context (essays, reports, labs, etc.)
- Detects student intent (needs help, wants feedback, etc.)
- Provides personalized academic guidance
- Uses conversation memory for tailored responses
- Maintains Prof. Zeng's mentorship style

### 📚 Document Q&A Mode
Standard RAG mode for direct questions about course materials with source citations.

### 💪 Study Coach Mode
General study advice and motivation without retrieval.

### ⚡ Quick Facts Mode
Brief, factual answers for quick questions.

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

### Standard Flow (Document Q&A):
1. User asks a question via Streamlit UI
2. UI sends request to Fly.io backend
3. Backend retrieves relevant chunks from ChromaDB
4. OpenRouter generates answer based on retrieved context
5. Answer is displayed in UI with source citations

### Enhanced Convenor Mode Flow:
1. User asks a question (e.g., "Help with my essay")
2. **Assignment Context Analyzer** detects intent and assignment type
3. **Session Memory** retrieves previous conversation context
4. Backend retrieves relevant course materials (RAG)
5. **Convenor Helper** enhances prompt with:
   - Module convenor personality
   - Assignment guidance context
   - Previous conversation summary
6. OpenRouter generates personalized academic guidance
7. Response saved to session memory for future context

## New Features

### Session-Based Memory
- Tracks conversation history per session (1-hour timeout)
- Provides context-aware responses
- Helps assistant understand student's journey

### Assignment Context Understanding
- Detects assignment types (essay, report, lab, etc.)
- Identifies student needs (help, feedback, explanation)
- Recognizes deadline queries
- Generates appropriate guidance context

### Module Convenor Personality
- Friendly and supportive mentorship style
- Encourages critical thinking
- Provides guidance, not just answers
- Tailored to Prof. Zeng's approach

## Example Queries

**Convenor Mode:**
- "Help me understand the key concepts for my assignment"
- "I'm stuck on my essay - can you guide me?"
- "What should I focus on for the exam?"
- "Can you give me feedback on my approach to this problem?"
- "Explain the learning outcomes for this module"

**Document Q&A:**
- "What are the assessment criteria?"
- "When is the project deadline?"
- "What topics are covered in Week 5?"

**Study Coach:**
- "How should I prepare for exams?"
- "Tips for effective note-taking?"

## API Endpoints

### POST /chat
Main chat endpoint (non-streaming)
```json
Request: {
  "messages": [{"role": "user", "content": "question"}],
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

### GET /health
Health check endpoint
```json
Response: {"ok": true}
```



