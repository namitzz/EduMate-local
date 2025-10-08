"""
Legacy models.py - maintained for backward compatibility.
Imports functions from providers.py to maintain existing API.
"""
from providers import (
    ollama_complete,
    ollama_complete_stream,
    llm_complete,
    llm_complete_stream,
)

# Re-export for backward compatibility
__all__ = [
    "ollama_complete",
    "ollama_complete_stream",
    "llm_complete",
    "llm_complete_stream",
]
