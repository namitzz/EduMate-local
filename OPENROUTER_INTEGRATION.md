# OpenRouter Integration Summary

This document summarizes the OpenRouter (OpenAI-compatible) provider integration for EduMate.

## Overview

EduMate now supports two LLM providers that can be switched via environment variables:
1. **Ollama** (local/dev) - Default, requires local Ollama instance
2. **OpenRouter** (cloud/production) - Uses OpenAI-compatible API, no local infrastructure needed

## What Was Changed

### 1. Dependencies (`backend/requirements.txt`)
- **Added**: `openai>=1.0.0` - Official OpenAI SDK for OpenRouter compatibility

### 2. Configuration (`backend/config.py`)
- **Added**: `USE_OPENAI` environment variable (default: `0`)
  - `USE_OPENAI=1` → Use OpenRouter
  - `USE_OPENAI=0` or unset → Use Ollama (default)
- **Added**: OpenRouter configuration variables:
  - `OPENAI_API_KEY` - Required when `USE_OPENAI=1`
  - `OPENAI_BASE_URL` - Default: `https://openrouter.ai/api/v1`
  - `OPENAI_MODEL` - Default: `openai/gpt-3.5-turbo`
- **Updated**: Ollama validation to only trigger when `USE_OPENAI=0`
- **Updated**: Added OpenRouter validation when `USE_OPENAI=1`

### 3. Provider Abstraction (`backend/providers.py`) - NEW FILE
Created a new module to abstract LLM provider logic:
- `openrouter_complete()` - Non-streaming OpenRouter completion
- `openrouter_complete_stream()` - Streaming OpenRouter completion
- `ollama_complete()` - Non-streaming Ollama completion (moved from models.py)
- `ollama_complete_stream()` - Streaming Ollama completion (moved from models.py)
- `llm_complete()` - **NEW**: Unified interface that routes to appropriate provider
- `llm_complete_stream()` - **NEW**: Unified streaming interface

### 4. Models Module (`backend/models.py`)
- **Changed**: Now imports from `providers.py` for backward compatibility
- **Maintains**: All existing function signatures (`ollama_complete`, `ollama_complete_stream`)
- **Exports**: New unified functions (`llm_complete`, `llm_complete_stream`)
- **Result**: Existing code continues to work without changes

### 5. Documentation

#### `.env.example`
- Added comprehensive OpenRouter configuration section
- Added `USE_OPENAI` documentation
- Added OpenRouter API key setup instructions
- Added model selection examples

#### `README.md`
- Updated introduction to mention both local and cloud deployment
- Added "LLM Provider Configuration" section with:
  - Ollama (local) setup
  - OpenRouter (cloud) setup
  - Environment variable summary
  - Links to deployment guide

#### `DEPLOYMENT.md`
- Added complete "Cloud LLM Provider (OpenRouter)" section with:
  - Why use OpenRouter for cloud deployments
  - Setup instructions
  - Available models
  - Docker deployment example
  - Fly.io deployment example with secrets management
  - Cost considerations
  - Switching guide between Ollama and OpenRouter

### 6. Tests

#### `backend/test_openrouter.py` - NEW FILE
Tests for OpenRouter integration:
- Provider selection configuration
- Module imports
- OpenAI SDK availability
- Provider selection logic
- Configuration validation
- Backward compatibility

#### `backend/test_provider_integration.py` - NEW FILE
Integration tests for provider switching:
- Ollama provider validation
- OpenRouter provider validation
- Environment variable validation
- Backward compatibility with models.py

## Key Features

### 1. Seamless Provider Switching
Switch between providers with a single environment variable:
```bash
# Local development
export USE_OPENAI=0
export OLLAMA_HOST=http://localhost:11434

# Production with OpenRouter
export USE_OPENAI=1
export OPENAI_API_KEY=sk-or-v1-your-key-here
```

### 2. Backward Compatibility
All existing code using `ollama_complete()` continues to work without changes.

### 3. Unified Interface
New code can use `llm_complete()` which automatically uses the configured provider.

### 4. Streaming Support
Both providers support streaming responses through the unified `llm_complete_stream()` interface.

### 5. Proper Error Handling
- Validates required environment variables at startup
- Clear error messages for missing configuration
- Detailed troubleshooting information

## Usage Examples

### Local Development (Ollama)
```bash
# .env or environment
USE_OPENAI=0
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=mistral
```

### Production (OpenRouter on Fly.io)
```bash
# Set via flyctl
flyctl secrets set OPENAI_API_KEY=sk-or-v1-your-key-here

# fly.toml
[env]
  USE_OPENAI = "1"
  OPENAI_MODEL = "openai/gpt-3.5-turbo"
  FAST_MODE = "1"
```

### Docker Deployment with OpenRouter
```bash
docker run -p 8000:8000 \
  -e USE_OPENAI=1 \
  -e OPENAI_API_KEY=sk-or-v1-your-key-here \
  -e OPENAI_MODEL=openai/gpt-3.5-turbo \
  edumate-backend
```

## Migration Guide

### For Existing Deployments
No changes needed! The default behavior (Ollama) is preserved.

### To Enable OpenRouter
1. Get an API key from https://openrouter.ai/keys
2. Set environment variables:
   ```bash
   USE_OPENAI=1
   OPENAI_API_KEY=your-api-key
   ```
3. Restart the application

### To Switch Back to Ollama
1. Set or remove environment variables:
   ```bash
   USE_OPENAI=0  # or unset
   OLLAMA_HOST=http://localhost:11434
   ```
2. Restart the application

## Testing

All tests pass successfully:

### OpenRouter Provider Tests (`test_openrouter.py`)
```
✓ PASSED: Config Provider Selection
✓ PASSED: Provider Module Imports
✓ PASSED: OpenAI SDK Availability
✓ PASSED: Provider Selection Logic
✓ PASSED: Configuration Validation
✓ PASSED: Backward Compatibility
Total: 6/6 tests passed
```

### Integration Tests (`test_provider_integration.py`)
```
✓ PASSED: Ollama Provider
✓ PASSED: OpenRouter Provider
✓ PASSED: Environment Validation
✓ PASSED: Backward Compatibility
Total: 4/4 tests passed
```

## Available OpenRouter Models

Popular models available through OpenRouter:
- `openai/gpt-3.5-turbo` - Fast, cost-effective (recommended default)
- `openai/gpt-4` - Higher quality, more expensive
- `anthropic/claude-3-haiku` - Fast Claude model
- `anthropic/claude-3-sonnet` - Balanced Claude model
- See full list: https://openrouter.ai/models

## Cost Considerations

- OpenRouter uses pay-per-use pricing
- Monitor usage at https://openrouter.ai/activity
- Set spending limits in your OpenRouter account
- `NUM_PREDICT=400` (Fast Mode) keeps responses short and costs low
- Start with `gpt-3.5-turbo` for cost efficiency

## Security

- **Never commit API keys to the repository**
- Use environment variables or secrets management
- For Fly.io: `flyctl secrets set OPENAI_API_KEY=...`
- For Docker: Pass via `-e` flag or `.env` file (gitignored)
- For local dev: Use `.env` file (already in `.gitignore`)

## CORS Configuration

CORS is already configured in `backend/main.py` with wildcard origins (`allow_origins=["*"]`), which supports Streamlit and other frontends without additional configuration.

## Files Changed

1. `backend/requirements.txt` - Added openai SDK
2. `backend/config.py` - Added OpenRouter configuration
3. `backend/providers.py` - NEW: Provider abstraction layer
4. `backend/models.py` - Updated to use providers.py
5. `.env.example` - Added OpenRouter documentation
6. `README.md` - Updated with provider selection guide
7. `DEPLOYMENT.md` - Added comprehensive OpenRouter deployment guide
8. `backend/test_openrouter.py` - NEW: OpenRouter tests
9. `backend/test_provider_integration.py` - NEW: Integration tests

## Summary

This implementation provides a clean, backward-compatible way to use either Ollama (local) or OpenRouter (cloud) as the LLM provider. The switch is controlled by a single environment variable (`USE_OPENAI`), making it easy to use Ollama for local development and OpenRouter for production cloud deployments.

Key benefits:
- ✅ No breaking changes to existing code
- ✅ Easy environment-based switching
- ✅ Comprehensive documentation
- ✅ Full test coverage
- ✅ Production-ready for cloud deployment
- ✅ CORS already configured for Streamlit
