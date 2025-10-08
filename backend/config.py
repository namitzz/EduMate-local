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
# Enable Fast Mode by default for better performance
FAST_MODE = os.getenv("FAST_MODE", "1") == "1"

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
# Optimized chunks for better retrieval and faster processing
# In Fast Mode, use smaller chunks for speed
if FAST_MODE:
    CHUNK_SIZE = 600  # Smaller for faster embedding and retrieval
    CHUNK_OVERLAP = 80
else:
    CHUNK_SIZE = 600
    CHUNK_OVERLAP = 120

# -----------------------
# Retrieval
# -----------------------
# In Fast Mode, retrieve fewer chunks for speed
if FAST_MODE:
    TOP_K = 3  # Fewer chunks for faster processing
    MAX_CONTEXT_CHARS = 6000  # Reduced for faster LLM processing
else:
    TOP_K = 8
    MAX_CONTEXT_CHARS = None  # no limit

BM25_WEIGHT  = 0.7      # Increased boost for keyword overlap (fuzzy matching enhanced)
HYDE         = False    # keep off until everything is stable
MULTI_QUERY  = False    # re-enable later for recall

# -----------------------
# LLM (Ollama)
# -----------------------
# OLLAMA_HOST Configuration Guide:
# 
# 1. LOCAL DEVELOPMENT (non-Docker):
#    - Use: http://localhost:11434
#    - Ollama must be running on your local machine
#    - Default if no environment variable is set
#
# 2. DOCKER DEPLOYMENTS:
#    - Use: http://ollama:11434
#    - Set in docker-compose.yml (container-to-container communication)
#    - The 'ollama' hostname resolves to the Ollama container
#
# 3. CLOUD/PUBLIC API DEPLOYMENTS (Fly.io, Streamlit Cloud, etc.):
#    - Use: Your assigned public Ollama API endpoint
#    - Examples: https://api.ollama.ai, https://your-ollama-instance.com
#    - Set OLLAMA_HOST or OLLAMA_URL environment variable to the public endpoint
#    - Do NOT use localhost in cloud deployments - it won't work
#    - May require API key authentication (check your provider's documentation)
#
# The code tries OLLAMA_URL first (used in .env.example), then OLLAMA_HOST,
# then defaults to http://localhost:11434 for local development convenience.

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")

OLLAMA_HOST = os.getenv("OLLAMA_URL", os.getenv("OLLAMA_HOST", "http://localhost:11434"))

# Validate OLLAMA_HOST is not empty
if not OLLAMA_HOST:
    raise ValueError("OLLAMA_HOST must be set. Set OLLAMA_HOST or OLLAMA_URL environment variable.")

# Generation controls (balanced for quality and speed)
# Reduced to 400 for faster responses (4-6 seconds target)
MAX_TOKENS   = int(os.getenv("NUM_PREDICT", "400"))
TEMPERATURE  = float(os.getenv("TEMP", "0.3"))

# Concurrency control for Fast Mode pilot
MAX_ACTIVE_GENERATIONS = int(os.getenv("MAX_ACTIVE_GENERATIONS", "1"))


