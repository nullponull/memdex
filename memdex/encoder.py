"""
MemdexEncoder - Chunk documents and build a portable semantic-search index
"""

import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

import numpy as np

from .utils import chunk_text
from .index import IndexManager
from .config import get_default_config, DEFAULT_CHUNK_SIZE, DEFAULT_OVERLAP

logger = logging.getLogger(__name__)


class MemdexEncoder:
    """
    Builds a semantic-search index from text, PDF and EPUB sources.

    The output is a single portable index (a ``<name>.json`` metadata file
    plus a ``<name>.faiss`` vector file) that stores both the embeddings and
    the full chunk text, so retrieval needs no external services.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or get_default_config()
        self.chunks = []
        self.index_manager = IndexManager(self.config)

    def add_chunks(self, chunks: List[str]):
        """Add text chunks to be indexed"""
        self.chunks.extend(chunks)
        logger.info(f"Added {len(chunks)} chunks. Total: {len(self.chunks)}")

    def add_text(self, text: str, chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_OVERLAP):
        """Add text and automatically chunk it"""
        chunks = chunk_text(text, chunk_size, overlap)
        self.add_chunks(chunks)

    def add_pdf(self, pdf_path: str, chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_OVERLAP):
        """Extract text from PDF and add as chunks"""
        try:
            import PyPDF2
        except ImportError:
            raise ImportError("PyPDF2 is required for PDF support. Install with: pip install PyPDF2")

        if not Path(pdf_path).exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            logger.info(f"Extracting text from {num_pages} pages of {Path(pdf_path).name}")
            for page_num in range(num_pages):
                page_text = pdf_reader.pages[page_num].extract_text()
                text += page_text + "\n\n"

        if text.strip():
            self.add_text(text, chunk_size, overlap)
            logger.info(f"Added PDF content: {len(text)} characters from {Path(pdf_path).name}")
        else:
            logger.warning(f"No text extracted from PDF: {pdf_path}")

    def add_epub(self, epub_path: str, chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_OVERLAP):
        """Extract text from EPUB and add as chunks"""
        try:
            import ebooklib
            from ebooklib import epub
            from bs4 import BeautifulSoup
        except ImportError:
            raise ImportError(
                "ebooklib and beautifulsoup4 are required for EPUB support. "
                "Install with: pip install ebooklib beautifulsoup4"
            )

        if not Path(epub_path).exists():
            raise FileNotFoundError(f"EPUB file not found: {epub_path}")

        book = epub.read_epub(epub_path)
        text_content = []
        logger.info(f"Extracting text from EPUB: {Path(epub_path).name}")

        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                for script in soup(["script", "style"]):
                    script.decompose()
                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                parts = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(part for part in parts if part)
                if text.strip():
                    text_content.append(text)

        full_text = "\n\n".join(text_content)
        if full_text.strip():
            self.add_text(full_text, chunk_size, overlap)
            logger.info(f"Added EPUB content: {len(full_text)} characters from {Path(epub_path).name}")
        else:
            logger.warning(f"No text extracted from EPUB: {epub_path}")

    def build_index(self, index_file: str, show_progress: bool = True) -> Dict[str, Any]:
        """
        Embed all chunks and write the portable search index to disk.

        Args:
            index_file: Output path for the index, e.g. "memory_index.json".
                A sibling "<name>.faiss" vector file is written alongside it.
            show_progress: Whether to log progress while embedding.

        Returns:
            Dictionary with build statistics.
        """
        if not self.chunks:
            raise ValueError("No chunks to index. Add content with add_text/add_pdf/add_chunks first.")

        index_path = Path(index_file)
        index_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Building index for {len(self.chunks)} chunks")

        frame_numbers = list(range(len(self.chunks)))
        self.index_manager.add_chunks(self.chunks, frame_numbers, show_progress)

        # IndexManager.save() appends its own suffixes to the stem
        self.index_manager.save(str(index_path.with_suffix('')))

        stats = {
            "total_chunks": len(self.chunks),
            "total_characters": sum(len(chunk) for chunk in self.chunks),
            "index_file": str(index_path),
            "index_stats": self.index_manager.get_stats(),
        }
        logger.info(f"Index built: {stats['total_chunks']} chunks -> {index_file}")
        return stats

    def clear(self):
        """Clear all chunks"""
        self.chunks = []
        self.index_manager = IndexManager(self.config)
        logger.info("Cleared all chunks")

    def get_stats(self) -> Dict[str, Any]:
        """Get encoder statistics"""
        return {
            "total_chunks": len(self.chunks),
            "total_characters": sum(len(chunk) for chunk in self.chunks),
            "avg_chunk_size": float(np.mean([len(chunk) for chunk in self.chunks])) if self.chunks else 0,
            "config": self.config,
        }

    @classmethod
    def from_file(cls, file_path: str, chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_OVERLAP,
                  config: Optional[Dict[str, Any]] = None) -> 'MemdexEncoder':
        """Create encoder from text file"""
        encoder = cls(config)
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        encoder.add_text(text, chunk_size, overlap)
        return encoder

    @classmethod
    def from_documents(cls, documents: List[str], chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_OVERLAP,
                       config: Optional[Dict[str, Any]] = None) -> 'MemdexEncoder':
        """Create encoder from list of documents"""
        encoder = cls(config)
        for doc in documents:
            encoder.add_text(doc, chunk_size, overlap)
        return encoder
