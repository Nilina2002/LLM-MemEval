"""
THE critical abstraction of the entire framework.

MemoryStrategy is the ONLY contract between the benchmark and any memory system.
The benchmark never imports, references, or knows about specific memory implementations.

To add a new memory system:
  1. Create a class that inherits MemoryStrategy.
  2. Implement all abstract methods.
  3. Register it in strategies/registry.py.
  4. Run experiments.

No other files in the framework change.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

from app.domain.entities.message import Message


class MemoryStrategy(ABC):
    """
    Abstract base for all memory management strategies.

    The benchmark treats every strategy as a black box that:
    - accepts conversation messages
    - returns a context string to prepend to LLM calls
    - can be queried for specific information
    - can be reset between experiments
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this strategy (used in logging and DB)."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description for the dashboard."""
        ...

    @abstractmethod
    def build_context(self, messages: list[Message], query: str | None = None) -> str:
        """
        Return the context string to prepend to the next LLM prompt.

        Args:
            messages: Full conversation history (the strategy selects what to include).
            query: Optional hint about what the next turn will ask about.

        Returns:
            A string that will be injected into the system or user prompt.
        """
        ...

    @abstractmethod
    def update_memory(self, message: Message) -> None:
        """
        Called after every conversation turn.
        Strategies use this to update internal state (e.g., append to window,
        summarize, embed into vector store, etc.).

        Args:
            message: The message just added to the conversation.
        """
        ...

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> list[str]:
        """
        Retrieve the most relevant memory fragments for a query.
        Used by the RecallTestingEngine to fetch what the strategy "remembers".

        Args:
            query: The recall question or search string.
            top_k: Maximum number of fragments to return.

        Returns:
            List of relevant memory strings, most relevant first.
        """
        ...

    @abstractmethod
    def clear(self) -> None:
        """
        Reset all internal state.
        Called at the start of each new experiment to ensure isolation.
        """
        ...

    def get_memory_stats(self) -> dict[str, Any]:
        """
        Optional: return strategy-specific statistics for logging.
        Override to expose internal state (window size, summary length, index size, etc.).
        """
        return {}
