# Memdex — Lightweight, Serverless AI Memory 🧠

**A local semantic-search memory for AI. No vector database, no server, no cloud costs — just a portable index file.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

Memdex turns a pile of documents into a single, portable semantic-search index. It embeds your text with `sentence-transformers`, stores the vectors in a FAISS index and the chunk text alongside them, and answers natural-language queries in milliseconds — entirely on your machine. Copy the index files anywhere and they just work, online or offline.

> **History:** Memdex began as a fork of [memvid](https://github.com/olow304/memvid), which stored chunks as QR codes inside an MP4 video and decoded frames at query time. In practice the video layer added latency, fragility, and storage overhead without providing the speed or portability benefits — those came entirely from the search index. Memdex keeps the good part (a single portable index) and drops the video machinery. See [Why the video was removed](#why-the-video-was-removed).

## ✨ Features

- **Serverless** — no database to run, no Pinecone/Zilliz bill. Just `pip install` and go.
- **Portable** — your knowledge base is two files (`*_index.json` + `*_index.faiss`) you can copy, version, or back up.
- **Fast** — retrieval is the cost of the FAISS search alone; chunk text is read straight from memory.
- **Offline-first** — once the embedding model is cached, everything runs locally.
- **Simple API** — build an index and query it in a few lines.
- **Pluggable LLMs** — optional chat layer works with OpenAI, Google, or Anthropic.
- **Document support** — plain text, PDF, and EPUB ingestion.

## 📦 Installation

```bash
pip install memdex                 # core
pip install "memdex[pdf]"          # + PDF ingestion
pip install "memdex[epub]"         # + EPUB ingestion
pip install "memdex[llm]"          # + OpenAI / Google / Anthropic chat
```

## 🚀 Quick Start

```python
from memdex import MemdexEncoder, MemdexRetriever

# 1. Build an index
encoder = MemdexEncoder()
encoder.add_chunks([
    "The Eiffel Tower is located in Paris, France.",
    "Python is a popular language for machine learning.",
    "Sushi is a traditional Japanese dish made with vinegared rice.",
])
encoder.build_index("memory_index.json")   # writes memory_index.json + memory_index.faiss

# 2. Search it
retriever = MemdexRetriever("memory_index.json")
for chunk in retriever.search("Japanese food", top_k=3):
    print(chunk)
```

### Build from documents

```python
from memdex import MemdexEncoder
import os

encoder = MemdexEncoder()
for name in os.listdir("documents"):
    path = os.path.join("documents", name)
    if name.endswith(".pdf"):
        encoder.add_pdf(path)
    elif name.endswith(".epub"):
        encoder.add_epub(path)
    else:
        with open(path, encoding="utf-8") as f:
            encoder.add_text(f.read())

encoder.build_index("knowledge_index.json")
```

### Search with scores and metadata

```python
retriever = MemdexRetriever("knowledge_index.json")
for hit in retriever.search_with_metadata("neural networks", top_k=5):
    print(f"{hit['score']:.3f}  {hit['text'][:80]}")
```

### Chat with your memory (optional LLM layer)

```python
from memdex import MemdexChat

chat = MemdexChat("knowledge_index.json", llm_provider="google")  # or "openai"/"anthropic"
print(chat.chat("What does the knowledge base say about transformers?"))
```

Set the relevant API key first, e.g. `export GOOGLE_API_KEY=...`. Without a key, the chat layer returns the retrieved context only.

### Chat with your own files from the CLI

```bash
python examples/file_chat.py --input-dir ./documents --provider google
python examples/file_chat.py --files report.pdf notes.txt --chunk-size 2048
python examples/file_chat.py --load-existing output/memory_20250101_index.json
```

## 🧩 How it works

```
Text / PDF / EPUB
   → chunk_text()                      # overlapping chunks
   → sentence-transformers embeddings  # vectors
   → FAISS index (+ chunk text in metadata)
   → *_index.json  +  *_index.faiss    # one portable index

Query → embed → FAISS search → return chunk text from the index
```

At query time there is no frame extraction, no image decoding, and no network call — the matching chunk text is already in the index metadata held in memory.

## Why the video was removed

The original project's headline benefits (zero infrastructure, file-based portability, offline use, no monthly cost) all came from the search index. The full chunk text was already stored in the index metadata, so the QR-in-video layer was never actually on the critical path for retrieval. Removing it:

- **drops latency** — measured chunk retrieval went from ~840 ms (decode a video frame and read its QR) to well under 1 ms (read from the in-memory index);
- **removes fragility** — no dependence on video codecs, frame resolution, or OpenCV's QR detector (which silently failed to decode high-version QR codes on recent OpenCV builds);
- **shrinks dependencies** — no `opencv`, `qrcode`, `ffmpeg`, or Docker;
- **shrinks storage** — encoding text → QR image → compressed video is far larger than the text itself.

## ⚖️ When to use Memdex (and when not to)

**Good fit:** personal notes, research papers, documentation, and small-to-medium knowledge bases (thousands to low hundreds of thousands of chunks) where you want a zero-ops, copy-anywhere semantic search.

**Not a good fit:** very large corpora (millions of chunks / multi-GB text). Memdex loads chunk text into memory, so at that scale a purpose-built store (LanceDB, SQLite + a vector extension, or a hosted vector DB) is the right tool.

Conceptually Memdex is close to a minimal local vector store like Chroma; its distinguishing goal is to stay tiny, dependency-light, and contained in a single portable index.

## 🧪 Development

```bash
pip install -e ".[dev,pdf,llm]"
pytest tests/
black memdex/
```

## 📄 License

MIT — see [LICENSE](LICENSE).

## 🙏 Acknowledgments

Memdex is derived from [memvid](https://github.com/olow304/memvid) by Olow304 and contributors. Built with [sentence-transformers](https://www.sbert.net/) and [FAISS](https://github.com/facebookresearch/faiss).
