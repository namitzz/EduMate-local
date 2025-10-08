import os, requests, json, time
import aiohttp
from typing import AsyncGenerator
import config

def ollama_complete(prompt: str, model: str | None = None) -> str:
    url = (config.OLLAMA_HOST or os.getenv("OLLAMA_HOST") or "http://host.docker.internal:11434").rstrip("/")
    model = model or config.OLLAMA_MODEL
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": config.TEMPERATURE, "num_predict": config.MAX_TOKENS},
        "keep_alive": "2h",
    }

    # Retry a couple of times to ride out cold-starts
    last_err = None
    for attempt in range(3):
        try:
            r = requests.post(f"{url}/api/generate", json=payload, timeout=180)  # bump to 180s
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
    if isinstance(last_err, requests.ReadTimeout):
        raise RuntimeError(f"Ollama ReadTimeout after {attempt + 1} retries: {last_err}")
    elif isinstance(last_err, requests.ConnectionError):
        raise RuntimeError(f"Ollama ConnectionError after {attempt + 1} retries: {last_err}")
    elif isinstance(last_err, requests.HTTPError):
        raise RuntimeError(f"Ollama HTTPError after {attempt + 1} retries: {last_err}")
    else:
        raise RuntimeError(f"Ollama call failed after {attempt + 1} retries: {last_err}")


async def ollama_complete_stream(prompt: str, model: str | None = None) -> AsyncGenerator[str, None]:
    """
    Stream tokens from Ollama using /api/chat endpoint.
    Yields text deltas as they arrive.
    """
    url = (config.OLLAMA_HOST or os.getenv("OLLAMA_HOST") or "http://host.docker.internal:11434").rstrip("/")
    model = model or config.OLLAMA_MODEL
    
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
        print(f"[ERROR] Streaming error: {e}")
        yield f"[Streaming error: {e}]"

