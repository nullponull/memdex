#!/usr/bin/env python3
"""
Example: Build a Memdex index from text data
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memdex import MemdexEncoder


def main():
    chunks = [
        "The quantum computer achieved 100 qubits of processing power in March 2024.",
        "Machine learning models can now process over 1 trillion parameters efficiently.",
        "The new GPU architecture delivers 5x performance improvement for AI workloads.",
        "Cloud storage costs have decreased by 80% over the past five years.",
        "Quantum encryption methods are becoming standard for secure communications.",
        "Edge computing reduces latency to under 1ms for critical applications.",
        "Neural networks can now generate photorealistic images in real-time.",
        "Blockchain technology processes over 100,000 transactions per second.",
        "5G networks provide speeds up to 10 Gbps in urban areas.",
        "Autonomous vehicles have logged over 50 million miles of testing.",
    ]

    os.makedirs("output", exist_ok=True)
    index_file = "output/memory_index.json"

    encoder = MemdexEncoder()
    encoder.add_chunks(chunks)

    print(f"Building index from {len(chunks)} chunks...")
    start = time.time()
    stats = encoder.build_index(index_file)
    print(f"Done in {time.time() - start:.2f}s")
    print(f"Index written to: {index_file}")
    print(f"Total chunks: {stats['total_chunks']}")


if __name__ == "__main__":
    main()
