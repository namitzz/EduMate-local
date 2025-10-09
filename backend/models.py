import os
import json
import time
import requests
from typing import Iterator, List, Dict, Optional

import config

# ---- Helpers ----

def _openrouter_headers() -> Dict[str, str]:
    headers = {
        "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    if config.OPENROUTER_SITE_URL:
        headers["HTTP-Referer"] = config.OPENROUTER_SITE_URL
    if config.OPENROUTER_APP_NAME:
        headers["X-Title"] = config.OPENROUTER_APP_NAME
    return headers

def _openrouter_chat_payload(messages: List[Dict], stream: bool = False) -> Dict:
    return {
        "model": config.OPENROUTER_MODEL,
        "messages": messages,
        "stream": stream,
        # You can add max_tokens, temperature, top_p, etc., here if desired.
    }

# ---- Cloud path (OpenRouter, OpenAI-compatible) ----

def _openrouter_complete(messages: List[Dict]) -> str:
    url = f"{config.OPENROUTER_BASE_URL}/chat/completions"
    resp = requests.post(
        url,
        headers=_openrouter_headers(),
        json=_openrouter_chat_payload(messages, stream=False),
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]

def _openrouter_complete_stream(messages: List[Dict]) -> Iterator[str]:
    url = f"{config.OPENROUTER_BASE_URL}/chat/completions"
    with requests.post(
        url,
        headers=_openrouter_headers(),
        json=_openrouter_chat_payload(messages, stream=True),
        stream=True,
        timeout=300,
    ) as r:
        r.raise_for_status()
        for line in r.iter_lines(decode_unicode=True):
            if not line:
                continue
            if line.startswith("data: "):
                chunk = line[len("data: "):]
                if chunk.strip() == "[DONE]":
                    break
                try:
                    obj = json.loads(chunk)
                    delta = obj["choices"][0]["delta"].get("content", "")
                    if delta:
                        yield delta
                except Exception:
                    # ignore malformed SSE fragments
                    continue

# ---- Optional: Local Ollama fallback (only if USE_OPENROUTER=0) ----

def _ollama_complete(messages: List[Dict]) -> str:
    base = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "mistral")
    resp = requests.post(
        f"{base}/api/chat",
        json={"model": model, "messages": messages, "stream": False},
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    # Ollama returns a list of messages or a single message depending on version
    if isinstance(data, dict) and "message" in data:
        return data["message"].get("content", "")
    # fallback concatenate
    return "".join(m.get("message", {}).get("content", "") for m in data if isinstance(m, dict))

def _ollama_complete_stream(messages: List[Dict]) -> Iterator[str]:
    base = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "mistral")
    with requests.post(
        f"{base}/api/chat",
        json={"model": model, "messages": messages, "stream": True},
        stream=True,
        timeout=300,
    ) as r:
        r.raise_for_status()
        for line in r.iter_lines(decode_unicode=True):
            if not line:
                continue
            try:
                obj = json.loads(line)
                token = obj.get("message", {}).get("content", "")
                if token:
                    yield token
            except Exception:
                continue

# ---- Public API used by main.py ----

def ollama_complete(messages: List[Dict]) -> str:
    if config.USE_OPENROUTER:
        return _openrouter_complete(messages)
    return _ollama_complete(messages)

def ollama_complete_stream(messages: List[Dict]) -> Iterator[str]:
    if config.USE_OPENROUTER:
        return _openrouter_complete_stream(messages)
    return _ollama_complete_stream(messages)
