"""
Baseline strategy: No Memory.
Every turn the model receives only the current message — no history, no context.
This establishes the lower bound for all benchmark comparisons.
"""
from __future__ import annotations
from app.strategies.base import MemoryStrategy
from app.domain.entities.message import Message


class NoMemoryStrategy(MemoryStrategy):
    """
    Stateless baseline. Zero context provided to the LLM.
    Expected to show rapid, near-complete forgetting in decay curves.
    """

    @property
    def name(self) -> str:
        return "no_memory"

    @property
    def description(self) -> str:
        return "Baseline: no memory context is provided. Establishes the lower bound."

    def build_context(self, messages: list[Message], query: str | None = None) -> str:
        return ""

    def update_memory(self, message: Message) -> None:
        pass  # Stateless — nothing to update

    def retrieve(self, query: str, top_k: int = 5) -> list[str]:
        return []  # No stored memories to retrieve

    def clear(self) -> None:
        pass
