# EduMate Deployment Guide

This guide explains how to deploy EduMate locally or on a server for production use.

## Quick Deploy with Docker (Recommended)

### Prerequisites
- Docker and Docker Compose installed
- At least 4GB RAM
- 10GB free disk space

### Steps

1. **Clone the repository**
```bash
git clone https://github.com/namitzz/EduMate-local.git
cd EduMate-local
```

2. **Add your course materials**
Place your documents (PDF, DOCX, PPTX, TXT, HTML) in the `corpus/` directory.

3. **Configure environment (optional)**
Create a `.env` file in the root directory:
```bash
# Optional: Use a smaller/faster model
OLLAMA_MODEL=mistral

# Fast Mode (enabled by default for 4-6s responses)
FAST_MODE=1

# Token limit (reduced for faster responses)
NUM_PREDICT=400

# Temperature (lower = more focused)
TEMP=0.3
```

4. **Start the application**
```bash
docker compose up --build
```

First run takes 5-10 minutes to download models and build the index.

5. **Access the application**
- Public UI: http://localhost:8501
- API: http://localhost:8000
- API Health: http://localhost:8000/health

### Using a Faster Model

For 4-6 second response times, use a smaller model:
```bash
# Edit docker-compose.yml, change OLLAMA_MODEL to:
OLLAMA_MODEL: qwen2.5:1.5b-instruct

# Or set in .env:
echo "OLLAMA_MODEL=qwen2.5:1.5b-instruct" >> .env
```

## Standalone Backend Deployment

For cloud platforms that auto-detect Dockerfiles (Railway, Render, etc.), use the root-level Dockerfile:

### Using the Root Dockerfile

The root Dockerfile builds the backend API only and is designed for platforms that expect a Dockerfile in the repository root.

```bash
# Build the backend image
docker build -t edumate-backend .

# Run with an external Ollama instance
docker run -p 8000:8000 \
  -e OLLAMA_HOST=http://your-ollama-host:11434 \
  -e OLLAMA_MODEL=mistral \
  edumate-backend
```

**Note:** This deployment method requires:
- An external Ollama instance, OR use OpenRouter (see Cloud LLM Provider section below)
- Corpus files are built into the image (update and rebuild for changes)
- No UI included (deploy UI separately or use the API directly)

**For full-stack deployment**, use `docker compose up --build` instead.

## Cloud LLM Provider (OpenRouter)

For production cloud deployments (Fly.io, Railway, Streamlit Cloud, etc.), you can use **OpenRouter** instead of running Ollama. OpenRouter provides access to various LLMs through an OpenAI-compatible API.

### Why OpenRouter for Cloud?
- ✅ No need to manage Ollama infrastructure
- ✅ Access to multiple models (GPT-3.5, GPT-4, Claude, etc.)
- ✅ Pay-per-use pricing
- ✅ Better reliability for production
- ✅ Easier scaling

### Setup Instructions

1. **Get an OpenRouter API Key**
   - Sign up at https://openrouter.ai
   - Get your API key from https://openrouter.ai/keys

2. **Configure Environment Variables**
   ```bash
   # Enable OpenRouter
   export USE_OPENAI=1
   
   # Set your API key
   export OPENAI_API_KEY=sk-or-v1-your-api-key-here
   
   # Optional: Choose a specific model (default: openai/gpt-3.5-turbo)
   export OPENAI_MODEL=openai/gpt-3.5-turbo
   
   # Keep Fast Mode enabled for better performance
   export FAST_MODE=1
   export NUM_PREDICT=400
   export TEMP=0.3
   ```

3. **Available Models**
   OpenRouter supports many models. Popular options:
   - `openai/gpt-3.5-turbo` - Fast, cost-effective (default)
   - `openai/gpt-4` - Higher quality, more expensive
   - `anthropic/claude-3-haiku` - Fast Claude model
   - `anthropic/claude-3-sonnet` - Balanced Claude model
   - See full list: https://openrouter.ai/models

4. **Deploy with Docker**
   ```bash
   docker build -t edumate-backend .
   
   docker run -p 8000:8000 \
     -e USE_OPENAI=1 \
     -e OPENAI_API_KEY=sk-or-v1-your-api-key-here \
     -e OPENAI_MODEL=openai/gpt-3.5-turbo \
     -e FAST_MODE=1 \
     edumate-backend
   ```

5. **Cost Considerations**
   - Monitor usage at https://openrouter.ai/activity
   - Set spending limits in your OpenRouter account
   - Start with gpt-3.5-turbo for cost efficiency
   - Fast Mode (NUM_PREDICT=400) keeps responses short and costs low

### Example: Fly.io Deployment with OpenRouter

1. **Create `fly.toml`** (if not exists):
   ```toml
   app = "edumate-backend"
   primary_region = "iad"
   
   [build]
     dockerfile = "Dockerfile"
   
   [env]
     USE_OPENAI = "1"
     FAST_MODE = "1"
     NUM_PREDICT = "400"
     TEMP = "0.3"
     OPENAI_MODEL = "openai/gpt-3.5-turbo"
   
   [[services]]
     internal_port = 8000
     protocol = "tcp"
   
     [[services.ports]]
       port = 80
       handlers = ["http"]
     
     [[services.ports]]
       port = 443
       handlers = ["tls", "http"]
   ```

2. **Set secrets**:
   ```bash
   flyctl secrets set OPENAI_API_KEY=sk-or-v1-your-api-key-here
   ```

3. **Deploy**:
   ```bash
   flyctl launch
   flyctl deploy
   ```

### Switching Between Ollama and OpenRouter

You can easily switch between local Ollama (development) and OpenRouter (production):

**Local Development (Ollama):**
```bash
export USE_OPENAI=0  # or unset
export OLLAMA_HOST=http://localhost:11434
export OLLAMA_MODEL=mistral
```

**Production (OpenRouter):**
```bash
export USE_OPENAI=1
export OPENAI_API_KEY=sk-or-v1-your-api-key-here
export OPENAI_MODEL=openai/gpt-3.5-turbo
```

The same codebase works with both providers without any changes!

## Deploy on a Server (LAN/Cloud)

### LAN Deployment (for students on same network)

1. **Find your server IP**
```bash
# On Linux/Mac
ip addr show | grep inet

# On Windows
ipconfig
```

2. **Update docker-compose.yml for LAN access**
Change the ports section to bind to all interfaces:
```yaml
ports:
  - "0.0.0.0:8501:8501"  # UI
  - "0.0.0.0:8000:8000"  # API
```

3. **Configure firewall**
```bash
# On Linux (Ubuntu/Debian)
sudo ufw allow 8501
sudo ufw allow 8000

# On Windows, add inbound rules for ports 8501 and 8000
```

4. **Students can access via**
- http://YOUR_SERVER_IP:8501

### Cloud Deployment (DigitalOcean, AWS, etc.)

#### Option 1: Simple VM Deployment

1. **Create a VM with**
   - 4GB+ RAM
   - Ubuntu 22.04 or later
   - Docker installed

2. **Clone and run**
```bash
git clone https://github.com/namitzz/EduMate-local.git
cd EduMate-local
docker compose up -d
```

3. **Configure reverse proxy (optional)**
Use nginx or caddy for HTTPS:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

#### Option 2: GitHub Actions (CI/CD)

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy EduMate

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd EduMate-local
            git pull
            docker compose down
            docker compose up -d --build
```

Add secrets in GitHub: Settings → Secrets → Actions

## Configuring Ollama Connection for Different Deployments

EduMate needs to connect to an Ollama instance for LLM generation. The configuration differs based on where you're deploying:

### Local Development

For local development, Ollama runs on your machine:

```bash
# In .env file
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=mistral
```

**Verify it works:**
```bash
# Check Ollama is running
ollama list

# Test the connection
curl http://localhost:11434/api/tags
```

### Docker Deployment

For Docker Compose deployment, Ollama runs in a separate container:

```yaml
# docker-compose.yml (already configured)
services:
  api:
    environment:
      OLLAMA_HOST: http://ollama:11434  # Container-to-container networking
```

The `ollama` hostname automatically resolves to the Ollama container.

### Cloud Deployment with Public/Shared Ollama API

⚠️ **IMPORTANT**: For cloud deployments (Fly.io, Streamlit Cloud, Railway, etc.), you MUST set OLLAMA_HOST to a public endpoint - **localhost will NOT work**.

**Option 1: Use a public Ollama API service**
```bash
# Set environment variable to your public Ollama endpoint
export OLLAMA_HOST=https://api.ollama.ai
# OR
export OLLAMA_URL=https://your-ollama-provider.com

# For Fly.io:
fly secrets set OLLAMA_HOST=https://your-ollama-api.com

# For Streamlit Cloud:
# Add to your app's secrets in the Streamlit dashboard
```

**Option 2: Host Ollama separately and expose it publicly**
```bash
# Deploy Ollama on a separate server/instance
# Then set OLLAMA_HOST to the public URL
export OLLAMA_HOST=https://your-ollama-instance.com:11434
```

**Common Cloud Configuration Mistakes:**
- ❌ `OLLAMA_HOST=http://localhost:11434` - Will NOT work in cloud (localhost refers to the app container)
- ❌ `OLLAMA_HOST=http://ollama:11434` - Will NOT work in cloud (no container networking)
- ✅ `OLLAMA_HOST=https://your-public-endpoint.com` - Correct for cloud deployments
- ✅ `OLLAMA_HOST=https://api.ollama.ai` - Example of a public Ollama API

**Troubleshooting Cloud Connections:**
1. Check the logs for "Attempting to connect to Ollama at: [URL]"
2. Verify the URL is accessible from your cloud environment
3. Test the endpoint: `curl https://your-ollama-api.com/api/tags`
4. Check if authentication/API keys are required
5. Ensure HTTPS is used if required by the provider

## Deploy on Fly.io (Free Tier)

Fly.io offers a generous free tier perfect for hosting the EduMate backend API at no cost.

### Prerequisites

1. **Install Fly.io CLI**
   ```bash
   # macOS
   brew install flyctl
   
   # Linux
   curl -L https://fly.io/install.sh | sh
   
   # Windows
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
   ```

2. **Sign up and login**
   ```bash
   fly auth signup  # Create account
   # OR
   fly auth login   # If you have an account
   ```

3. **Set spending limits (IMPORTANT)**
   ```bash
   fly orgs billing-limits set
   # Set to $0 to ensure you're never charged
   ```

### Deployment Steps

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Deploy to Fly.io**
   ```bash
   fly launch
   # Follow the prompts:
   # - Choose app name (e.g., edumate-backend-yourname)
   # - Select region closest to your users
   # - Do NOT add a PostgreSQL database (select No)
   # - Do NOT add Redis (select No)
   # - Deploy now? Yes
   ```

   Alternatively, use the existing fly.toml:
   ```bash
   # Edit app name in fly.toml if needed
   fly deploy
   ```

3. **Verify deployment**
   ```bash
   fly status
   fly logs
   
   # Check health endpoint
   curl https://edumate-local.fly.dev/health
   ```

### Important Notes for Free Tier

⚠️ **Limitations to be aware of:**

1. **No Ollama**: Fly.io's free tier cannot run Ollama alongside the API. You have two options:
   - **Option A**: Modify the backend to use cloud LLM APIs (OpenAI, Anthropic, etc.)
   - **Option B**: Use a separate Ollama instance and connect via network (requires paid hosting)
   
   **To use a public/shared Ollama API:**
   ```bash
   # Set the OLLAMA_HOST to your public Ollama API endpoint
   fly secrets set OLLAMA_HOST=https://your-ollama-api.com
   # OR
   fly secrets set OLLAMA_URL=https://your-ollama-api.com
   
   # Important: Use the actual public endpoint URL, NOT localhost
   # Examples:
   # - https://api.ollama.ai (if using Ollama cloud service)
   # - https://your-ollama-instance.fly.dev (if hosting Ollama separately)
   ```

2. **Ephemeral Storage**: The ChromaDB vector database will be reset on each deployment. For persistent storage:
   - Use Fly.io volumes (paid feature)
   - Or use an external vector database service

3. **Auto-scaling**: The free tier config includes:
   - Auto-stop when idle (saves resources)
   - Auto-start on requests (may have cold start delay)
   - Single machine (no redundancy)

### Update Frontend Configuration

After deploying, update your Streamlit frontend to use the new API endpoint:

```bash
# In ui/ directory
export API_BASE=https://edumate-local.fly.dev

# Or modify the code directly in app.py / app_simple.py / app_public.py:
API_BASE = "https://edumate-local.fly.dev"
```

### Monitoring Usage

```bash
# Check current usage
fly billing show

# View spending
fly dashboard
# Navigate to: Billing → Usage

# Check logs
fly logs

# SSH into container (debugging)
fly ssh console
```

### Cost Management

To ensure you stay on the free tier:

1. **Set billing limits**: `fly orgs billing-limits set` → Set to $0
2. **Monitor usage**: Check dashboard weekly at https://fly.io/dashboard
3. **Use auto-stop**: Already configured in fly.toml
4. **Limit scale**: Keep min_machines_running = 0

Free tier includes:
- 3 shared-cpu-1x VMs (256MB RAM each)
- 160GB outbound transfer/month
- Enough for small-scale educational use (5-10 concurrent users)

### Troubleshooting Fly.io

**Issue: Deployment fails due to memory**
```bash
# The backend with all dependencies may exceed 256MB
# Solution: Optimize dependencies or upgrade to 512MB (may incur small cost)
fly scale memory 512
```

**Issue: App crashes or restarts**
```bash
# Check logs
fly logs
# Common issues: Out of memory, missing environment variables
```

**Issue: Cold starts are slow**
```bash
# Keep at least one machine running (uses free tier allocation)
# Edit fly.toml:
min_machines_running = 1
```

## Performance Optimization

### For 4-6 Second Response Times

The default configuration is optimized for 4-6 second responses:

1. **Fast Mode enabled** - Fewer chunks, smaller context
2. **MAX_TOKENS=400** - Shorter responses
3. **TOP_K=3** - Retrieve fewer documents
4. **Smaller model** - qwen2.5:1.5b-instruct or mistral

### If responses are still slow

1. **Check CPU usage**
```bash
docker stats
```

2. **Reduce context further**
Edit `backend/config.py`:
```python
MAX_CONTEXT_CHARS = 4000  # Down from 6000
TOP_K = 2  # Down from 3
```

3. **Use an even smaller model**
```bash
ollama pull tinyllama
# Update docker-compose.yml: OLLAMA_MODEL: tinyllama
```

## Updating Course Materials

1. **Add/modify files in `corpus/` directory**

2. **Rebuild the index**
```bash
docker compose down
docker compose up --build
```

Or manually:
```bash
docker exec edumate-local-api-1 python /app/ingest.py
```

## Monitoring and Logs

### View logs
```bash
# All services
docker compose logs -f

# Just the API
docker compose logs -f api

# Just the UI
docker compose logs -f ui
```

### Check response times
Logs include performance metrics:
```
[Performance] First token received in 2.34s
[Performance] Total response time: 5.67s
```

## Troubleshooting

### Issue: Responses take longer than 6 seconds

**Solution:**
1. Enable Fast Mode: `FAST_MODE=1` in .env
2. Use smaller model: `OLLAMA_MODEL=qwen2.5:1.5b-instruct`
3. Reduce MAX_TOKENS to 300-400
4. Check CPU/RAM availability

### Issue: Out of memory

**Solution:**
1. Reduce CHUNK_SIZE in config.py
2. Lower TOP_K value
3. Use smaller embedding model
4. Increase server RAM

### Issue: Can't connect from other devices

**Solution:**
1. Check firewall settings
2. Bind to 0.0.0.0 in docker-compose.yml
3. Verify network connectivity
4. Check if ports 8000 and 8501 are open

### Issue: Model download fails

**Solution:**
```bash
# Manually pull model
docker exec edumate-ollama ollama pull mistral

# Or use a smaller model
docker exec edumate-ollama ollama pull tinyllama
```

## Security Considerations

For production deployment:

1. **Use HTTPS** - Configure reverse proxy with SSL
2. **Add authentication** - Use nginx basic auth or OAuth
3. **Rate limiting** - Prevent abuse
4. **Update regularly** - Keep dependencies updated
5. **Firewall** - Only expose necessary ports
6. **Backup** - Regular backups of chroma_db directory

## Support

For issues:
1. Check logs: `docker compose logs -f`
2. Verify health: http://localhost:8000/health
3. Review this guide
4. Check GitHub Issues: https://github.com/namitzz/EduMate-local/issues
