"""
Minimal FastAPI backend for EduMate.
- GET /health: Health check
- POST /chat: Streams LLM responses from OpenRouter (SSE)
- Secrets:
    * Prefers OPENROUTER_API_KEY from environment (Fly secrets)
    * Falls back to Google Secret Manager if configured (optional)
"""

import os
import json
from typing import List, Dict, Optional, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx

# --- Optional Google Secret Manager imports ---
try:
    from google.cloud import secretmanager  # type: ignore
    from google.oauth2 import service_account  # type: ignore
except Exception:  # pragma: no cover
    secretmanager = None
    service_account = None

# --- Config ---
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_FRONTEND_URL = "https://edumate.streamlit.app"
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
API_TIMEOUT = httpx.Timeout(connect=15.0, read=120.0, write=30.0, pool=None)

# Cache for the API key after first successful load
OPENROUTER_API_KEY: Optional[str] = None


# --- Key loading: ENV first, GSM second (lazy, safe for mounted apps) ---
def get_openrouter_key() -> str:
    """
    Returns the OpenRouter API key, preferring the OPENROUTER_API_KEY env var.
    If not present, optionally loads from Google Secret Manager if configured.

    Raises:
        RuntimeError if the key cannot be loaded.
    """
    global OPENROUTER_API_KEY
    if OPENROUTER_API_KEY:  # cached after first successful load
        return OPENROUTER_API_KEY

    # 1) ENV (Fly secrets / local dev)
    env_key = os.getenv("OPENROUTER_API_KEY")
    if env_key:
        OPENROUTER_API_KEY = env_key
        return OPENROUTER_API_KEY

    # 2) Optional: Google Secret Manager
    gcp_secret_name = os.getenv("GCP_SECRET_NAME")  # can be full path or simple name
    if gcp_secret_name and secretmanager:
        try:
            creds = None
            sa_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
            if sa_json and service_account:
                # Build credentials from in-memory JSON (no file needed)
                creds = service_account.Credentials.from_service_account_info(json.loads(sa_json))

            client = secretmanager.SecretManagerServiceClient(credentials=creds)
            if "/" in gcp_secret_name:
                # Full resource path provided
                name = gcp_secret_name
            else:
                # Simple name provided, need project id
                project = PROJECT_ID or os.getenv("GOOGLE_CLOUD_PROJECT")
                if not project:
                    raise RuntimeError("GOOGLE_CLOUD_PROJECT not set for Secret Manager lookup")
                name = f"projects/{project}/secrets/{gcp_secret_name}/versions/latest"

            resp = client.access_secret_version(request={"name": name})
            OPENROUTER_API_KEY = resp.payload.data.decode("UTF-8")
            return OPENROUTER_API_KEY
        except Exception as e:  # do not log sensitive details
            print(f"[WARNING] GCP Secret Manager lookup failed: {type(e).__name__}")

    raise RuntimeError("OPENROUTER_API_KEY not configured. Set Fly secret or GCP Secret Manager.")


# --- FastAPI app ---
app = FastAPI(
    title="EduMate API",
    version="1.0.0",
    description="Backend API that streams chat completions via OpenRouter",
)

# CORS: keep permissive for initial setup; restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # set to [os.getenv("FRONTEND_ORIGIN")] in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Models ---
class ChatRequest(BaseModel):
    model: str = "openrouter/openai/gpt-4o-mini"
    messages: List[Dict[str, Any]]
    temperature: float = 0.2


# --- Health ---
@app.get("/health")
def health():
    return {"ok": True}


# --- Chat (SSE streaming) ---
@app.post("/chat")
async def chat(request: ChatRequest):
    # Validate
    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")

    # Load key lazily (works even when app is mounted under /api)
    try:
        api_key = get_openrouter_key()
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        # OpenRouter recommends these (non-sensitive):
        "HTTP-Referer": os.getenv("FRONTEND_ORIGIN", DEFAULT_FRONTEND_URL),
        "X-Title": "EduMate",
    }

    payload = {
        "model": request.model,
        "messages": request.messages,
        "temperature": request.temperature,
        "stream": True,  # request SSE stream
    }

    async def stream_tokens():
        try:
            async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
                async with client.stream(
                    "POST",
                    OPENROUTER_API_URL,
                    headers=headers,
                    json=payload,
                ) as response:
                    if response.status_code != 200:
                        # avoid leaking details; front-end can show a generic message
                        print(f"[ERROR] OpenRouter error status={response.status_code}")
                        yield f"data: {json.dumps({'error':'Upstream API error'})}\n\n"
                        return

                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        if line.startswith("data: "):
                            data_str = line[6:].strip()
                            if data_str == "[DONE]":
                                yield "data: [DONE]\n\n"
                                break
                            # pass through the chunk as-is (client will parse it)
                            yield f"data: {data_str}\n\n"

        except httpx.TimeoutException:
            print("[ERROR] OpenRouter API timeout")
            yield f"data: {json.dumps({'error':'Request timeout'})}\n\n"
        except Exception as e:
            print(f"[ERROR] Streaming error: {type(e).__name__}")
            yield f"data: {json.dumps({'error':'Streaming error'})}\n\n"

    return StreamingResponse(
        stream_tokens(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


# --- Local dev entrypoint ---
if __name__ == "__main__":
    import uvicorn
    print("[INFO] Starting dev server on http://0.0.0.0:8080")
    print("[INFO] Ensure OPENROUTER_API_KEY is set for local testing")
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
