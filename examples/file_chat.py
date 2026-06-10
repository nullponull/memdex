#!/usr/bin/env python3
"""
file_chat.py - Build a Memdex index from your own files and chat with it

Usage:
    python file_chat.py --input-dir /path/to/documents --provider google
    python file_chat.py --files file1.txt file2.pdf --provider openai --chunk-size 2048
    python file_chat.py --load-existing output/my_memory_index.json --provider google
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memdex import MemdexEncoder, MemdexChat

SUPPORTED_TEXT = {".txt", ".md"}


def collect_files(input_dir, files):
    paths = []
    if input_dir:
        for p in Path(input_dir).rglob("*"):
            if p.suffix.lower() in SUPPORTED_TEXT or p.suffix.lower() in {".pdf", ".epub"}:
                paths.append(p)
    if files:
        paths.extend(Path(f) for f in files)
    return paths


def build(paths, chunk_size, overlap):
    encoder = MemdexEncoder()
    for p in paths:
        ext = p.suffix.lower()
        try:
            if ext == ".pdf":
                encoder.add_pdf(str(p), chunk_size=chunk_size, overlap=overlap)
            elif ext == ".epub":
                encoder.add_epub(str(p), chunk_size=chunk_size, overlap=overlap)
            else:
                encoder.add_text(p.read_text(encoding="utf-8"), chunk_size=chunk_size, overlap=overlap)
            print(f"  added {p.name}")
        except Exception as e:
            print(f"  skipped {p.name}: {e}")

    os.makedirs("output", exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    index_file = f"output/memory_{stamp}_index.json"
    stats = encoder.build_index(index_file)
    print(f"Index built with {stats['total_chunks']} chunks -> {index_file}")
    return index_file


def main():
    parser = argparse.ArgumentParser(description="Build a Memdex index and chat with it")
    parser.add_argument("--input-dir", help="Directory of documents to index")
    parser.add_argument("--files", nargs="+", help="Specific files to index")
    parser.add_argument("--load-existing", help="Path to an existing *_index.json to load")
    parser.add_argument("--provider", default="google", choices=["google", "openai", "anthropic"])
    parser.add_argument("--chunk-size", type=int, default=1024)
    parser.add_argument("--overlap", type=int, default=32)
    args = parser.parse_args()

    if args.load_existing:
        index_file = args.load_existing
        if not os.path.exists(index_file):
            print(f"Error: index not found: {index_file}")
            return
    else:
        paths = collect_files(args.input_dir, args.files)
        if not paths:
            print("Error: no input files. Use --input-dir or --files.")
            return
        print(f"Indexing {len(paths)} file(s)...")
        index_file = build(paths, args.chunk_size, args.overlap)

    chat = MemdexChat(index_file, llm_provider=args.provider)
    chat.interactive_chat()


if __name__ == "__main__":
    main()
