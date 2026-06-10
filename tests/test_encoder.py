"""
Tests for MemdexEncoder
"""

import os
import tempfile

from memdex import MemdexEncoder


def test_encoder_initialization():
    encoder = MemdexEncoder()
    assert encoder.chunks == []
    assert encoder.index_manager is not None


def test_add_chunks():
    encoder = MemdexEncoder()
    chunks = ["chunk1", "chunk2", "chunk3"]
    encoder.add_chunks(chunks)
    assert len(encoder.chunks) == 3
    assert encoder.chunks == chunks


def test_add_text():
    encoder = MemdexEncoder()
    text = "This is a test. " * 50
    encoder.add_text(text, chunk_size=100, overlap=20)
    assert len(encoder.chunks) > 1
    assert all(chunk for chunk in encoder.chunks)


def test_build_index():
    encoder = MemdexEncoder()
    chunks = [
        "Test chunk 1: Important information",
        "Test chunk 2: More data here",
        "Test chunk 3: Final piece of info",
    ]
    encoder.add_chunks(chunks)

    with tempfile.TemporaryDirectory() as temp_dir:
        index_file = os.path.join(temp_dir, "test_index.json")
        stats = encoder.build_index(index_file, show_progress=False)

        assert os.path.exists(index_file)
        assert os.path.exists(index_file.replace(".json", ".faiss"))
        assert stats["total_chunks"] == 3

        # No video or QR artifacts should be produced anywhere
        leftovers = [f for f in os.listdir(temp_dir)
                     if f.endswith((".mp4", ".mkv", ".png")) or f.startswith("frame_")]
        assert leftovers == []


def test_encoder_stats():
    encoder = MemdexEncoder()
    chunks = ["short", "medium length chunk", "this is a longer chunk with more text"]
    encoder.add_chunks(chunks)

    stats = encoder.get_stats()
    assert stats["total_chunks"] == 3
    assert stats["total_characters"] == sum(len(c) for c in chunks)
    assert stats["avg_chunk_size"] > 0


def test_clear():
    encoder = MemdexEncoder()
    encoder.add_chunks(["test1", "test2"])
    encoder.clear()
    assert encoder.chunks == []
    assert encoder.get_stats()["total_chunks"] == 0
