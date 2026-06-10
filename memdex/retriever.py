"""
MemdexRetriever - Fast semantic search over a portable index

Chunk text is stored in the index metadata and loaded in memory, so retrieval
is the cost of the FAISS semantic search alone - no external services, no
video frame extraction, no QR decoding.
"""

import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

from .index import IndexManager
from .config import get_default_config

logger = logging.getLogger(__name__)


class MemdexRetriever:
    """Fast retrieval from a Memdex index using semantic search"""

    def __init__(self, index_file: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize MemdexRetriever

        Args:
            index_file: Path to the index file (e.g. "memory_index.json")
            config: Optional configuration
        """
        self.index_file = str(Path(index_file).absolute())
        self.config = config or get_default_config()

        # Load index (IndexManager appends its own suffixes to the stem)
        self.index_manager = IndexManager(self.config)
        self.index_manager.load(str(Path(index_file).with_suffix('')))

        logger.info(
            f"Initialized retriever with "
            f"{self.index_manager.get_stats()['total_chunks']} chunks"
        )

    def search(self, query: str, top_k: int = 5) -> List[str]:
        """
        Search for relevant chunks using semantic search.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of relevant text chunks
        """
        start_time = time.time()

        search_results = self.index_manager.search(query, top_k)
        results = [metadata["text"] for _, _, metadata in search_results]

        elapsed = time.time() - start_time
        logger.info(f"Search completed in {elapsed:.4f}s for query: '{query[:50]}...'")
        return results

    def search_with_metadata(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search and return results with scores and metadata.

        Args:
            query: Search query
            top_k: Number of results

        Returns:
            List of dicts with text, score, chunk_id and metadata
        """
        start_time = time.time()

        search_results = self.index_manager.search(query, top_k)

        results = []
        for chunk_id, distance, metadata in search_results:
            results.append({
                "text": metadata["text"],
                "score": 1.0 / (1.0 + distance),  # Convert distance to similarity
                "chunk_id": chunk_id,
                "metadata": metadata,
            })

        elapsed = time.time() - start_time
        logger.info(f"Search with metadata completed in {elapsed:.4f}s")
        return results

    def get_chunk_by_id(self, chunk_id: int) -> Optional[str]:
        """
        Get a specific chunk's text by ID.

        Args:
            chunk_id: Chunk ID

        Returns:
            Chunk text or None
        """
        metadata = self.index_manager.get_chunk_by_id(chunk_id)
        return metadata["text"] if metadata else None

    def get_context_window(self, chunk_id: int, window_size: int = 2) -> List[str]:
        """
        Get a chunk together with its surrounding chunks.

        Args:
            chunk_id: Central chunk ID
            window_size: Number of chunks before/after to include

        Returns:
            List of chunk texts in the context window
        """
        chunks = []
        for offset in range(-window_size, window_size + 1):
            chunk = self.get_chunk_by_id(chunk_id + offset)
            if chunk:
                chunks.append(chunk)
        return chunks

    def get_stats(self) -> Dict[str, Any]:
        """Get retriever statistics"""
        return {
            "index_file": self.index_file,
            "index_stats": self.index_manager.get_stats(),
        }
