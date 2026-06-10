"""
Memdex - Lightweight, serverless semantic-search memory for AI
"""

__version__ = "0.1.0"

from .encoder import MemdexEncoder
from .retriever import MemdexRetriever
from .chat import MemdexChat
from .interactive import chat_with_memory, quick_chat
from .llm_client import LLMClient, create_llm_client

__all__ = [
    "MemdexEncoder",
    "MemdexRetriever",
    "MemdexChat",
    "chat_with_memory",
    "quick_chat",
    "LLMClient",
    "create_llm_client",
]
