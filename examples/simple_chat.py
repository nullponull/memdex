#!/usr/bin/env python3
"""
Simplified chat example
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memdex import chat_with_memory, quick_chat


def main():
    print("Memdex Simple Chat Examples")
    print("=" * 50)

    index_file = "output/memory_index.json"
    if not os.path.exists(index_file):
        print("\nError: Run 'python examples/build_memory.py' first!")
        return

    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\nNote: Set GOOGLE_API_KEY/OPENAI_API_KEY for full LLM responses.")
        print("Without it, you'll only see raw context chunks.\n")

    print("\n1. Quick one-off query:")
    print("-" * 30)
    response = quick_chat(index_file, "How many qubits did the quantum computer achieve?", api_key=api_key)
    print(f"Response: {response}")

    print("\n\n2. Interactive chat session:")
    print("-" * 30)
    chat_with_memory(index_file, api_key=api_key)


if __name__ == "__main__":
    main()
