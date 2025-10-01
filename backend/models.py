import os, requests, json, time
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
            print(f"[WARNING] Ollama returned empty response. Full data: {data}")
            raise RuntimeError("Empty response from Ollama")
        except (requests.ReadTimeout, requests.ConnectionError, requests.HTTPError, json.JSONDecodeError) as e:
            last_err = e
            time.sleep(2 + 2*attempt)  # backoff: 2s, 4s, 6s
    raise RuntimeError(f"Ollama call failed after retries: {last_err}")

