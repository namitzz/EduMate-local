import os
import json
import time
import requests
from typing import Iterator, List, Dict, Optional

import config

# ============================================================================
# OpenRouter API Integration (Cloud LLM - Zero Local Setup)
# ============================================================================

def _openrouter_headers() -> Dict[str, str]:
    """Generate headers for OpenRouter API requests."""
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
    """Generate payload for OpenRouter chat completions."""
    return {
        "model": config.OPENROUTER_MODEL,
        "messages": messages,
        "stream": stream,
        "temperature": config.TEMPERATURE,
        "max_tokens": config.MAX_TOKENS,
    }


def ollama_complete(messages: List[Dict]) -> str:
    """
    Generate a complete response from OpenRouter API.
    
    Note: Function name kept as 'ollama_complete' for backward compatibility,
    but now uses OpenRouter exclusively for cloud deployment.
    """
    url = f"{config.OPENROUTER_BASE_URL}/chat/completions"
    
    try:
        resp = requests.post(
            url,
            headers=_openrouter_headers(),
            json=_openrouter_chat_payload(messages, stream=False),
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.Timeout:
        raise RuntimeError("OpenRouter API request timed out. Please try again.")
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError(f"Failed to connect to OpenRouter API: {str(e)}")
    except requests.exceptions.HTTPError as e:
        error_detail = ""
        try:
            error_detail = e.response.json().get("error", {}).get("message", "")
        except:
            pass
        raise RuntimeError(f"OpenRouter API error: {e.response.status_code} {error_detail}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error calling OpenRouter: {str(e)}")


def ollama_complete_stream(messages: List[Dict]) -> Iterator[str]:
    """
    Stream response tokens from OpenRouter API.
    
    Note: Function name kept as 'ollama_complete_stream' for backward compatibility,
    but now uses OpenRouter exclusively for cloud deployment.
    """
    url = f"{config.OPENROUTER_BASE_URL}/chat/completions"
    
    try:
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
                        # Ignore malformed SSE fragments
                        continue
    except requests.exceptions.Timeout:
        yield "\n\n⏱️ OpenRouter API request timed out. Please try again."
    except requests.exceptions.ConnectionError:
        yield "\n\n❌ Failed to connect to OpenRouter API. Please check your internet connection."
    except Exception as e:
        yield f"\n\n❌ Error: {str(e)}"

