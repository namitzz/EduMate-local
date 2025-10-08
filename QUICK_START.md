# EduMate Quick Start Guide

## TL;DR - Get Started in 5 Minutes

### Prerequisites
- Docker & Docker Compose installed
- 4GB+ RAM available

### Run the Application

```bash
# Clone the repository
git clone https://github.com/namitzz/EduMate-local.git
cd EduMate-local

# Start everything (first run takes 5-10 min)
docker compose up --build

# Access the app
# UI: http://localhost:8501
# API: http://localhost:8000
```

That's it! 🚀

## What You Get

### ⚡ Fast Responses (4-6 seconds)
- Fast Mode enabled by default
- Optimized for speed and quality

### 🎯 Smart Greeting Detection
Try these:
```
"hi"
"hello there"
"good morning"
"what's up"
"thanks"
```

### 🔍 Synonym & Fuzzy Matching
The system understands:
- "learn" = "study" = "understand"
- "exam" = "test" = "assessment"
- "help" = "assist" = "support"

### 💫 Clean UI
- Smooth animations
- Loading indicators
- Performance metrics
- Stream responses

## Configuration

### For Even Faster Responses (3-4s)
Create `.env` file:
```bash
FAST_MODE=1
MAX_TOKENS=300
OLLAMA_MODEL=qwen2.5:1.5b-instruct
```

### For Better Quality (6-8s)
```bash
FAST_MODE=0
MAX_TOKENS=600
OLLAMA_MODEL=mistral
```

## Add Your Documents

1. Place your files in `corpus/` directory:
   - PDFs, DOCX, PPTX, TXT, HTML supported

2. Rebuild to index:
```bash
docker compose down
docker compose up --build
```

## LAN Access (for students)

1. Find your IP:
```bash
# Linux/Mac
hostname -I

# Windows
ipconfig
```

2. Share with students:
```
http://YOUR_IP:8501
```

## Troubleshooting

### Slow Responses?
```bash
# Check if Fast Mode is enabled
cd backend
python -c "import config; print(f'FAST_MODE={config.FAST_MODE}')"

# Should show: FAST_MODE=True
```

### Out of Memory?
```bash
# Use smaller model
export OLLAMA_MODEL=qwen2.5:1.5b-instruct
docker compose restart
```

### View Logs
```bash
docker compose logs -f
```

## Performance Expectations

| Query Type | Response Time | Example |
|------------|---------------|---------|
| Greeting | < 1 second | "hi", "hello" |
| Simple | 2-4 seconds | "what is machine learning?" |
| Complex | 4-6 seconds | "explain neural networks in detail" |

## Learn More

- 📖 Full documentation: [README.md](README.md)
- 🚀 Deployment guide: [DEPLOYMENT.md](DEPLOYMENT.md)
- 📊 Improvements details: [IMPROVEMENTS.md](IMPROVEMENTS.md)

## Need Help?

1. Check [DEPLOYMENT.md](DEPLOYMENT.md) troubleshooting section
2. Review logs: `docker compose logs -f`
3. Open an issue on GitHub

---

**Enjoy your fast, smart study assistant!** 🎓✨
