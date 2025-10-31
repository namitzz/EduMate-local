"""
Minimal FastAPI app for Google App Engine Standard deployment.
Streams LLM responses from OpenRouter API using Google Secret Manager for credentials.

This is a production-safe implementation for App Engine (Option 1):
- GET /health: Health check endpoint
- POST /chat: Streaming chat completions from OpenRouter API
- Loads API key from Google Secret Manager (no secrets in code)
- Implements timeout and error handling
- Permissive CORS (TODO: restrict to FRONTEND_ORIGIN in production)
"""
import os
import json
from typing import List, Dict, Optional, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx
from google.cloud import secretmanager


# --- Configuration ---
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")  # Automatically set by App Engine
OPENROUTER_API_KEY = None  # Will be loaded from Secret Manager at startup
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_FRONTEND_URL = "https://edumate.streamlit.app"
API_TIMEOUT_SECONDS = int(os.getenv("API_TIMEOUT", "60"))  # Configurable timeout


# --- Secret Manager Integration ---
def load_secret_from_gcp(secret_name: str) -> str:
    """
    Load a secret from Google Cloud Secret Manager.
    
    Args:
        secret_name: Name of the secret (e.g., 'OPENROUTER_API_KEY')
    
    Returns:
        The secret value as a string
    
    Raises:
        RuntimeError: If secret cannot be loaded
    """
    if not PROJECT_ID:
        raise RuntimeError("GOOGLE_CLOUD_PROJECT environment variable not set")
    
    client = secretmanager.SecretManagerServiceClient()
    secret_path = f"projects/{PROJECT_ID}/secrets/{secret_name}/versions/latest"
    
    try:
        response = client.access_secret_version(request={"name": secret_path})
        secret_value = response.payload.data.decode("UTF-8")
        print(f"[INFO] Successfully loaded secret: {secret_name}")
        return secret_value
    except Exception as e:
        print(f"[ERROR] Failed to load secret {secret_name}: {e}")
        raise RuntimeError(f"Failed to load secret {secret_name}: {e}")


# --- Application Lifecycle ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle handler.
    Loads secrets from Secret Manager at startup.
    """
    global OPENROUTER_API_KEY
    
    # Try to load from environment first (for local testing)
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    
    # If not in environment, load from Secret Manager (production on App Engine)
    if not OPENROUTER_API_KEY and PROJECT_ID:
        try:
            OPENROUTER_API_KEY = load_secret_from_gcp("OPENROUTER_API_KEY")
        except Exception as e:
            print(f"[WARNING] Could not load OPENROUTER_API_KEY from Secret Manager: {e}")
            print("[WARNING] API calls will fail without a valid API key")
    
    if OPENROUTER_API_KEY:
        print("[INFO] OPENROUTER_API_KEY loaded successfully")
    else:
        print("[WARNING] OPENROUTER_API_KEY not set - API calls will fail")
    
    yield
    
    # Cleanup (if needed)
    print("[INFO] Shutting down...")


# --- FastAPI App ---
app = FastAPI(
    title="EduMate App Engine API",
    version="0.1.0",
    description="Minimal LLM proxy for App Engine Standard deployment",
    lifespan=lifespan
)

# TODO: Restrict CORS to FRONTEND_ORIGIN only in production
# For now, allow all origins for easier initial setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Change to [os.getenv("FRONTEND_ORIGIN")] in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request/Response Models ---
class ChatRequest(BaseModel):
    """
    Chat request payload matching OpenRouter API format.
    """
    model: str = "openrouter/anthropic/claude-3.5-sonnet"
    messages: List[Dict[str, Any]]  # Support complex message formats (function calls, etc.)
    temperature: float = 0.2


# --- Health Check ---
@app.get("/health")
def health():
    """
    Health check endpoint for App Engine load balancer.
    
    Returns:
        dict: Status indicator
    """
    return {"ok": True}


# --- Chat Endpoint with Streaming ---
@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Stream chat completions from OpenRouter API.
    
    Accepts OpenAI-compatible chat format and streams tokens via Server-Sent Events (SSE).
    Uses httpx.AsyncClient for streaming with proper timeout handling.
    
    Args:
        request: ChatRequest with model, messages, and temperature
    
    Returns:
        StreamingResponse: Server-Sent Events stream of chat tokens
    
    Raises:
        HTTPException: If API key is not configured or request is invalid
    
    Note:
        Never logs sensitive user content. Only logs error types for debugging.
    """
    if not OPENROUTER_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="OPENROUTER_API_KEY not configured. Please set up Secret Manager."
        )
    
    # Validate request
    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")
    
    # OpenRouter API endpoint (OpenAI-compatible)
    url = OPENROUTER_API_URL
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": os.getenv("FRONTEND_ORIGIN", DEFAULT_FRONTEND_URL),
        "X-Title": "EduMate",
    }
    
    payload = {
        "model": request.model,
        "messages": request.messages,
        "temperature": request.temperature,
        "stream": True,  # Enable streaming
    }
    
    # Stream response from OpenRouter
    async def stream_tokens():
        """
        Stream tokens from OpenRouter API as Server-Sent Events.
        Implements proper error handling and timeout management.
        Never logs user message content for privacy.
        """
        try:
            # Use httpx.AsyncClient with configurable timeout for streaming
            async with httpx.AsyncClient(timeout=API_TIMEOUT_SECONDS) as client:
                async with client.stream(
                    "POST",
                    url,
                    headers=headers,
                    json=payload,
                ) as response:
                    # Handle API errors
                    if response.status_code != 200:
                        # Don't log potentially sensitive error details
                        print(f"[ERROR] OpenRouter API error: status={response.status_code}")
                        yield f"data: {json.dumps({'error': 'API request failed'})}\n\n"
                        return
                    
                    # Process SSE stream from OpenRouter
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        
                        if line.startswith("data: "):
                            data_str = line[6:]  # Remove "data: " prefix
                            
                            # Check for stream completion
                            if data_str.strip() == "[DONE]":
                                yield "data: [DONE]\n\n"
                                break
                            
                            try:
                                # Parse and forward SSE chunk to client
                                data = json.loads(data_str)
                                yield f"data: {json.dumps(data)}\n\n"
                            except json.JSONDecodeError:
                                # Ignore malformed JSON chunks (common in SSE streams)
                                continue
        
        except httpx.TimeoutException:
            # Handle timeout without logging user data
            print("[ERROR] OpenRouter API timeout")
            yield f"data: {json.dumps({'error': 'Request timeout'})}\n\n"
        except Exception as e:
            # Generic error handling - don't log potentially sensitive user data
            print(f"[ERROR] Streaming error: {type(e).__name__}")
            yield f"data: {json.dumps({'error': 'Streaming error'})}\n\n"
    
    return StreamingResponse(
        stream_tokens(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


# --- For local testing ---
if __name__ == "__main__":
    import uvicorn
    print("[INFO] Starting development server...")
    print("[INFO] Make sure OPENROUTER_API_KEY is set in environment for local testing")
    print("[INFO] Example: export OPENROUTER_API_KEY=sk-or-v1-...")
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
