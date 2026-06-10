"""
Interactive chat interface for Memdex
"""

import os
import time
from typing import Optional, Dict, Any
from .chat import MemdexChat


def chat_with_memory(
    index_file: str,
    api_key: Optional[str] = None,
    llm_model: Optional[str] = None,
    llm_provider: str = "google",
    show_stats: bool = True,
    session_dir: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
):
    """
    Start an interactive chat session backed by a Memdex index.

    Args:
        index_file: Path to the index file (e.g. "memory_index.json")
        api_key: LLM API key (or set the provider's env var)
        llm_model: LLM model to use (uses provider default if None)
        llm_provider: LLM provider ('google', 'openai', 'anthropic')
        show_stats: Show index stats on startup
        session_dir: Directory to save exported conversations (default: "output")
        config: Optional configuration

    Commands:
        - 'search <query>': Show raw search results
        - 'stats': Show system statistics
        - 'clear': Clear conversation history
        - 'help': Show commands
        - 'exit' or 'quit': End session
    """
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'

    session_dir = session_dir or "output"
    os.makedirs(session_dir, exist_ok=True)

    if not os.path.exists(index_file):
        print(f"Error: Index file not found: {index_file}")
        return

    api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")

    print("Initializing Memdex Chat...")
    chat = MemdexChat(
        index_file,
        llm_provider=llm_provider,
        llm_model=llm_model,
        llm_api_key=api_key,
        config=config,
    )
    chat.start_session()

    if show_stats:
        stats = chat.get_stats()
        print(f"\nIndex loaded with {stats['index_file']}")
        if stats['llm_available']:
            print(f"LLM provider: {stats['llm_provider']}")
        else:
            print("LLM: Not available (context-only mode)")

    print("\nType 'help' for commands, 'exit' to quit")
    print("-" * 50)

    while True:
        try:
            user_input = input("\nYou: ").strip()
            if not user_input:
                continue

            lower_input = user_input.lower()

            if lower_input in ['exit', 'quit', 'q']:
                break

            elif lower_input == 'help':
                print("\nCommands:")
                print("  search <query> - Show raw search results")
                print("  stats          - Show system statistics")
                print("  clear          - Clear conversation history")
                print("  help           - Show this help")
                print("  exit/quit      - End session")
                continue

            elif lower_input == 'stats':
                stats = chat.get_stats()
                print(f"\nMessages exchanged: {stats['messages_exchanged']}")
                print(f"LLM provider: {stats['llm_provider']}")
                continue

            elif lower_input == 'clear':
                chat.clear_history()
                continue

            elif lower_input.startswith('search '):
                query = user_input[7:]
                print(f"\nSearching: '{query}'")
                start_time = time.time()
                results = chat.retriever.search_with_metadata(query, top_k=5)
                elapsed = time.time() - start_time
                print(f"Found {len(results)} results in {elapsed:.4f}s:\n")
                for i, result in enumerate(results[:3]):
                    print(f"{i+1}. [Score: {result['score']:.3f}] {result['text'][:100]}...")
                continue

            print("\nAssistant: ", end="", flush=True)
            start_time = time.time()
            response = chat.chat(user_input)
            elapsed = time.time() - start_time
            print(response)
            print(f"\n[{elapsed:.1f}s]", end="")

        except KeyboardInterrupt:
            print("\n\nInterrupted.")
            break
        except Exception as e:
            print(f"\nError: {e}")
            continue

    print("\nGoodbye!")


def quick_chat(index_file: str, query: str, api_key: Optional[str] = None,
               llm_provider: str = "google") -> str:
    """
    Quick one-off query without an interactive loop.

    Args:
        index_file: Path to the index file
        query: Question to ask
        api_key: LLM API key (optional)
        llm_provider: LLM provider

    Returns:
        Response string

    Example:
        >>> from memdex import quick_chat
        >>> response = quick_chat("knowledge_index.json", "What is quantum computing?")
        >>> print(response)
    """
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    chat = MemdexChat(index_file, llm_provider=llm_provider, llm_api_key=api_key)
    return chat.chat(query)
