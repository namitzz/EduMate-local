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
# LLM Provider Configuration - OpenRouter Only
# -----------------------
# This app is configured for cloud deployment using OpenRouter API
# No local LLM setup required - zero-cost deployment ready
#
# Set OPENROUTER_API_KEY environment variable with your API key
# Get free credits at: https://openrouter.ai/
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
if not OPENROUTER_API_KEY:
    raise ValueError(
        "OPENROUTER_API_KEY environment variable is required. "
        "Get your free API key at https://openrouter.ai/"
    )

OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")
OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL", "")  # optional: your site/app URL
OPENROUTER_APP_NAME = os.getenv("OPENROUTER_APP_NAME", "EduMate")

# Generation controls (balanced for quality and speed)
# Reduced to 400 for faster responses (4-6 seconds target)
MAX_TOKENS   = int(os.getenv("NUM_PREDICT", "400"))
TEMPERATURE  = float(os.getenv("TEMP", "0.3"))

# Concurrency control for Fast Mode pilot
MAX_ACTIVE_GENERATIONS = int(os.getenv("MAX_ACTIVE_GENERATIONS", "1"))

# -----------------------
# Conversation Memory Configuration
# -----------------------
# Maximum number of conversation turns to retain per session
MAX_CONVERSATION_HISTORY = int(os.getenv("MAX_CONVERSATION_HISTORY", "10"))

# Enable conversation memory for context-aware responses
ENABLE_CONVERSATION_MEMORY = os.getenv("ENABLE_CONVERSATION_MEMORY", "1") == "1"
