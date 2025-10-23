# 🚀 Cloud Deployment Guide - Zero Cost Setup

This guide walks you through deploying EduMate to the cloud with **$0 base cost** using free tiers.

## Architecture Overview

```
Students → Streamlit Cloud (Free) → Fly.io Backend (Free) → OpenRouter API (Pay-per-use)
```

All components use generous free tiers, making this setup completely free for moderate usage.

## Prerequisites

1. **GitHub Account** - For code hosting
2. **Streamlit Cloud Account** - Sign up at [share.streamlit.io](https://share.streamlit.io)
3. **Fly.io Account** - Sign up at [fly.io](https://fly.io/app/sign-up)
4. **OpenRouter API Key** - Get free credits at [openrouter.ai](https://openrouter.ai/)

## Step 1: Get OpenRouter API Key

1. Go to [openrouter.ai](https://openrouter.ai/)
2. Sign up for a free account (get $1-5 in free credits)
3. Navigate to **Keys** section
4. Click **Create Key**
5. Copy your API key (format: `sk-or-v1-...`)

💡 **Cost**: Free credits available, then ~$0.0015 per 1,000 tokens for GPT-3.5-turbo

## Step 2: Deploy Backend to Fly.io

### 2.1 Install Fly.io CLI

```bash
# macOS/Linux
curl -L https://fly.io/install.sh | sh

# Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex
```

### 2.2 Login to Fly.io

```bash
fly auth login
```

### 2.3 Deploy Backend

```bash
# Navigate to backend directory
cd backend

# Launch the app (first time only)
fly launch --copy-config --yes

# Set your OpenRouter API key as a secret
fly secrets set OPENROUTER_API_KEY=sk-or-v1-your-api-key-here

# Deploy the app
fly deploy
```

### 2.4 Verify Backend

```bash
# Check status
fly status

# Check logs
fly logs

# Test health endpoint
curl https://your-app-name.fly.dev/health
```

✅ Your backend should now be running at `https://your-app-name.fly.dev`

## Step 3: Deploy Frontend to Streamlit Cloud

### 3.1 Deploy to Streamlit Cloud

1. Fork this repository to your GitHub account (if you haven't already)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **"New app"**
4. Configure:
   - **Repository**: `yourusername/EduMate-local`
   - **Branch**: `main`
   - **Main file path**: `ui/app_simple.py`
5. **Advanced settings** → **Environment variables** (if your app name differs from "edumate-local"):
   - Add: `EDUMATE_API_BASE` = `https://your-app-name.fly.dev`
6. Click **"Deploy"**

Wait 2-3 minutes for deployment to complete.

✅ Your app will be available at `https://your-app-name.streamlit.app`

## Step 4: Test the Complete Setup

1. Open your Streamlit app URL
2. Check the sidebar for "System Status"
3. Should show: ✅ Backend API: Online
4. Try asking: "What can you help me with?"
5. Verify you get a response

## Step 5: Add Your Course Materials

### 5.1 Add Documents

Place your course materials in `backend/corpus/` directory:
- PDFs, DOCX, PPTX, TXT, HTML supported
- Organize in subdirectories if needed

### 5.2 Build Vector Index

```bash
cd backend
python ingest.py
```

### 5.3 Redeploy Backend

```bash
fly deploy
```

## 💰 Cost Management

### Free Tier Limits

**Streamlit Cloud**
- ✅ 1 private app or unlimited public apps
- ✅ 1 GB RAM per app
- ✅ Unlimited viewers
- **Cost**: $0/month

**Fly.io**
- ✅ 3 VMs with 256MB RAM (shared-cpu-1x)
- ✅ 160GB outbound data transfer/month
- ✅ Auto-stop/start (configured)
- **Cost**: $0/month for typical usage

**OpenRouter API**
- ✅ Pay-per-use only (no subscription)
- ✅ GPT-3.5-turbo: ~$0.0015 per 1,000 tokens
- ✅ Free models available (with rate limits)
- **Example**: 1,000 questions ≈ $3-5

### Set Spending Limits

```bash
# Fly.io spending cap
fly orgs billing-limits set --max-monthly-spend 5

# Monitor usage
fly billing show
```

### Use Free Models (Optional)

Update `backend/fly.toml`:
```toml
[env]
  OPENROUTER_MODEL = "meta-llama/llama-3.1-8b-instruct:free"
  # or
  OPENROUTER_MODEL = "mistralai/mistral-7b-instruct:free"
```

⚠️ **Note**: Free models have rate limits and may be slower.

## 🔧 Configuration

### Environment Variables

All configuration is in `backend/fly.toml`:

```toml
[env]
  # Performance
  FAST_MODE = "1"                      # Faster responses
  MAX_ACTIVE_GENERATIONS = "1"         # Prevent rate limiting
  TEMP = "0.3"                         # Response creativity
  NUM_PREDICT = "400"                  # Max response length
  
  # Conversation Memory
  ENABLE_CONVERSATION_MEMORY = "1"     # Context-aware
  MAX_CONVERSATION_HISTORY = "10"      # Conversation turns
  
  # OpenRouter
  OPENROUTER_MODEL = "openai/gpt-3.5-turbo"
  OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
```

### Update Configuration

```bash
# Method 1: Edit fly.toml and redeploy
vim fly.toml
fly deploy

# Method 2: Set environment variables directly
fly secrets set OPENROUTER_MODEL=openai/gpt-4-turbo
```

## 🔍 Monitoring & Troubleshooting

### Check Backend Status

```bash
# View logs
fly logs

# Check machine status
fly status

# SSH into machine
fly ssh console

# Restart app
fly apps restart edumate-local
```

### Common Issues

#### Backend not responding
```bash
# Check status
fly status

# View logs for errors
fly logs

# Restart if needed
fly apps restart edumate-local
```

#### "Backend API: Offline" in UI
1. Check Fly.io status: `fly status`
2. Verify API URL in sidebar matches your Fly.io app
3. Test health endpoint: `curl https://your-app.fly.dev/health`
4. Check Fly.io logs: `fly logs`

#### "OPENROUTER_API_KEY is required" error
```bash
# Set the secret
fly secrets set OPENROUTER_API_KEY=sk-or-v1-your-api-key-here

# Verify it's set
fly secrets list
```

#### High API costs
1. Check usage: Monitor OpenRouter dashboard
2. Switch to free model (see "Use Free Models" above)
3. Set rate limits in your code
4. Reduce MAX_CONVERSATION_HISTORY

### View Logs

```bash
# Fly.io backend logs
fly logs --app edumate-local

# Streamlit Cloud logs
# Available in Streamlit Cloud dashboard under "Logs"
```

## 🔄 Updating Your Deployment

### Update Backend

```bash
cd backend
git pull
fly deploy
```

### Update Frontend

Streamlit Cloud auto-deploys when you push to GitHub:
```bash
cd ui
git add app_simple.py
git commit -m "Update UI"
git push
```

Wait 1-2 minutes for auto-deployment.

## 📊 Scaling Considerations

### If you need more capacity:

**Increase Fly.io Resources**
```bash
# Upgrade machine (leaves free tier)
fly scale vm shared-cpu-2x --memory 512
```

**Add More Machines**
```bash
# Add more instances (leaves free tier)
fly scale count 2
```

**Optimize Performance**
- Enable caching for repeated queries
- Reduce chunk size for faster retrieval
- Use smaller embedding model
- Switch to faster LLM model

## 🎓 Sharing with Students

### Public Access
1. Share Streamlit URL: `https://your-app.streamlit.app`
2. No login required
3. Each student gets their own session
4. Privacy-first design (sessions not persisted)

### Custom Domain (Optional)
- Streamlit Cloud: Upgrade to paid plan
- Or use Cloudflare Pages for custom domain

## 📚 Additional Resources

- **Streamlit Docs**: https://docs.streamlit.io/
- **Fly.io Docs**: https://fly.io/docs/
- **OpenRouter Docs**: https://openrouter.ai/docs
- **Project README**: [README.md](README.md)

## 🆘 Getting Help

1. Check logs first: `fly logs`
2. Review this guide's troubleshooting section
3. Search GitHub issues
4. Open a new issue with:
   - Error message
   - Logs (sanitized)
   - Steps to reproduce

---

**Next Steps**: [Share with students](README.md#sharing-with-students) | [Add more documents](#step-5-add-your-course-materials)
