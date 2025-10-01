from pathlib import Path

# -----------------------
# Paths
# -----------------------
# /app inside the container
BASE_DIR   = Path(__file__).parent
DATA_DIR   = BASE_DIR / "chroma_db"   # Chroma persistence dir
CORPUS_DIR = BASE_DIR / "corpus"      # Put your docs here inside the container

# -----------------------
# Embeddings
# -----------------------
# Use SAME model in ingest.py and retrieval.py
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"   # 384-dim, fast & accurate

# -----------------------
# Chunking
# -----------------------
# Smaller chunks + overlap = better chance that headings stay with bullets
CHUNK_SIZE    = 600
CHUNK_OVERLAP = 120

# -----------------------
# Retrieval
# -----------------------
TOP_K        = 8        # how many chunks to retrieve
BM25_WEIGHT  = 0.6      # boost for keyword overlap during re-rank (0..1)
HYDE         = False    # keep off until everything is stable
MULTI_QUERY  = False    # re-enable later for recall

# -----------------------
# LLM (Ollama)
# -----------------------
# docker-compose.yml sets OLLAMA_HOST to http://ollama:11434
OLLAMA_MODEL = "mistral"     # <- switch here
OLLAMA_HOST  = "http://localhost:11434"  # default for local non-Docker setup

# Generation controls (balanced for quality and speed)
MAX_TOKENS   = 800  # Increased from 320 to allow complete answers
TEMPERATURE  = 0.3  # Slightly increased for more natural responses


