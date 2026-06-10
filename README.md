# Memdex — A document memory you can `git commit`, wired straight into Claude 🧠

**Lightweight, serverless semantic search for your documents. One portable index file, zero infrastructure, and a built-in [MCP](https://modelcontextprotocol.io) server so Claude Desktop / Claude Code can search your notes on demand.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

Memdex turns a pile of documents into a single, portable semantic-search index — two files you can copy, version-control, and carry offline. Then it hands that index to your AI assistant through MCP, so the assistant can pull the right passage out of *your* documents without a database, a server, or a cloud bill.

```python
from memdex import MemdexEncoder, MemdexRetriever

MemdexEncoder.from_documents(open("notes.md").read().split("\n\n")).build_index("notes_index.json")

for hit in MemdexRetriever("notes_index.json").search("what did I decide about the API redesign?"):
    print(hit)
```

> **Heads up — honest scope:** Memdex is a thin, friendly wrapper around `sentence-transformers` + FAISS. It is **not** faster or smarter than a mature vector store like Chroma or LanceDB, and it is **not** for million-chunk corpora. Its whole reason to exist is ergonomics: a single committable file, near-zero dependencies, full offline use, and first-class MCP. If that combination fits, it's lovely. If you need scale or rich filtering, use Chroma/LanceDB — see [the honest comparison](#-honest-comparison) below.

## 🎯 Why you might want this

- **Your memory is one file.** `notes_index.json` + `notes_index.faiss`. Commit it, diff it, drop it in a Gist, sync it in Dropbox. No server to run, nothing to "spin up."
- **Claude can search it directly.** The bundled MCP server exposes a `search_memory` tool, so Claude Desktop / Claude Code can answer "what do my docs say about X?" against your private content.
- **Truly offline.** After the embedding model is cached once, everything runs locally. Good for air-gapped, private, or just-on-a-plane work.
- **Tiny.** Core install is `sentence-transformers` + `faiss-cpu`. No opencv, no ffmpeg, no Docker.

## 📦 Install

```bash
pip install memdex                 # core: build + search
pip install "memdex[mcp]"          # + MCP server for Claude
pip install "memdex[pdf,epub]"     # + PDF / EPUB ingestion
pip install "memdex[llm]"          # + optional chat layer (OpenAI/Google/Anthropic)
```

## 🚀 60-second quickstart

**1. Build an index from your documents**

```python
from memdex import MemdexEncoder

enc = MemdexEncoder()
enc.add_pdf("handbook.pdf")          # or add_text(...) / add_epub(...) / add_chunks([...])
enc.build_index("memory_index.json") # writes memory_index.json + memory_index.faiss
```

**2. Search it (no LLM needed)**

```python
from memdex import MemdexRetriever

r = MemdexRetriever("memory_index.json")
for hit in r.search("vacation policy", top_k=3):
    print(hit)
```

That's the whole library. Everything else is convenience on top.

## 🔌 Use it from Claude (MCP)

This is the part that makes Memdex feel different day-to-day: let Claude search your documents itself.

**1. Build an index** (as above), then **2. register the MCP server** with your client.

**Claude Desktop** — add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "memdex": {
      "command": "memdex-mcp",
      "args": ["/absolute/path/to/memory_index.json"]
    }
  }
}
```

**Claude Code** — register it as a stdio server:

```bash
claude mcp add memdex -- memdex-mcp /absolute/path/to/memory_index.json
```

Now ask Claude things like *"search my memory for what we decided about retries"* and it will call `search_memory` against your index. The server exposes two tools:

| Tool | What it does |
|------|--------------|
| `search_memory(query, top_k=5)` | Returns the most relevant chunks with similarity scores |
| `memory_stats()` | Reports the index path and chunk count |

You can also point the server at an index with an environment variable instead of an argument: `MEMDEX_INDEX=/path/to/memory_index.json memdex-mcp`.

## 🧩 How it works

```
Text / PDF / EPUB
   → chunk_text()                          # overlapping chunks
   → sentence-transformers embeddings
   → FAISS index (+ chunk text in metadata)
   → memory_index.json + memory_index.faiss   # one portable index

Query → embed → FAISS search → return chunk text (already in memory)
```

There's no magic and no novel algorithm here — that's the point. The value is the packaging: a committable file and an MCP plug.

## ⚖️ Honest comparison

| | **Memdex** | **Chroma / LanceDB** | **Hosted vector DB** (Pinecone, …) |
|---|---|---|---|
| Setup | `pip install`, one file | `pip install`, embedded DB | account + API keys + network |
| Ops | none | none–light | managed service |
| Portability | **single committable index file** | DB directory | remote only |
| Offline | ✅ | ✅ | ❌ |
| MCP server included | ✅ | ✖️ (DIY) | ✖️ (DIY) |
| Metadata filtering | ✖️ (minimal) | ✅ | ✅ |
| Incremental updates | rebuild | ✅ | ✅ |
| Scale | thousands–~100k chunks | millions | billions |
| Speed | FAISS-flat (fine at small scale) | optimized indexes | optimized + distributed |

**Choose Memdex** for personal notes, docs, research libraries, or a private knowledge base you want to commit and hand to Claude with zero ops. **Choose Chroma/LanceDB** the moment you need filtering, incremental writes, or large scale. Memdex deliberately does less.

> Note on coding agents: **Claude Code searches code with agentic grep, not embeddings**, and deliberately avoids pre-built indexes. Memdex is for searching *documents/prose*, not for indexing a codebase you're editing.

## 📜 History

Memdex began as a fork of [memvid](https://github.com/olow304/memvid), which stored chunks as QR codes inside an MP4 and decoded video frames at query time. Measurement showed the video layer added latency and fragility while contributing nothing to retrieval — the chunk text was always in the search index. Memdex keeps the portable index, drops the video machinery, and adds the MCP server. (Retrieval went from ~840 ms decoding a video frame to <1 ms reading the index.)

## 🧪 Development

```bash
pip install -e ".[dev,pdf,mcp,llm]"
pytest tests/
black memdex/
```

## 📄 License

MIT — see [LICENSE](LICENSE). Derived from [memvid](https://github.com/olow304/memvid) by Olow304 and contributors. Built with [sentence-transformers](https://www.sbert.net/) and [FAISS](https://github.com/facebookresearch/faiss).
