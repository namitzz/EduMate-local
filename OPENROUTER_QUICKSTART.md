# OpenRouter Quick Start Guide

## What is OpenRouter?

OpenRouter is a unified API that provides access to multiple LLM providers (OpenAI, Anthropic, Google, etc.) through an OpenAI-compatible interface. Perfect for production deployments where you don't want to manage Ollama infrastructure.

## Quick Setup (5 minutes)

### 1. Get an API Key
1. Go to https://openrouter.ai
2. Sign up (free tier available)
3. Get your API key from https://openrouter.ai/keys

### 2. Configure Environment Variables

**Local Testing:**
```bash
export USE_OPENAI=1
export OPENAI_API_KEY=sk-or-v1-your-api-key-here
export OPENAI_MODEL=openai/gpt-3.5-turbo
```

**Docker:**
```bash
docker run -p 8000:8000 \
  -e USE_OPENAI=1 \
  -e OPENAI_API_KEY=sk-or-v1-your-api-key-here \
  -e OPENAI_MODEL=openai/gpt-3.5-turbo \
  edumate-backend
```

**Fly.io:**
```bash
# Set secret
flyctl secrets set OPENAI_API_KEY=sk-or-v1-your-api-key-here

# In fly.toml
[env]
  USE_OPENAI = "1"
  OPENAI_MODEL = "openai/gpt-3.5-turbo"
```

### 3. Start the Backend
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 4. Test It
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello!"}]}'
```

## Model Selection

Choose based on your needs:

### Cost-Effective (Recommended)
```bash
OPENAI_MODEL=openai/gpt-3.5-turbo
```
- **Cost**: ~$0.50-2 per 1M tokens
- **Speed**: Very fast
- **Quality**: Good for most use cases

### Higher Quality
```bash
OPENAI_MODEL=openai/gpt-4
```
- **Cost**: ~$30 per 1M tokens
- **Speed**: Moderate
- **Quality**: Excellent

### Anthropic Claude
```bash
OPENAI_MODEL=anthropic/claude-3-haiku
```
- **Cost**: ~$0.25-1.25 per 1M tokens
- **Speed**: Very fast
- **Quality**: Excellent

See all models: https://openrouter.ai/models

## Switching Between Providers

### Development (Ollama)
```bash
export USE_OPENAI=0
export OLLAMA_HOST=http://localhost:11434
export OLLAMA_MODEL=mistral
```

### Production (OpenRouter)
```bash
export USE_OPENAI=1
export OPENAI_API_KEY=sk-or-v1-your-key
export OPENAI_MODEL=openai/gpt-3.5-turbo
```

**Same code works with both!** No changes needed.

## Cost Management

### Monitor Usage
- Dashboard: https://openrouter.ai/activity
- Set spending limits in your account
- Monitor per-model costs

### Keep Costs Low
1. Use `NUM_PREDICT=400` (Fast Mode) for shorter responses
2. Start with `gpt-3.5-turbo` ($0.50 per 1M tokens)
3. Set `TEMP=0.3` for more focused responses
4. Monitor usage regularly

### Example Costs
With `NUM_PREDICT=400` and `gpt-3.5-turbo`:
- **10 students, 20 questions each, 400 tokens/response**
- = 10 × 20 × 400 = 80,000 tokens
- = ~$0.04 per session
- = ~$1.20 per month (30 sessions)

## Troubleshooting

### Error: "OPENAI_API_KEY must be set"
```bash
# Make sure you set the API key
export OPENAI_API_KEY=sk-or-v1-your-actual-key-here
```

### Error: "OpenAI SDK not installed"
```bash
cd backend
pip install openai>=1.0.0
```

### Check Current Configuration
```bash
cd backend
python3 -c "import config; print(f'Provider: {\"OpenRouter\" if config.USE_OPENAI else \"Ollama\"}'); print(f'Model: {config.OPENAI_MODEL if config.USE_OPENAI else config.OLLAMA_MODEL}')"
```

### Test Provider
```bash
cd backend
python3 test_openrouter.py
```

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `USE_OPENAI` | No | `0` | Set to `1` to use OpenRouter |
| `OPENAI_API_KEY` | Yes (when USE_OPENAI=1) | - | Your OpenRouter API key |
| `OPENAI_MODEL` | No | `openai/gpt-3.5-turbo` | Model to use |
| `OPENAI_BASE_URL` | No | `https://openrouter.ai/api/v1` | OpenRouter API base URL |
| `FAST_MODE` | No | `1` | Enable fast mode optimizations |
| `NUM_PREDICT` | No | `400` | Max tokens per response |
| `TEMP` | No | `0.3` | Temperature (0.0-1.0) |

## Security Best Practices

1. **Never commit API keys to git**
   ```bash
   # Use .env file (already in .gitignore)
   echo "OPENAI_API_KEY=sk-or-v1-..." >> .env
   ```

2. **Use secrets management for production**
   ```bash
   # Fly.io
   flyctl secrets set OPENAI_API_KEY=...
   
   # Docker
   docker run -e OPENAI_API_KEY=... (from env var)
   ```

3. **Rotate keys regularly**
   - Generate new keys at https://openrouter.ai/keys
   - Delete old keys after rotation

## Next Steps

1. ✅ Get API key from https://openrouter.ai/keys
2. ✅ Set `USE_OPENAI=1` and `OPENAI_API_KEY`
3. ✅ Choose a model (default: `gpt-3.5-turbo`)
4. ✅ Start backend and test
5. ✅ Deploy to production (see DEPLOYMENT.md)
6. ✅ Monitor usage and costs

## Support

- **OpenRouter Documentation**: https://openrouter.ai/docs
- **Available Models**: https://openrouter.ai/models
- **Usage Dashboard**: https://openrouter.ai/activity
- **Full Integration Guide**: See OPENROUTER_INTEGRATION.md
