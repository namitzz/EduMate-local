# EduMate - AI Module Convenor Assistant

An intelligent AI-powered Module Convenor Assistant that provides **personalized academic guidance, feedback, and mentorship** to students. More than just a Q&A bot, EduMate acts as a mini version of your module convenor, understanding course content deeply and offering tailored support.

> 🚀 **[Quick Start - Deploy in 5 Minutes](QUICKSTART.md)** | 📖 **[Full Deployment Guide](STREAMLIT_DEPLOYMENT.md)**

## 🎯 What Makes EduMate Special?

EduMate goes beyond basic document retrieval to provide **intelligent academic guidance**:

- **🎓 Module Convenor Persona** - Acts like an experienced university professor
- **🧠 Context-Aware Conversations** - Remembers your discussion and provides continuity
- **📝 Intent Detection** - Understands whether you need assignment help, concept clarification, or exam prep
- **💡 Tailored Feedback** - Provides structured guidance, not just answers
- **📚 RAG-Powered** - References actual course materials with citations
- **🤝 Mentorship Style** - Encouraging, pedagogical, and supportive

### Interaction Types

EduMate automatically detects your intent and adapts its response style:

1. **Assignment Help** - Structured guidance on coursework, rubric interpretation
2. **Concept Clarification** - Clear explanations with examples and analogies
3. **Exam Preparation** - Study strategies, topic prioritization
4. **Study Planning** - Time management, learning techniques
5. **Progress Feedback** - Constructive support and improvement suggestions
6. **General Queries** - Course information and quick facts

> 🚀 **[Quick Start - Deploy in 5 Minutes](QUICKSTART.md)** | 📖 **[Full Deployment Guide](STREAMLIT_DEPLOYMENT.md)**

## Architecture

- **UI**: Streamlit (enhanced chat interface with session management)
- **Backend**: FastAPI (deployed on Fly.io)
- **Vector DB**: ChromaDB (for document retrieval)
- **Embeddings**: SentenceTransformers (`all-MiniLM-L6-v2`)
- **LLM**: OpenRouter API (`gpt-3.5-turbo`)
- **Memory**: In-memory conversation tracking with pattern detection
- **Persona**: Module Convenor prompt system with intent detection

## Live Demo

- **Frontend**: Deploy on Streamlit Cloud (see deployment guide) or run locally
- **Backend API**: https://edumate-local.fly.dev

## 🚀 Deploy to Streamlit Cloud

**For easy student access, deploy the frontend to Streamlit Cloud (free tier):**

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app" and select:
   - Repository: `yourusername/EduMate-local`
   - Branch: `main`
   - Main file: `ui/app_simple.py`
4. Click "Deploy"

Students can then access your app at `https://your-app-name.streamlit.app` - no login required!

📖 **Full deployment guide**: See [STREAMLIT_DEPLOYMENT.md](STREAMLIT_DEPLOYMENT.md) for detailed instructions.

## Quick Start

### Option 1: Run Locally (Development)

```bash
cd ui
pip install -r requirements.txt
streamlit run app_simple.py
```

The UI is pre-configured to connect to the Fly.io backend at `https://edumate-local.fly.dev`

### Option 2: Deploy to Streamlit Cloud (Production)

For easy student access, deploy the frontend to Streamlit Cloud:

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app" and configure:
   - Repository: Your fork of this repo
   - Branch: `main`
   - Main file: `ui/app_simple.py`
3. Click "Deploy"

See [STREAMLIT_DEPLOYMENT.md](STREAMLIT_DEPLOYMENT.md) for detailed instructions.

### Deploy Backend to Fly.io

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
- `ENABLE_CONVERSATION_MEMORY=1` - Context-aware conversations
- `MAX_CONVERSATION_HISTORY=10` - Number of turns to remember

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

1. **Student asks a question** via Streamlit UI (with session tracking)
2. **UI sends request** to Fly.io backend with conversation context
3. **Intent detection** identifies the type of academic support needed
4. **Backend retrieves** relevant chunks from ChromaDB
5. **Module Convenor persona** generates tailored academic guidance
6. **Conversation memory** tracks context for follow-up questions
7. **Answer displayed** in UI with source citations and suggestions

## 💰 Free Tier & Cost Management

This setup uses free tiers to minimize costs:

### Streamlit Cloud (Free Tier)
- ✅ 1 private app or unlimited public apps
- ✅ 1 GB RAM
- ✅ Unlimited viewers
- **Cost**: $0/month

### Fly.io (Free Tier)
- ✅ 3 VMs with 256MB RAM
- ✅ 160GB data transfer/month
- ✅ Auto-stop when idle (configured)
- **Cost**: $0/month for typical usage

### OpenRouter API
- ✅ Pay-per-use only
- ✅ GPT-3.5-turbo: ~$0.0015 per 1,000 tokens
- ✅ Example: 1,000 student questions ≈ $3-5
- **Cost**: Only when students use it

**Total**: $0 base cost + minimal API usage fees

### Set Spending Limits
```bash
# Fly.io spending cap (recommended)
fly orgs billing-limits set

# Monitor usage
fly billing show
```

## 📖 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - ⚡ Deploy in 5 minutes
- **[STREAMLIT_DEPLOYMENT.md](STREAMLIT_DEPLOYMENT.md)** - Complete deployment guide for Streamlit Cloud + Fly.io
- **[SETUP.md](SETUP.md)** - Configuration details
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
- **[VERIFICATION.md](VERIFICATION.md)** - Verification steps



