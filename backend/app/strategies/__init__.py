"""
Strategy registration.
Import and register all built-in strategies at application startup.
To add a new strategy: import it here and call registry.register().
"""
from app.strategies.registry import registry
from app.strategies.no_memory import NoMemoryStrategy
from app.strategies.sliding_window import SlidingWindowStrategy


def register_all_strategies() -> None:
    """Register all built-in strategies. Called once at app startup."""
    registry.register(NoMemoryStrategy)
    registry.register(SlidingWindowStrategy)
    # SummarizationStrategy requires an LLM provider — registered with params in dependency injection
    # ChromaRAGStrategy requires ChromaDB — registered conditionally based on config
