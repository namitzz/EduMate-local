# 🚀 Complete Deployment Guide for Fly.io

This guide provides step-by-step instructions to deploy EduMate to Fly.io.

## Prerequisites

- [ ] GitHub account
- [ ] Fly.io account ([sign up](https://fly.io/app/sign-up))
- [ ] OpenRouter API key ([get free credits](https://openrouter.ai/))
- [ ] Fly.io CLI installed

## Step 1: Install Fly.io CLI

### macOS/Linux
```bash
curl -L https://fly.io/install.sh | sh
```

### Windows (PowerShell)
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

### Verify Installation
```bash
fly version
```

## Step 2: Login to Fly.io

```bash
fly auth login
```

This will open a browser window to authenticate.

## Step 3: Deploy Backend

### Option A: Deploy from Repository Root (Recommended)

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/yourusername/EduMate-local.git
cd EduMate-local

# Launch the app (first time only)
fly launch --copy-config --yes

# When prompted:
# - App name: Choose a unique name (e.g., edumate-myuniversity)
# - Region: Choose closest to your users (e.g., lhr for London)
# - PostgreSQL database: No
# - Redis database: No

# Set your OpenRouter API key
fly secrets set OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Deploy the application
fly deploy

# Verify deployment
fly status
fly logs
```

### Option B: Deploy from Backend Directory

```bash
cd backend

# Launch the app
fly launch --copy-config --yes

# Set your OpenRouter API key
fly secrets set OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Deploy
fly deploy
```

## Step 4: Verify Backend

### Check Health Endpoint
```bash
curl https://your-app-name.fly.dev/health
```

Expected response:
```json
{"status": "healthy"}
```

### Check Logs
```bash
fly logs
```

Look for:
- ✅ Application started
- ✅ Uvicorn running
- ⚠️ "OPENROUTER_API_KEY not set" warning is OK if you haven't set it yet

### Test API
```bash
# Check if backend is responding
curl https://your-app-name.fly.dev/
```

## Step 5: Deploy Frontend to Streamlit Cloud

1. **Fork the Repository**
   - Go to https://github.com/namitzz/EduMate-local
   - Click "Fork" button

2. **Deploy to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your forked repository
   - Set:
     - **Branch**: `main`
     - **Main file path**: `ui/app_simple.py`

3. **Configure Backend URL (if needed)**
   - Click "Advanced settings"
   - Add environment variable:
     - Name: `EDUMATE_API_BASE`
     - Value: `https://your-app-name.fly.dev`
   - Note: Only needed if your app name is different from "edumate-local"

4. **Deploy**
   - Click "Deploy!"
   - Wait for deployment to complete (2-3 minutes)

## Step 6: Add Course Documents (Optional)

If you want to use RAG with your course materials:

1. **Prepare Documents**
   - Place PDF, DOCX, PPTX, TXT files in `backend/corpus/` directory

2. **Run Ingestion** (locally)
   ```bash
   cd backend
   pip install -r requirements.txt
   export OPENROUTER_API_KEY=your-key-here
   python ingest.py
   ```

3. **Redeploy**
   ```bash
   fly deploy
   ```

The chroma_db directory will be included in the deployment.

## Step 7: Test Complete Setup

1. **Access Frontend**: `https://your-app-name.streamlit.app`
2. **Test Question**: "What is this course about?"
3. **Verify Response**: Should get an AI-generated response

## Common Issues & Solutions

### Backend won't start
```bash
fly logs                    # Check logs
fly status                  # Check machine status
fly secrets list            # Verify API key is set
```

### "Connection refused" from frontend
- Verify backend URL is correct
- Check backend is running: `fly status`
- Test health endpoint: `curl https://your-app-name.fly.dev/health`

### "OPENROUTER_API_KEY not set" warning
```bash
fly secrets set OPENROUTER_API_KEY=sk-or-v1-your-key-here
fly deploy
```

### Port binding errors
- The app automatically uses PORT env var from Fly.io (8080)
- Don't override PORT in fly.toml unless you have a specific reason

### High costs
```bash
# Set spending limit
fly orgs billing-limits set --max-monthly-spend 5

# Use free model
fly secrets set OPENROUTER_MODEL=meta-llama/llama-3.1-8b-instruct:free
```

## Monitoring & Maintenance

### View Logs
```bash
fly logs                    # Recent logs
fly logs -f                 # Follow logs (live)
```

### Check Status
```bash
fly status                  # Machine status
fly info                    # App info
```

### Update Application
```bash
git pull                    # Get latest changes
fly deploy                  # Redeploy
```

### Scale Resources (if needed)
```bash
# Check current machine size
fly scale show

# Upgrade to larger machine (if needed)
fly scale vm shared-cpu-2x  # 2x CPU, 512MB RAM
```

### Set Spending Limits
```bash
fly orgs billing-limits set --max-monthly-spend 5
```

## Cost Optimization

1. **Use Free Tier**
   - Fly.io: 3 shared-cpu-1x VMs (256MB RAM) - FREE
   - OpenRouter: Use free models or set spending limits

2. **Auto-Sleep Configuration** (already in fly.toml)
   - `auto_stop_machines = true` - Sleep when idle
   - `auto_start_machines = true` - Wake on request
   - `min_machines_running = 0` - Scale to zero

3. **Monitor Usage**
   ```bash
   fly billing show
   ```

## Support

- **Fly.io Issues**: https://community.fly.io/
- **OpenRouter Issues**: https://openrouter.ai/docs
- **App Issues**: Check logs with `fly logs`

## Next Steps

- [ ] Add course materials to `backend/corpus/`
- [ ] Customize Module Convenor persona in `backend/persona.py`
- [ ] Share with students
- [ ] Monitor usage and costs

---

**Need help?** Check the [troubleshooting section in README.md](README.md#-troubleshooting)
