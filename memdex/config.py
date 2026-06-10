"""
Configuration defaults and constants for Memdex
"""

from typing import Dict, Any

# Chunking settings
DEFAULT_CHUNK_SIZE = 1024
DEFAULT_OVERLAP = 32

# Retrieval settings
DEFAULT_TOP_K = 5
BATCH_SIZE = 100

# Embedding settings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Fast and good quality
EMBEDDING_DIMENSION = 384

# Index settings
INDEX_TYPE = "Flat"  # Can be "IVF" for larger datasets, otherwise use Flat
NLIST = 100  # Number of clusters for IVF index

# LLM settings
DEFAULT_LLM_PROVIDER = "google"  # google, openai, anthropic
DEFAULT_LLM_MODELS = {
    "google": "gemini-2.0-flash-exp",
    "openai": "gpt-4o",
    "anthropic": "claude-3-5-sonnet-20241022"
}

MAX_TOKENS = 8192
TEMPERATURE = 0.1
CONTEXT_WINDOW = 32000

# Chat settings
MAX_HISTORY_LENGTH = 10
CONTEXT_CHUNKS_PER_QUERY = 5


def get_default_config() -> Dict[str, Any]:
    """Get default configuration dictionary"""
    return {
        "chunking": {
            "chunk_size": DEFAULT_CHUNK_SIZE,
            "overlap": DEFAULT_OVERLAP,
        },
        "retrieval": {
            "top_k": DEFAULT_TOP_K,
            "batch_size": BATCH_SIZE,
        },
        "embedding": {
            "model": EMBEDDING_MODEL,
            "dimension": EMBEDDING_DIMENSION,
        },
        "index": {
            "type": INDEX_TYPE,
            "nlist": NLIST,
        },
        "llm": {
            "model": DEFAULT_LLM_MODELS[DEFAULT_LLM_PROVIDER],
            "max_tokens": MAX_TOKENS,
            "temperature": TEMPERATURE,
            "context_window": CONTEXT_WINDOW,
        },
        "chat": {
            "max_history": MAX_HISTORY_LENGTH,
            "context_chunks": CONTEXT_CHUNKS_PER_QUERY,
        },
    }
