# Streamlit Cloud Deployment Guide

This guide explains how to deploy EduMate on **Streamlit Cloud** (frontend) with **Fly.io** (backend).

## 🏗️ Architecture

```
Students → Streamlit Cloud (UI) → Fly.io (Backend API) → OpenRouter (LLM)
```

- **Frontend**: Hosted on Streamlit Cloud (free tier)
- **Backend**: Hosted on Fly.io (free tier)
- **LLM**: OpenRouter API (pay-per-use, cost-effective)

Both services have generous free tiers, making this setup completely free for moderate usage.

## 📋 Prerequisites

1. **Streamlit Cloud Account**: Sign up at [share.streamlit.io](https://share.streamlit.io)
2. **Fly.io Account**: Sign up at [fly.io](https://fly.io/app/sign-up)
3. **GitHub Repository**: Fork or use this repository

## 🚀 Step-by-Step Deployment

### Step 1: Deploy Backend to Fly.io

The backend is already configured for Fly.io free tier.

1. **Install Fly.io CLI**:
   ```bash
   # macOS/Linux
   curl -L https://fly.io/install.sh | sh
   
   # Windows (PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex
   ```

2. **Login to Fly.io**:
   ```bash
   fly auth login
   ```

3. **Deploy the backend**:
   ```bash
   cd backend
   fly deploy
   ```

4. **Verify deployment**:
   ```bash
   curl https://edumate-local.fly.dev/health
   # Expected: {"ok": true}
   ```

5. **Check your Fly.io app name**:
   ```bash
   fly status
   ```
   
   Note: If your app name is different from `edumate-local`, update the API URL in `ui/app_simple.py`:
   ```python
   API_BASE_URL = "https://your-app-name.fly.dev/"
   ```

### Step 2: Deploy Frontend to Streamlit Cloud

1. **Go to Streamlit Cloud**: Visit [share.streamlit.io](https://share.streamlit.io)

2. **Sign in** with your GitHub account

3. **Click "New app"**

4. **Configure the deployment**:
   - **Repository**: Select your forked repository (e.g., `yourusername/EduMate-local`)
   - **Branch**: `main`
   - **Main file path**: `ui/app_simple.py`

5. **Click "Deploy"**

6. **Wait for deployment**: Streamlit Cloud will install dependencies and start your app (takes 2-3 minutes)

7. **Get your app URL**: You'll get a URL like `https://your-app-name.streamlit.app`

### Step 3: Share with Students

Students can now access your app at:
```
https://your-app-name.streamlit.app
```

No login or setup required - just share the link!

## 💰 Cost Breakdown

### Streamlit Cloud (Free Tier)
- ✅ **1 private app** (or unlimited public apps)
- ✅ **1 GB RAM**
- ✅ **Unlimited viewers**
- ✅ **Custom domain** (optional)
- **Cost**: $0/month

### Fly.io (Free Tier)
- ✅ **3 VMs** with 256MB RAM each
- ✅ **160GB data transfer/month**
- ✅ **Auto-stop when idle** (saves resources)
- ✅ **Auto-start on request**
- **Cost**: $0/month for typical usage

### OpenRouter API
- ✅ **Pay-per-use** (no monthly fees)
- ✅ **GPT-3.5-turbo**: ~$0.0015 per 1,000 tokens
- ✅ **Example**: 1,000 questions ≈ $3-5
- **Cost**: Only when students use it

**Total Monthly Cost**: $0 base + minimal API costs

## 🔒 Staying Within Free Tier Limits

### Fly.io Free Tier
The backend is configured to stay within free tier:
- `auto_stop_machines = true` - Stops when idle
- `auto_start_machines = true` - Starts on request
- `min_machines_running = 0` - Scales to zero
- `memory = "256mb"` - Free tier VM size

### Monitor Usage
```bash
# Check Fly.io usage
fly billing show

# Set spending limit (recommended)
fly orgs billing-limits set

# View logs
fly logs
```

### Streamlit Cloud
- Monitor at: [share.streamlit.io/settings](https://share.streamlit.io/settings)
- Free tier: 1 private app or unlimited public apps
- No action needed - automatically managed

## 🛠️ Configuration

### Backend Configuration (backend/config.py)
Already configured for production:
```python
USE_OPENAI = "1"  # Uses OpenRouter
OPENAI_API_KEY = "sk-or-v1-..."  # Pre-configured
OPENAI_MODEL = "openai/gpt-3.5-turbo"
FAST_MODE = "1"  # Optimized for speed
```

### Frontend Configuration (ui/app_simple.py)
Already configured to connect to Fly.io:
```python
API_BASE_URL = "https://edumate-local.fly.dev/"
```

### Streamlit Configuration (.streamlit/config.toml)
Already configured for Streamlit Cloud deployment.

## 📚 Adding Course Materials

1. **Add documents** to `backend/corpus/` directory
   - Supported: PDF, DOCX, PPTX, TXT, HTML

2. **Process documents**:
   ```bash
   cd backend
   python ingest.py
   ```

3. **Redeploy backend**:
   ```bash
   fly deploy
   ```

4. **Frontend updates automatically** - no redeployment needed

## ✅ Verification Checklist

- [ ] Backend deployed to Fly.io
- [ ] Backend health check passes: `curl https://edumate-local.fly.dev/health`
- [ ] Frontend deployed to Streamlit Cloud
- [ ] Students can access the Streamlit URL
- [ ] Chat functionality works end-to-end
- [ ] Spending limits set on Fly.io: `fly orgs billing-limits set`

## 🆘 Troubleshooting

### Backend not responding
```bash
# Check status
fly status

# View logs
fly logs

# Restart app
fly apps restart edumate-local
```

### Frontend shows API offline
1. Check if backend is running: `curl https://edumate-local.fly.dev/health`
2. Verify API URL in `ui/app_simple.py` matches your Fly.io app name
3. Check Fly.io logs for errors: `fly logs`

### Streamlit Cloud deployment fails
1. Check `ui/requirements.txt` has all dependencies
2. Verify `ui/app_simple.py` exists
3. Check Streamlit Cloud logs in the deployment panel

### Costs increasing
1. Set Fly.io spending limit: `fly orgs billing-limits set`
2. Check usage: `fly billing show`
3. Ensure auto-stop is enabled in `fly.toml`

## 📖 Additional Resources

- [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-community-cloud)
- [Fly.io Documentation](https://fly.io/docs/)
- [OpenRouter Documentation](https://openrouter.ai/docs)

## 🎓 Student Access

Share this URL with your students:
```
https://your-app-name.streamlit.app
```

They can:
- ✅ Access instantly (no login required)
- ✅ Ask questions about course materials
- ✅ Get instant AI-powered answers
- ✅ View source citations
- ✅ Use from any device (desktop, tablet, mobile)

## 🔄 Updating the App

### Update Course Materials
```bash
cd backend
python ingest.py
fly deploy
```

### Update UI
```bash
# Commit changes to GitHub
git add ui/app_simple.py
git commit -m "Update UI"
git push

# Streamlit Cloud auto-deploys from GitHub
```

### Update Backend Code
```bash
cd backend
# Make changes
git add .
git commit -m "Update backend"
git push
fly deploy
```

