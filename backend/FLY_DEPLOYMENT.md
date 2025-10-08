# Fly.io Deployment Guide for EduMate Backend

This guide provides step-by-step instructions for deploying the EduMate backend API on Fly.io's **free tier**.

## Prerequisites

1. **Fly.io Account**: Sign up at https://fly.io
2. **Flyctl CLI**: Install from https://fly.io/docs/hands-on/install-flyctl/

## Quick Start

```bash
# 1. Login to Fly.io
fly auth login

# 2. Set spending limit to $0 (IMPORTANT for free tier)
fly orgs billing-limits set

# 3. Deploy from the backend directory
cd backend
fly launch

# Or if you've already configured fly.toml:
fly deploy
```

## Step-by-Step Deployment

### 1. Install Flyctl

**macOS:**
```bash
brew install flyctl
```

**Linux:**
```bash
curl -L https://fly.io/install.sh | sh
```

**Windows:**
```powershell
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

### 2. Login and Configure

```bash
# Login to Fly.io
fly auth login

# Set billing limit to $0 to prevent charges
fly orgs billing-limits set
# When prompted, enter: 0
```

### 3. Deploy the Application

```bash
# Navigate to backend directory
cd backend

# Launch (first time deployment)
fly launch

# Follow the interactive prompts:
# - App name: Choose a unique name (e.g., edumate-backend-yourname)
# - Region: Select closest to your users (e.g., iad for US East)
# - Add PostgreSQL? NO
# - Add Redis? NO
# - Deploy now? YES
```

The `fly.toml` configuration is already optimized for the free tier:
- 256MB RAM
- 1 shared CPU
- Auto-stop/auto-start enabled
- No paid add-ons

### 4. Verify Deployment

```bash
# Check app status
fly status

# View logs
fly logs

# Test the health endpoint
curl https://your-app-name.fly.dev/health

# Expected response:
# {"ok": true}
```

### 5. Update Frontend Configuration

After deployment, update your Streamlit frontend to use the new API endpoint:

**Option A: Environment Variable (Recommended)**
```bash
# In your ui/ directory or deployment environment
export API_BASE=https://your-app-name.fly.dev

# Then run your Streamlit app
streamlit run app_simple.py
```

**Option B: Code Modification**
Edit the UI files directly:

```python
# In ui/app.py, ui/app_simple.py, or ui/app_public.py
API_BASE = "https://your-app-name.fly.dev"
```

## Important Notes

### ⚠️ Free Tier Limitations

1. **No Ollama**: The free tier cannot run Ollama for LLM generation. You need to:
   - Modify the backend to use cloud LLM APIs (OpenAI, Anthropic, etc.), OR
   - Use a separate Ollama instance (requires additional hosting)

2. **Ephemeral Storage**: ChromaDB data will be reset on each deployment
   - Consider using external vector database services for persistence
   - Or enable Fly.io volumes (paid feature)

3. **Cold Starts**: Auto-stop means first request after idle may be slow
   - Typical cold start: 5-15 seconds
   - Subsequent requests are fast

### 🔍 Monitoring Usage

```bash
# Check current usage and billing
fly billing show

# View dashboard
fly dashboard
# Navigate to: Billing → Usage

# Monitor logs
fly logs -f

# SSH into container for debugging
fly ssh console
```

### 💰 Cost Management

Free tier includes:
- **3 shared-cpu-1x VMs** with 256MB RAM each
- **160GB** outbound data transfer per month
- **Sufficient for**: 5-10 concurrent users, educational use

To ensure you stay on free tier:
1. ✅ Set billing limit to $0: `fly orgs billing-limits set`
2. ✅ Keep `min_machines_running = 0` in fly.toml
3. ✅ Monitor usage weekly at https://fly.io/dashboard
4. ✅ Use auto-stop/auto-start (already configured)

## Updating Your Deployment

```bash
# Make changes to your code
# Then redeploy:
fly deploy

# View deploy logs
fly logs -f
```

## Troubleshooting

### Deployment fails due to memory

```bash
# Check logs
fly logs

# If out of memory, scale up (may incur small cost)
fly scale memory 512
```

### App crashes or doesn't start

```bash
# View detailed logs
fly logs -f

# Check status
fly status

# SSH into container
fly ssh console
# Then check: ps aux, df -h, etc.
```

### Cold starts too slow

```bash
# Keep at least one machine running
# Edit fly.toml:
min_machines_running = 1

# Then redeploy:
fly deploy
```

### Health check fails

```bash
# Check if /health endpoint works locally
curl http://localhost:8000/health

# View Fly.io health check logs
fly logs --grep health

# Adjust health check settings in fly.toml if needed
```

## Advanced Configuration

### Environment Variables

```bash
# Set environment variables
fly secrets set FAST_MODE=1
fly secrets set MAX_ACTIVE_GENERATIONS=1

# List all secrets
fly secrets list

# Remove a secret
fly secrets unset SECRET_NAME
```

### Scaling

```bash
# Scale memory (may incur cost above 256MB)
fly scale memory 512

# Scale to multiple machines (may incur cost)
fly scale count 2

# Scale to zero machines when idle (recommended for free tier)
# Already configured in fly.toml
```

### Custom Domain

```bash
# Add a custom domain (requires DNS configuration)
fly certs add your-domain.com

# View certificates
fly certs list
```

## Support and Resources

- **Fly.io Docs**: https://fly.io/docs/
- **Fly.io Community**: https://community.fly.io/
- **EduMate Issues**: https://github.com/namitzz/EduMate-local/issues
- **Free Tier Limits**: https://fly.io/docs/about/pricing/

## Security Notes

For production use:
1. ✅ HTTPS is automatic with Fly.io
2. ⚠️ Add authentication (not included by default)
3. ⚠️ Configure CORS properly for your frontend domain
4. ⚠️ Set up rate limiting if needed
5. ⚠️ Use secrets for sensitive configuration

## Next Steps

After deploying the backend:
1. ✅ Update your frontend to use the new API URL
2. ✅ Test all endpoints: `/health`, `/chat`, `/chat_stream`
3. ✅ Monitor usage for the first week
4. ⚠️ Consider implementing authentication
5. ⚠️ Plan for Ollama replacement with cloud LLM API
