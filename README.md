# EduMate - AI Module Convenor Assistant

An intelligent AI-powered Module Convenor Assistant that provides **personalized academic guidance, feedback, and mentorship** to students. More than just a Q&A bot, EduMate acts as a mini version of your module convenor, understanding course content deeply and offering tailored support.

## 🚀 Quick Deploy to Fly.io

**Deploy in 3 simple steps:**

1. **Get OpenRouter API key** at [openrouter.ai](https://openrouter.ai/) (free credits available)

2. **Deploy Backend to Fly.io:**
   ```bash
   # Install Fly.io CLI: https://fly.io/docs/hands-on/install-flyctl/
   fly auth login
   
   # Deploy from repository root
   fly launch --copy-config --yes
   fly secrets set OPENROUTER_API_KEY=your-key-here
   fly deploy
   ```

3. **Deploy Frontend to Streamlit Cloud:**
   - Fork this repository to your GitHub account
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - New app → select your forked repo → Main file: `ui/app_simple.py`
   - **Important:** If your Fly.io app name is different from "edumate-local":
     - In Streamlit settings → "Advanced settings" → "Environment variables"
     - Add: `EDUMATE_API_BASE` = `https://your-app-name.fly.dev`
   - Deploy!

**Total cost:** $0/month base + minimal API usage (~$0.0015 per 1K tokens)

> 📖 **Detailed instructions:** [Cloud Deployment Guide](CLOUD_DEPLOYMENT.md) | [Quick Start](QUICKSTART.md)

---

## 🎯 What Makes EduMate Special?

EduMate goes beyond basic document retrieval to provide **intelligent academic guidance**:

- **🎓 Module Convenor Persona** - Acts like an experienced university professor
- **🧠 Context-Aware Conversations** - Remembers your discussion and provides continuity
- **📝 Intent Detection** - Understands whether you need assignment help, concept clarification, or exam prep
- **💡 Tailored Feedback** - Provides structured guidance, not just answers
- **📚 RAG-Powered** - References actual course materials with citations
- **🤝 Mentorship Style** - Encouraging, pedagogical, and supportive
- **☁️ Cloud-Native** - Zero local setup required, $0 base cost

### Interaction Types

EduMate automatically detects your intent and adapts its response style:

1. **Assignment Help** - Structured guidance on coursework, rubric interpretation
2. **Concept Clarification** - Clear explanations with examples and analogies
3. **Exam Preparation** - Study strategies, topic prioritization
4. **Study Planning** - Time management, learning techniques
5. **Progress Feedback** - Constructive support and improvement suggestions
6. **General Queries** - Course information and quick facts

## Architecture

- **UI**: Streamlit Cloud (free tier)
- **Backend**: Fly.io (free tier)  
- **Vector DB**: ChromaDB (for document retrieval)
- **Embeddings**: SentenceTransformers (`all-MiniLM-L6-v2`)
- **LLM**: OpenRouter API (pay-as-you-go, ~$0.0015/1K tokens)
- **Memory**: In-memory conversation tracking with pattern detection
- **Persona**: Module Convenor prompt system with intent detection

## Quick Start (Local Development)

### Option 1: Run Frontend Locally

```bash
cd ui
pip install -r requirements.txt
streamlit run app_simple.py
```

The UI will connect to the cloud backend at `https://edumate-local.fly.dev` (or set `EDUMATE_API_BASE` env var)

### Option 2: Run Full Stack Locally

**Backend:**
```bash
cd backend
pip install -r requirements.txt

# Set your OpenRouter API key
export OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Optional: Ingest documents
python ingest.py

# Start backend
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd ui
export EDUMATE_API_BASE=http://localhost:8000
streamlit run app_simple.py
```

## Configuration

### Environment Variables

Set these in your deployment environment:

**Required:**
- `OPENROUTER_API_KEY` - Your OpenRouter API key (get from openrouter.ai)

**Optional (with defaults):**
- `OPENROUTER_MODEL` - Model to use (default: `openai/gpt-3.5-turbo`)
- `OPENROUTER_BASE_URL` - API base URL (default: `https://openrouter.ai/api/v1`)
- `FAST_MODE` - Enable fast mode (default: `1`)
- `TEMP` - LLM temperature (default: `0.3`)
- `NUM_PREDICT` - Max tokens (default: `400`)
- `ENABLE_CONVERSATION_MEMORY` - Enable context (default: `1`)
- `MAX_CONVERSATION_HISTORY` - Conversation turns (default: `10`)

### Backend Configuration

See `backend/config.py` for all available options.

### Frontend Configuration  

Update API URL in `ui/app_simple.py`:
```python
DEFAULT_API_BASE = "https://your-backend.fly.dev"
```

Or set environment variable:
```bash
export EDUMATE_API_BASE=https://your-backend.fly.dev
```

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

## 💰 Cost Breakdown

This setup uses free tiers to minimize costs:

### Streamlit Cloud (Free Tier)
- ✅ 1 private app or unlimited public apps
- ✅ 1 GB RAM per app
- ✅ Unlimited viewers
- **Cost**: $0/month

### Fly.io (Free Tier)
- ✅ 3 shared-cpu-1x VMs with 256MB RAM
- ✅ 160GB outbound data transfer/month
- ✅ Auto-stop when idle (configured)
- ✅ Scales to zero when not in use
- **Cost**: $0/month for typical usage

### OpenRouter API (Pay-as-you-go)
- ✅ No subscription or base fee
- ✅ GPT-3.5-turbo: ~$0.0015 per 1,000 tokens
- ✅ Free models available (with rate limits)
- ✅ Example: 1,000 student questions ≈ $3-5
- **Cost**: Only pay for what you use

**Total**: $0 base cost + minimal API usage fees

### Set Spending Limits
```bash
# Fly.io spending cap (recommended)
fly orgs billing-limits set --max-monthly-spend 5

# Monitor usage
fly billing show
```

### Use Free Models (Optional)

OpenRouter offers free models with rate limits:
- `meta-llama/llama-3.1-8b-instruct:free`
- `mistralai/mistral-7b-instruct:free`

Update in `backend/fly.toml` or set via:
```bash
fly secrets set OPENROUTER_MODEL=meta-llama/llama-3.1-8b-instruct:free
```

## 📖 Documentation

- **[CLOUD_DEPLOYMENT.md](CLOUD_DEPLOYMENT.md)** - ⭐ Complete cloud deployment guide
- **[QUICKSTART.md](QUICKSTART.md)** - ⚡ Quick start guide
- **[STREAMLIT_DEPLOYMENT.md](STREAMLIT_DEPLOYMENT.md)** - Legacy deployment guide
- **[SETUP.md](SETUP.md)** - Configuration details
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
- **[MODULE_CONVENOR_GUIDE.md](MODULE_CONVENOR_GUIDE.md)** - Feature guide

## 🔧 Advanced Features

### Add Course Materials

1. Place documents in `backend/corpus/` (PDF, DOCX, PPTX, TXT, HTML)
2. Run ingestion:
   ```bash
   cd backend
   python ingest.py
   ```
3. Redeploy:
   ```bash
   fly deploy
   ```

### Conversation Memory

EduMate maintains conversation context automatically:
- Tracks up to 10 conversation turns
- Detects patterns (struggling students, repeated topics)
- Privacy-preserving (in-memory only)

### Custom Prompts

Modify the Module Convenor persona in `backend/persona.py` to customize:
- Teaching style
- Response format
- Domain-specific guidance

## 🆘 Troubleshooting

### Quick Fixes

1. **Backend won't start / health check fails**
   ```bash
   fly status              # Check if machines are running
   fly logs --app your-app-name    # View recent logs
   fly secrets list        # Verify OPENROUTER_API_KEY is set
   ```

2. **"OPENROUTER_API_KEY not set" warning**
   ```bash
   fly secrets set OPENROUTER_API_KEY=your-key-here
   fly deploy              # Redeploy after setting secret
   ```

3. **Port binding errors**
   - The app uses PORT env var from Fly.io (default 8080)
   - Health check endpoint: `/health` 
   - Verify fly.toml has `internal_port = 8080`

4. **"fly.toml is not valid: check item name not a string" error**
   - Ensure all `[[checks]]` sections have a `name` field
   - Example: `name = "health"` should be added to the checks section
   - Validate TOML syntax: `python3 -c "import tomllib; tomllib.load(open('fly.toml', 'rb'))"`

5. **Streamlit can't connect to backend**
   - Verify backend URL in Streamlit: `https://your-app-name.fly.dev`
   - Check CORS is enabled (backend/main.py already has this)
   - Test backend health: `curl https://your-app-name.fly.dev/health`

6. **High costs / unexpected charges**
   ```bash
   # Set spending limit
   fly orgs billing-limits set --max-monthly-spend 5
   
   # Use free models
   fly secrets set OPENROUTER_MODEL=meta-llama/llama-3.1-8b-instruct:free
   ```

For more help, see [CLOUD_DEPLOYMENT.md](CLOUD_DEPLOYMENT.md) or check [Fly.io docs](https://fly.io/docs/).

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

[Add your license here]

## 🙏 Acknowledgments

Built with:
- [Streamlit](https://streamlit.io/) - Web UI framework
- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [OpenRouter](https://openrouter.ai/) - LLM API aggregator
- [Fly.io](https://fly.io/) - Cloud hosting

---

**Ready to deploy?** Start with the [Cloud Deployment Guide](CLOUD_DEPLOYMENT.md) 🚀
