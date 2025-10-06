import os
from pathlib import Path

# -----------------------
# Paths
# -----------------------
# /app inside the container
BASE_DIR   = Path(__file__).parent
DATA_DIR   = BASE_DIR / "chroma_db"   # Chroma persistence dir
CORPUS_DIR = BASE_DIR / "corpus"      # Put your docs here inside the container

# -----------------------
# Fast Mode (env-guarded optimization)
# -----------------------
FAST_MODE = os.getenv("FAST_MODE", "0") == "1"

# -----------------------
# Embeddings
# -----------------------
# Use SAME model in ingest.py and retrieval.py
# In Fast Mode, use a smaller/faster model
if FAST_MODE:
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
else:
    EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"   # 384-dim, fast & accurate

# -----------------------
# Chunking
# -----------------------
# Smaller chunks + overlap = better chance that headings stay with bullets
# In Fast Mode, use even smaller chunks for speed
if FAST_MODE:
    CHUNK_SIZE = 750
    CHUNK_OVERLAP = 100
else:
    CHUNK_SIZE = 600
    CHUNK_OVERLAP = 120

# -----------------------
# Retrieval
# -----------------------
# In Fast Mode, retrieve fewer chunks for speed
if FAST_MODE:
    TOP_K = 3
    MAX_CONTEXT_CHARS = 8000
else:
    TOP_K = 8
    MAX_CONTEXT_CHARS = None  # no limit

BM25_WEIGHT  = 0.6      # boost for keyword overlap during re-rank (0..1)
HYDE         = False    # keep off until everything is stable
MULTI_QUERY  = False    # re-enable later for recall

# -----------------------
# LLM (Ollama)
# -----------------------
# docker-compose.yml sets OLLAMA_HOST to http://ollama:11434
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
OLLAMA_HOST  = os.getenv("OLLAMA_URL", os.getenv("OLLAMA_HOST", "http://ollama:11434"))

# Generation controls (balanced for quality and speed)
MAX_TOKENS   = int(os.getenv("NUM_PREDICT", "800"))
TEMPERATURE  = float(os.getenv("TEMP", "0.3"))

# Concurrency control for Fast Mode pilot
MAX_ACTIVE_GENERATIONS = int(os.getenv("MAX_ACTIVE_GENERATIONS", "1"))


