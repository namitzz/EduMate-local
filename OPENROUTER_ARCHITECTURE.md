# OpenRouter Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        EduMate Application                       │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         backend/main.py                          │
│                     (FastAPI Endpoints)                          │
│                    /chat, /chat_stream                           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        backend/models.py                         │
│              (Backward Compatibility Layer)                      │
│   ollama_complete, ollama_complete_stream (legacy)               │
│   llm_complete, llm_complete_stream (new unified)                │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      backend/providers.py                        │
│                   (Provider Abstraction)                         │
└─────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
        ┌──────────────────┐    ┌──────────────────┐
        │  Ollama Provider │    │ OpenRouter (OAI) │
        │  (Local/Docker)  │    │  (Cloud/Prod)    │
        └──────────────────┘    └──────────────────┘
                    │                       │
                    ▼                       ▼
        ┌──────────────────┐    ┌──────────────────┐
        │ Local Ollama     │    │ OpenRouter API   │
        │ localhost:11434  │    │ openrouter.ai    │
        └──────────────────┘    └──────────────────┘
```

## Configuration Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Environment Variables                         │
└─────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
        ┌──────────────────┐    ┌──────────────────┐
        │  USE_OPENAI=0    │    │  USE_OPENAI=1    │
        │  (Default)       │    │  (Cloud)         │
        └──────────────────┘    └──────────────────┘
                    │                       │
                    ▼                       ▼
        ┌──────────────────┐    ┌──────────────────┐
        │ Ollama Config    │    │ OpenRouter Config│
        │ • OLLAMA_HOST    │    │ • OPENAI_API_KEY │
        │ • OLLAMA_MODEL   │    │ • OPENAI_MODEL   │
        └──────────────────┘    └──────────────────┘
                    │                       │
                    └───────────┬───────────┘
                                ▼
                    ┌──────────────────┐
                    │  backend/config.py│
                    │  Validates & Loads│
                    └──────────────────┘
```

## Request Flow

```
User Request
    │
    ▼
┌─────────────────┐
│ Streamlit UI    │
│ (app_public.py) │
└─────────────────┘
    │
    │ HTTP POST /chat_stream
    ▼
┌─────────────────┐
│ FastAPI         │
│ backend/main.py │
└─────────────────┘
    │
    │ Retrieval (RAG)
    ▼
┌─────────────────┐
│ Retriever       │
│ (ChromaDB)      │
└─────────────────┘
    │
    │ Build Prompt
    ▼
┌─────────────────┐
│ models.py       │
│ llm_complete_   │
│ stream()        │
└─────────────────┘
    │
    │ Route based on USE_OPENAI
    ▼
┌─────────────────────────────────────┐
│        providers.py                 │
│  if USE_OPENAI:                     │
│    openrouter_complete_stream()     │
│  else:                              │
│    ollama_complete_stream()         │
└─────────────────────────────────────┘
    │
    └─► LLM Provider (Ollama or OpenRouter)
```

## File Dependencies

```
main.py
  ├── models.py
  │     └── providers.py
  │           ├── config.py
  │           ├── requests (for Ollama)
  │           ├── aiohttp (for Ollama streaming)
  │           └── openai (for OpenRouter)
  ├── retrieval.py
  │     └── config.py
  └── config.py
```

## Environment Variables Hierarchy

```
Backend Configuration
├── LLM Provider Selection
│   └── USE_OPENAI (0 or 1)
│
├── OpenRouter Config (USE_OPENAI=1)
│   ├── OPENAI_API_KEY (required)
│   ├── OPENAI_MODEL (default: openai/gpt-3.5-turbo)
│   └── OPENAI_BASE_URL (default: https://openrouter.ai/api/v1)
│
├── Ollama Config (USE_OPENAI=0)
│   ├── OLLAMA_HOST (default: http://localhost:11434)
│   └── OLLAMA_MODEL (default: mistral)
│
└── Generation Settings (both providers)
    ├── FAST_MODE (default: 1)
    ├── NUM_PREDICT (default: 400)
    ├── TEMP (default: 0.3)
    └── MAX_ACTIVE_GENERATIONS (default: 1)
```

## Deployment Scenarios

### Scenario 1: Local Development
```
Developer Machine
  ├── Backend (Python)
  │   ├── USE_OPENAI=0
  │   └── Ollama (localhost:11434)
  └── UI (Streamlit)
      └── localhost:8501
```

### Scenario 2: Docker Local
```
Docker Compose
  ├── Ollama Container
  │   └── ollama:11434
  ├── Backend Container
  │   ├── USE_OPENAI=0
  │   └── OLLAMA_HOST=http://ollama:11434
  └── UI Container
      └── port 8501
```

### Scenario 3: Cloud Production (Fly.io)
```
Fly.io
  ├── Backend App
  │   ├── USE_OPENAI=1
  │   ├── OPENAI_API_KEY (secret)
  │   └── Connects to OpenRouter API
  └── (Optional) Separate UI deployment
```

## Provider Comparison

| Feature | Ollama | OpenRouter |
|---------|--------|------------|
| **Setup** | Install locally | API key only |
| **Cost** | Free (own hardware) | Pay-per-use |
| **Models** | Pull manually | 100+ models |
| **Latency** | Low (local) | Varies by model |
| **Scaling** | Limited by hardware | Unlimited |
| **Best For** | Dev, privacy | Production, variety |
| **Config** | OLLAMA_HOST | OPENAI_API_KEY |

## Testing Structure

```
Backend Tests
├── test_openrouter.py
│   ├── Config provider selection
│   ├── Provider module imports
│   ├── OpenAI SDK availability
│   ├── Provider selection logic
│   ├── Configuration validation
│   └── Backward compatibility
│
└── test_provider_integration.py
    ├── Ollama provider validation
    ├── OpenRouter provider validation
    ├── Environment validation
    └── Backward compatibility
```

## Code Organization

```
EduMate-local/
├── backend/
│   ├── config.py           # Configuration with provider selection
│   ├── providers.py        # NEW: Provider abstraction
│   ├── models.py          # Backward compatibility wrapper
│   ├── main.py            # FastAPI endpoints (unchanged)
│   ├── retrieval.py       # RAG logic (unchanged)
│   ├── requirements.txt   # Added openai SDK
│   ├── test_openrouter.py # NEW: Provider tests
│   └── test_provider_integration.py # NEW: Integration tests
│
├── Documentation/
│   ├── README.md                    # Updated with provider info
│   ├── DEPLOYMENT.md                # Updated with OpenRouter guide
│   ├── .env.example                 # Updated with all env vars
│   ├── OPENROUTER_INTEGRATION.md    # NEW: Full integration guide
│   ├── OPENROUTER_QUICKSTART.md     # NEW: Quick start guide
│   └── OPENROUTER_ARCHITECTURE.md   # This file
│
└── ui/                     # Unchanged
    ├── app_simple.py
    ├── app.py
    └── app_public.py
```

## Key Design Decisions

### 1. Provider Abstraction
- Created `providers.py` to separate provider logic
- Maintained backward compatibility in `models.py`
- New code uses `llm_complete()` unified interface

### 2. Environment-Based Switching
- Single variable (`USE_OPENAI`) controls provider
- No code changes needed to switch providers
- Validates required configs at startup

### 3. Backward Compatibility
- All existing imports continue to work
- `ollama_complete()` and `ollama_complete_stream()` preserved
- New unified functions added alongside legacy ones

### 4. Zero Breaking Changes
- Default behavior (Ollama) unchanged
- CORS already configured
- Existing endpoints work identically
- Same response format for both providers

## Migration Path

### From Legacy to New Interface
```python
# Old code (still works)
from models import ollama_complete
response = ollama_complete(prompt)

# New code (provider-agnostic)
from models import llm_complete
response = llm_complete(prompt)
```

### Local to Cloud Migration
```bash
# Step 1: Get OpenRouter API key
# Step 2: Update environment
USE_OPENAI=1
OPENAI_API_KEY=sk-or-v1-...

# Step 3: Restart - that's it!
```

## Security Considerations

1. **API Keys**: Never committed to git (`.gitignore` includes `.env`)
2. **Secrets Management**: Use platform secrets (Fly.io, Docker, etc.)
3. **Key Rotation**: Easy to update via environment variables
4. **Validation**: Config validates required vars at startup

## Performance Characteristics

### Ollama (Local)
- **First Request**: 2-8 seconds (model loading)
- **Subsequent**: 0.5-2 seconds
- **Throughput**: Limited by hardware
- **Concurrency**: Controlled by semaphore

### OpenRouter (Cloud)
- **First Request**: 1-3 seconds
- **Subsequent**: 1-3 seconds
- **Throughput**: High (API scales)
- **Concurrency**: API handles scaling

## Cost Analysis (Example)

### OpenRouter with gpt-3.5-turbo
```
Assumptions:
- 10 students
- 20 questions per session
- 400 tokens per response
- $0.50 per 1M tokens

Calculation:
- Tokens per session: 10 × 20 × 400 = 80,000
- Cost per session: 80,000 / 1,000,000 × $0.50 = $0.04
- Cost per month (30 sessions): $0.04 × 30 = $1.20

Annual cost: ~$15
```

### Ollama (Local)
- Hardware: One-time investment
- Electricity: Negligible
- Maintenance: Time only
- Cost: Effectively free after setup

## Conclusion

This architecture provides:
- ✅ Flexible deployment options
- ✅ Easy provider switching
- ✅ Backward compatibility
- ✅ Production readiness
- ✅ Cost optimization
- ✅ Clear separation of concerns
