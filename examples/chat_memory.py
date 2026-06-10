#!/usr/bin/env python3
"""
Example: Interactive conversation using MemdexChat
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memdex import MemdexChat


def main():
    print("Memdex Example: Interactive Chat with Memory")
    print("=" * 50)

    index_file = "output/memory_index.json"
    if not os.path.exists(index_file):
        print("\nError: Memory index not found!")
        print("Please run 'python examples/build_memory.py' first.")
        return

    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("OPENAI_API_KEY")
    chat = MemdexChat(index_file, llm_api_key=api_key)
    chat.interactive_chat()


if __name__ == "__main__":
    main()
