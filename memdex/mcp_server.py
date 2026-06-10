"""
Memdex MCP server.

Exposes a Memdex index to MCP clients (Claude Desktop, Claude Code, Cursor, ...)
as a small set of tools, so an assistant can semantically search your private
documents on demand.

Run it directly:

    memdex-mcp /path/to/knowledge_index.json

or point an MCP client at it via stdio (see README for client config).
"""

import argparse
import os
import sys
from typing import List, Dict, Any, Optional

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:  # pragma: no cover - import guard with a helpful message
    sys.stderr.write(
        "The MCP server requires the 'mcp' package.\n"
        "Install it with:  pip install \"memdex[mcp]\"\n"
    )
    raise

from .retriever import MemdexRetriever

# The index path is resolved once, when the server process starts, from either
# the MEMDEX_INDEX environment variable or the first CLI argument.
_retriever: Optional[MemdexRetriever] = None
_index_path: Optional[str] = None

mcp = FastMCP("memdex")


def _get_retriever() -> MemdexRetriever:
    global _retriever
    if _retriever is None:
        if not _index_path:
            raise RuntimeError(
                "No Memdex index configured. Set MEMDEX_INDEX or pass the index "
                "path as the first argument to memdex-mcp."
            )
        _retriever = MemdexRetriever(_index_path)
    return _retriever


@mcp.tool()
def search_memory(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Semantically search the document memory and return the most relevant chunks.

    Args:
        query: A natural-language description of what to find.
        top_k: How many chunks to return (default 5).

    Returns:
        A list of {"text", "score"} objects, most relevant first.
    """
    retriever = _get_retriever()
    hits = retriever.search_with_metadata(query, top_k=top_k)
    return [{"text": h["text"], "score": round(h["score"], 4)} for h in hits]


@mcp.tool()
def memory_stats() -> Dict[str, Any]:
    """
    Report basic statistics about the loaded document memory (chunk count, etc.).
    """
    retriever = _get_retriever()
    stats = retriever.get_stats()
    return {
        "index_file": stats["index_file"],
        "total_chunks": stats["index_stats"].get("total_chunks"),
    }


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        description="Run the Memdex MCP server over stdio."
    )
    parser.add_argument(
        "index",
        nargs="?",
        default=os.getenv("MEMDEX_INDEX"),
        help="Path to a Memdex index (e.g. knowledge_index.json). "
        "Falls back to the MEMDEX_INDEX environment variable.",
    )
    args = parser.parse_args(argv)

    global _index_path
    _index_path = args.index
    if not _index_path:
        parser.error(
            "No index given. Pass a path or set MEMDEX_INDEX. "
            "Build one first with MemdexEncoder.build_index(...)."
        )

    # Fail fast with a clear message if the index can't be loaded, rather than
    # surfacing an opaque error on the first tool call.
    _get_retriever()

    mcp.run()  # stdio transport by default


if __name__ == "__main__":
    main()
