"""
Tests for the Memdex MCP server tools.

These exercise the tool functions directly (not over the wire); the FastMCP
stdio transport is covered by the SDK itself.
"""

import asyncio
import os
import tempfile

import pytest

from memdex import MemdexEncoder

pytest.importorskip("mcp")  # skip if the optional MCP extra isn't installed


@pytest.fixture
def index_path():
    encoder = MemdexEncoder()
    encoder.add_chunks([
        "The mitochondria is the powerhouse of the cell.",
        "Python uses indentation to define code blocks.",
        "Mount Fuji is the highest mountain in Japan.",
    ])
    with tempfile.TemporaryDirectory() as d:
        idx = os.path.join(d, "k_index.json")
        encoder.build_index(idx, show_progress=False)
        yield idx


def test_tools_registered(index_path):
    import memdex.mcp_server as srv
    srv._index_path = index_path
    srv._retriever = None
    tools = asyncio.run(srv.mcp.list_tools())
    names = {t.name for t in tools}
    assert {"search_memory", "memory_stats"} <= names


def test_search_memory(index_path):
    import memdex.mcp_server as srv
    srv._index_path = index_path
    srv._retriever = None
    results = srv.search_memory("tallest mountain in Japan", top_k=2)
    assert len(results) <= 2
    assert "text" in results[0] and "score" in results[0]
    assert "Fuji" in results[0]["text"]


def test_memory_stats(index_path):
    import memdex.mcp_server as srv
    srv._index_path = index_path
    srv._retriever = None
    stats = srv.memory_stats()
    assert stats["total_chunks"] == 3
    assert stats["index_file"].endswith("k_index.json")
