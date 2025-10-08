# EduMate Deployment Architecture

## 🌐 Production Deployment Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                          STUDENTS                               │
│                     (Multiple Devices)                          │
│                                                                 │
│  🖥️  Desktop    📱 Mobile    💻 Laptop    🖳 Tablet            │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      │ HTTPS
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                    STREAMLIT CLOUD                              │
│                    (Frontend - Free Tier)                       │
│                                                                 │
│  📊 Streamlit UI:  ui/app_simple.py                            │
│  🎨 Theme:         Green & White                               │
│  💾 Resources:     1 GB RAM                                     │
│  👥 Users:         Unlimited viewers                           │
│  💰 Cost:          $0/month                                     │
│                                                                 │
│  API_BASE_URL = "https://edumate-local.fly.dev/"              │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      │ REST API (HTTPS)
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                       FLY.IO                                    │
│                 (Backend API - Free Tier)                       │
│                                                                 │
│  🐳 Container:  FastAPI (main.py)                              │
│  💾 Memory:     256 MB                                          │
│  🔄 Auto-stop:  When idle (saves resources)                    │
│  🚀 Auto-start: On first request                               │
│  💰 Cost:       $0/month (free tier)                           │
│                                                                 │
│  Endpoints:                                                     │
│  • GET  /health       → Health check                           │
│  • POST /chat         → Non-streaming chat                     │
│  • POST /chat_stream  → Streaming chat                         │
│                                                                 │
│  Components:                                                    │
│  ├─ 📚 ChromaDB (Vector Database)                              │
│  │   └─ Ephemeral (resets on restart)                         │
│  ├─ 🔍 Retrieval System                                        │
│  │   └─ SentenceTransformers embeddings                       │
│  └─ ⚙️  Configuration                                           │
│      ├─ FAST_MODE = 1                                          │
│      ├─ USE_OPENAI = 1                                         │
│      └─ MAX_ACTIVE_GENERATIONS = 1                             │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      │ API Calls (HTTPS)
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                     OPENROUTER API                              │
│                   (LLM Provider - Pay-per-use)                  │
│                                                                 │
│  🤖 Model:    GPT-3.5-turbo                                     │
│  🌐 Endpoint: https://openrouter.ai/api/v1                     │
│  🔑 Auth:     Pre-configured API key                           │
│  💰 Cost:     ~$0.0015 per 1,000 tokens                        │
│              (~$3-5 per 1,000 student questions)               │
│                                                                 │
│  Features:                                                      │
│  • OpenAI-compatible API                                       │
│  • Multiple model options                                      │
│  • Low latency                                                 │
│  • Reliable uptime                                             │
└─────────────────────────────────────────────────────────────────┘
```

## 💰 Cost Breakdown

### Monthly Costs (Typical Usage)

| Service          | Free Tier Limit          | Cost if Under Limit | Typical Usage     |
|------------------|--------------------------|---------------------|-------------------|
| Streamlit Cloud  | 1 GB RAM, unlimited views| $0/month           | ✅ Under limit    |
| Fly.io           | 3 VMs @ 256MB, 160GB/mo | $0/month           | ✅ Under limit    |
| OpenRouter       | Pay-per-use only         | ~$3-5/1000 queries | Variable          |
| **TOTAL**        | -                        | **$0-5/month**     | Low-moderate use  |

### Cost Optimization Features

✅ **Fly.io Backend**
- Auto-stops when idle (no cost)
- Auto-starts on request (fast)
- Scales to zero (maximum savings)
- 256MB RAM (free tier)

✅ **Streamlit Cloud**
- Static frontend (minimal resources)
- Free tier covers typical usage
- Unlimited student viewers

✅ **OpenRouter**
- Only charged when used
- Fast model (GPT-3.5-turbo)
- Reduced token generation (FAST_MODE)

## 🚀 Deployment Flow

```
┌──────────────────────────────────────────────────────────────┐
│ STEP 1: Deploy Backend to Fly.io                            │
│                                                              │
│  cd backend                                                  │
│  fly deploy                                                  │
│                                                              │
│  Result: https://edumate-local.fly.dev                      │
│  Time: 2-3 minutes                                          │
└──────────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 2: Deploy Frontend to Streamlit Cloud                  │
│                                                              │
│  1. Go to share.streamlit.io                                │
│  2. New app → Select repository                             │
│  3. Main file: ui/app_simple.py                             │
│  4. Click Deploy                                            │
│                                                              │
│  Result: https://your-app-name.streamlit.app                │
│  Time: 2-3 minutes                                          │
└──────────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 3: Share with Students                                 │
│                                                              │
│  Share URL: https://your-app-name.streamlit.app             │
│                                                              │
│  Students can access immediately!                           │
│  ✅ No login required                                        │
│  ✅ Works on all devices                                     │
│  ✅ Instant AI answers                                       │
└──────────────────────────────────────────────────────────────┘
```

## 🔒 Security & Reliability

### Security Features
- ✅ HTTPS only (both services)
- ✅ API key in environment variables
- ✅ CORS configured
- ✅ No student data stored
- ✅ Ephemeral vector database

### Reliability Features
- ✅ Health checks (15s interval)
- ✅ Auto-restart on failure
- ✅ Fast startup (30s grace period)
- ✅ Timeout protection (10s)

## 📊 Performance

### Response Times
- **Streamlit UI Load**: < 1 second
- **Backend Cold Start**: 2-5 seconds (first request after idle)
- **Backend Warm**: < 1 second
- **LLM Generation**: 3-6 seconds (with FAST_MODE)
- **Total User Response**: 4-10 seconds

### Optimizations
- FAST_MODE enabled (faster responses)
- Smaller embeddings model
- Reduced context window
- Limited concurrent requests
- Auto-stop after idle

## 🎓 Student Experience

### Access Flow
```
Student → Opens URL → Streamlit loads → Backend starts → Chat ready
   (0s)      (1s)         (2s)             (3s)            (6s)

First message → Backend retrieves → LLM generates → Response shown
      (0s)           (1s)              (4s)             (5s)
```

### Features Available
- ✅ Natural language questions
- ✅ AI-powered answers
- ✅ Source citations
- ✅ Chat history
- ✅ Clear chat option
- ✅ API status indicator

## 📁 Repository Structure

```
EduMate-local/
├── .streamlit/                    # Streamlit Cloud config
│   ├── config.toml               # Theme & server settings
│   └── secrets.toml.example      # Secrets template
│
├── backend/                       # Fly.io backend
│   ├── fly.toml                  # Fly.io configuration
│   ├── Dockerfile                # Container image
│   ├── main.py                   # FastAPI application
│   ├── config.py                 # Configuration
│   ├── requirements.txt          # Python dependencies
│   └── ...                       # Other backend files
│
├── ui/                           # Streamlit frontend
│   ├── app_simple.py            # Main Streamlit app
│   └── requirements.txt         # UI dependencies
│
└── Documentation/
    ├── README.md                # Main documentation
    ├── QUICKSTART.md            # 5-minute guide
    ├── STREAMLIT_DEPLOYMENT.md  # Full deployment guide
    ├── DEPLOYMENT_CHECKLIST.md  # Verification checklist
    └── DEPLOYMENT_ARCHITECTURE.md # This file
```

## 🔄 Update Process

### Update Course Materials
```bash
1. Add documents to backend/corpus/
2. Run: python ingest.py
3. Deploy: fly deploy
4. Streamlit updates automatically
```

### Update UI
```bash
1. Modify ui/app_simple.py
2. Commit and push to GitHub
3. Streamlit auto-deploys from GitHub
```

### Update Backend
```bash
1. Modify backend files
2. Deploy: fly deploy
3. Backend restarts automatically
```

## 📞 Support & Monitoring

### Monitor Usage
```bash
# Fly.io usage
fly billing show

# Fly.io logs
fly logs

# Set spending limit
fly orgs billing-limits set
```

### Streamlit Cloud
- Dashboard: share.streamlit.io
- View logs in deployment panel
- Monitor app health

## ✅ Production Checklist

Before sharing with students:

- [ ] Backend deployed and healthy
- [ ] Frontend deployed and accessible
- [ ] Test chat functionality works
- [ ] API status shows online
- [ ] Spending limits set
- [ ] Documentation URL shared
- [ ] Tested on multiple devices

---

**Ready to deploy?** Start with [QUICKSTART.md](QUICKSTART.md)
