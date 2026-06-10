"""
Tests for MemdexRetriever
"""

import os
import tempfile

import pytest

from memdex import MemdexEncoder, MemdexRetriever


@pytest.fixture
def setup_test_memory():
    """Create a test index and yield its path"""
    encoder = MemdexEncoder()
    chunks = [
        "Quantum computing uses qubits for parallel processing",
        "Machine learning models require large datasets",
        "Neural networks mimic brain structure",
        "Cloud computing provides scalable resources",
        "Blockchain ensures data immutability",
    ]
    encoder.add_chunks(chunks)

    with tempfile.TemporaryDirectory() as temp_dir:
        index_file = os.path.join(temp_dir, "test_index.json")
        encoder.build_index(index_file, show_progress=False)
        yield index_file, chunks


def test_retriever_initialization(setup_test_memory):
    index_file, chunks = setup_test_memory
    retriever = MemdexRetriever(index_file)
    assert retriever.get_stats()["index_stats"]["total_chunks"] == len(chunks)


def test_search(setup_test_memory):
    index_file, chunks = setup_test_memory
    retriever = MemdexRetriever(index_file)

    results = retriever.search("quantum physics", top_k=3)
    assert len(results) <= 3
    assert any("quantum" in result.lower() for result in results)

    results = retriever.search("artificial intelligence", top_k=3)
    assert len(results) <= 3
    assert any("neural" in r.lower() or "machine" in r.lower() for r in results)


def test_search_with_metadata(setup_test_memory):
    index_file, chunks = setup_test_memory
    retriever = MemdexRetriever(index_file)

    results = retriever.search_with_metadata("blockchain", top_k=2)
    assert len(results) <= 2
    if results:
        result = results[0]
        assert "text" in result
        assert "score" in result
        assert "chunk_id" in result
        assert result["score"] > 0


def test_get_chunk_by_id(setup_test_memory):
    index_file, chunks = setup_test_memory
    retriever = MemdexRetriever(index_file)

    chunk = retriever.get_chunk_by_id(0)
    assert chunk is not None
    assert "quantum" in chunk.lower()

    assert retriever.get_chunk_by_id(999) is None


def test_get_context_window(setup_test_memory):
    index_file, chunks = setup_test_memory
    retriever = MemdexRetriever(index_file)

    window = retriever.get_context_window(2, window_size=1)
    # chunks 1, 2, 3 -> 3 results
    assert len(window) == 3


def test_retriever_stats(setup_test_memory):
    index_file, chunks = setup_test_memory
    retriever = MemdexRetriever(index_file)

    stats = retriever.get_stats()
    assert "index_file" in stats
    assert stats["index_stats"]["total_chunks"] == len(chunks)
