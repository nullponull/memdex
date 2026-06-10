# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Memdex is a lightweight, serverless Python library for AI memory. It builds a
portable semantic-search index from documents and answers natural-language
queries locally — no vector database server and no cloud dependency.

It is derived from the `memvid` project but removes the QR-code-in-video storage
layer; see README "Why the video was removed".

## Key Architecture

### Core Components
- **MemdexEncoder** (memdex/encoder.py): Text/PDF/EPUB chunking and index building via `build_index()`
- **MemdexRetriever** (memdex/retriever.py): Semantic search returning chunk text from the index
- **MemdexChat** (memdex/chat.py): Conversation management and LLM interface
- **IndexManager** (memdex/index.py): Embedding generation, FAISS storage, and vector search
- **utils.py**: `chunk_text` plus index file I/O
- **llm_client.py**: Pluggable OpenAI / Google / Anthropic client

### Data Flow
1. Text/PDF/EPUB → chunks → embeddings → FAISS index (chunk text stored in metadata)
2. Query → embedding → FAISS search → chunk text returned directly from the index
3. Context + history → LLM → response

The index is two files: `<name>_index.json` (metadata + chunk text) and
`<name>_index.faiss` (vectors). No video, image, or QR artifacts are produced.

## Development Commands

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,pdf,llm]"
pytest tests/
pytest tests/test_encoder.py::test_build_index
black memdex/
```

## Key Dependencies
- sentence-transformers: semantic embeddings
- faiss-cpu: vector search
- numpy, tqdm
- Optional: PyPDF2 (pdf), ebooklib + beautifulsoup4 (epub), openai/google-generativeai/anthropic (llm)

## Implementation Notes
- Chunk text lives in the index metadata and is loaded in memory, so retrieval
  needs no external services. This suits small-to-medium corpora; multi-GB text
  should use a purpose-built store.
- The LLM backend is pluggable (OpenAI, Anthropic, Google).
