"""
LLM Provider abstraction for Ollama and OpenRouter (OpenAI-compatible).
Provides a unified interface for both streaming and non-streaming completions.
"""
import os
import json
import time
import requests
import aiohttp
from typing import AsyncGenerator, Optional
import config


# -----------------------
# OpenRouter (OpenAI-compatible) Provider
# -----------------------
def openrouter_complete(prompt: str, model: str | None = None) -> str:
    """
    Complete using OpenRouter API (OpenAI-compatible).
    Uses the official OpenAI SDK for compatibility.
    """
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError(
            "OpenAI SDK not installed. Install with: pip install openai>=1.0.0"
        )
    
    model = model or config.OPENAI_MODEL
    
    print(f"[DEBUG] Using OpenRouter with model: {model}")
    print(f"[DEBUG] Base URL: {config.OPENAI_BASE_URL}")
    
    client = OpenAI(
        api_key=config.OPENAI_API_KEY,
        base_url=config.OPENAI_BASE_URL,
    )
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=config.TEMPERATURE,
            max_tokens=config.MAX_TOKENS,
        )
        
        text = response.choices[0].message.content.strip()
        if text:
            return text
        
        print(f"[WARNING] OpenRouter returned empty response")
        raise RuntimeError("Empty response from OpenRouter")
        
    except Exception as e:
        print(f"[ERROR] OpenRouter API error: {e}")
        raise RuntimeError(f"OpenRouter API error: {e}")


async def openrouter_complete_stream(prompt: str, model: str | None = None) -> AsyncGenerator[str, None]:
    """
    Stream tokens from OpenRouter API (OpenAI-compatible).
    Uses the official OpenAI SDK for streaming.
    """
    try:
        from openai import AsyncOpenAI
    except ImportError:
        yield "[Error: OpenAI SDK not installed. Install with: pip install openai>=1.0.0]"
        return
    
    model = model or config.OPENAI_MODEL
    
    print(f"[DEBUG] Streaming from OpenRouter with model: {model}")
    print(f"[DEBUG] Base URL: {config.OPENAI_BASE_URL}")
    
    client = AsyncOpenAI(
        api_key=config.OPENAI_API_KEY,
        base_url=config.OPENAI_BASE_URL,
    )
    
    try:
        stream = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=config.TEMPERATURE,
            max_tokens=config.MAX_TOKENS,
            stream=True,
        )
        
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
                
    except Exception as e:
        print(f"[ERROR] OpenRouter streaming error: {e}")
        yield f"[Streaming error from OpenRouter: {e}]"


# -----------------------
# Ollama Provider
# -----------------------
def ollama_complete(prompt: str, model: str | None = None) -> str:
    """Complete using local Ollama instance."""
    url = config.OLLAMA_HOST.rstrip("/")
    model = model or config.OLLAMA_MODEL
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": config.TEMPERATURE, "num_predict": config.MAX_TOKENS},
        "keep_alive": "2h",
    }

    print(f"[DEBUG] Attempting to connect to Ollama at: {url}")
    print(f"[DEBUG] Using model: {model}")
    
    # Retry a couple of times to ride out cold-starts
    last_err = None
    for attempt in range(3):
        try:
            r = requests.post(f"{url}/api/generate", json=payload, timeout=180)
            r.raise_for_status()
            data = r.json()
            text = (data.get("response") or "").strip()
            if text:
                return text
            # Log when we get empty response
            print(f"[WARNING] Ollama returned empty response on attempt {attempt + 1}/3. Full data: {data}")
            raise RuntimeError("Empty response from Ollama")
        except requests.ReadTimeout as e:
            last_err = e
            print(f"[WARNING] Ollama ReadTimeout on attempt {attempt + 1}/3: {e}")
            time.sleep(2 + 2*attempt)  # backoff: 2s, 4s, 6s
        except requests.ConnectionError as e:
            last_err = e
            print(f"[WARNING] Ollama ConnectionError on attempt {attempt + 1}/3: {e}")
            time.sleep(2 + 2*attempt)  # backoff: 2s, 4s, 6s
        except requests.HTTPError as e:
            last_err = e
            print(f"[WARNING] Ollama HTTPError on attempt {attempt + 1}/3: {e}")
            time.sleep(2 + 2*attempt)  # backoff: 2s, 4s, 6s
        except json.JSONDecodeError as e:
            last_err = e
            print(f"[WARNING] Ollama JSONDecodeError on attempt {attempt + 1}/3: {e}")
            time.sleep(2 + 2*attempt)  # backoff: 2s, 4s, 6s
    
    # Provide detailed error message based on error type
    print(f"[ERROR] Failed to connect to Ollama at {url} after {attempt + 1} retries")
    print(f"[ERROR] Troubleshooting:")
    print(f"[ERROR]   - For local: Ensure Ollama is running (http://localhost:11434)")
    print(f"[ERROR]   - For Docker: Verify OLLAMA_HOST=http://ollama:11434")
    print(f"[ERROR]   - For cloud: Set OLLAMA_HOST to your public API endpoint (NOT localhost)")
    if isinstance(last_err, requests.ReadTimeout):
        raise RuntimeError(f"Ollama ReadTimeout after {attempt + 1} retries (URL: {url}): {last_err}")
    elif isinstance(last_err, requests.ConnectionError):
        raise RuntimeError(f"Ollama ConnectionError after {attempt + 1} retries (URL: {url}): {last_err}")
    elif isinstance(last_err, requests.HTTPError):
        raise RuntimeError(f"Ollama HTTPError after {attempt + 1} retries (URL: {url}): {last_err}")
    else:
        raise RuntimeError(f"Ollama call failed after {attempt + 1} retries (URL: {url}): {last_err}")


async def ollama_complete_stream(prompt: str, model: str | None = None) -> AsyncGenerator[str, None]:
    """
    Stream tokens from Ollama using /api/chat endpoint.
    Yields text deltas as they arrive.
    """
    url = config.OLLAMA_HOST.rstrip("/")
    model = model or config.OLLAMA_MODEL
    
    print(f"[DEBUG] Attempting to stream from Ollama at: {url}")
    print(f"[DEBUG] Using model: {model}")
    
    # Use chat format for streaming
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,
        "options": {"temperature": config.TEMPERATURE, "num_predict": config.MAX_TOKENS},
        "keep_alive": "2h",
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{url}/api/chat",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=180)
            ) as response:
                response.raise_for_status()
                
                async for line in response.content:
                    if line:
                        try:
                            data = json.loads(line.decode('utf-8'))
                            if "message" in data and "content" in data["message"]:
                                delta = data["message"]["content"]
                                if delta:
                                    yield delta
                            # Check if done
                            if data.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue
    except Exception as e:
        print(f"[ERROR] Streaming error from {url}: {e}")
        yield f"[Streaming error (URL: {url}): {e}]"


# -----------------------
# Unified Provider Interface
# -----------------------
def llm_complete(prompt: str, model: str | None = None) -> str:
    """
    Unified completion interface that routes to the appropriate provider.
    Uses OpenRouter if USE_OPENAI=1, otherwise uses Ollama.
    """
    if config.USE_OPENAI:
        return openrouter_complete(prompt, model)
    else:
        return ollama_complete(prompt, model)


async def llm_complete_stream(prompt: str, model: str | None = None) -> AsyncGenerator[str, None]:
    """
    Unified streaming interface that routes to the appropriate provider.
    Uses OpenRouter if USE_OPENAI=1, otherwise uses Ollama.
    """
    if config.USE_OPENAI:
        async for token in openrouter_complete_stream(prompt, model):
            yield token
    else:
        async for token in ollama_complete_stream(prompt, model):
            yield token
