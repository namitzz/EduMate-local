# EduMate Setup Guide

## Current Configuration

This repository is configured for **production deployment** using:
- **OpenRouter API** for LLM (GPT-3.5-turbo)
- **Fly.io** for backend hosting
- **Streamlit** for frontend UI

### ✅ What's Configured

1. **Backend** (`backend/`)
   - OpenRouter API key pre-configured
   - Fast Mode enabled for 4-6 second responses
   - Fly.io deployment config in `backend/fly.toml`

2. **Frontend** (`ui/`)
   - Streamlit app (`app_simple.py`)
   - Pre-configured to connect to Fly.io backend
   - Simple chat interface with source citations

### 🚀 Quick Start

#### Run Streamlit UI (Local)

```bash
cd ui
pip install -r requirements.txt
streamlit run app_simple.py
```

The UI will connect to the live backend at `https://edumate-local.fly.dev`

#### Deploy Backend to Fly.io (If needed)

```bash
cd backend
fly deploy
```

### 📝 Configuration Details

**Backend (`backend/config.py`):**
- `USE_OPENAI = "1"` - Uses OpenRouter by default
- `OPENAI_API_KEY = "sk-or-v1-..."` - Pre-configured
- `OPENAI_MODEL = "openai/gpt-3.5-turbo"` - Default model
- `FAST_MODE = "1"` - Enabled for speed

**Backend Fly.io (`backend/fly.toml`):**
- Configured for Fly.io free tier
- Environment variables set for OpenRouter
- Auto-start/stop enabled to save resources

**Frontend (`ui/app_simple.py`):**
- `API_BASE_URL = "https://edumate-local.fly.dev/"` - Points to Fly.io backend

### 🔧 Customization

To use a different OpenRouter model, edit `backend/config.py`:
```python
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "openai/gpt-4")  # Change to gpt-4
```

To use a different API key, edit `backend/config.py`:
```python
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-new-key-here")
```

### 📚 Adding Documents

1. Place documents in `backend/corpus/` (PDF, DOCX, PPTX, TXT, HTML)
2. Run the ingestion script:
   ```bash
   cd backend
   python ingest.py
   ```
3. Redeploy to Fly.io:
   ```bash
   fly deploy
   ```

### ✅ Verification

Test the backend health:
```bash
curl https://edumate-local.fly.dev/health
```

Should return: `{"ok": true}`

### 🌐 Architecture

```
User Browser
    ↓
Streamlit UI (local)
    ↓
FastAPI Backend (Fly.io)
    ↓
OpenRouter API (GPT-3.5-turbo)
```
