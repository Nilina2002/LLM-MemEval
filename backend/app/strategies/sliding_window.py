"""
Sliding Window Memory Strategy.
Maintains a fixed-size window of the most recent N conversation turns.
Classic baseline — simple, predictable, well-understood forgetting behavior.
"""
from __future__ import annotations
from collections import deque
from typing import Any

from app.strategies.base import MemoryStrategy
from app.domain.entities.message import Message


class SlidingWindowStrategy(MemoryStrategy):
    """
    Keeps the last `window_size` messages as context.
    Forgetting is deterministic: facts injected more than window_size turns ago are lost.
    """

    def __init__(self, window_size: int = 20) -> None:
        self._window_size = window_size
        self._window: deque[Message] = deque(maxlen=window_size)

    @property
    def name(self) -> str:
        return "sliding_window"

    @property
    def description(self) -> str:
        return f"Keeps the last {self._window_size} conversation turns as context."

    def build_context(self, messages: list[Message], query: str | None = None) -> str:
        if not self._window:
            return ""
        lines = []
        for msg in self._window:
            lines.append(f"{msg.role.value.upper()}: {msg.content}")
        return "Recent conversation:\n" + "\n".join(lines)

    def update_memory(self, message: Message) -> None:
        self._window.append(message)

    def retrieve(self, query: str, top_k: int = 5) -> list[str]:
        return [msg.content for msg in list(self._window)[-top_k:]]

    def clear(self) -> None:
        self._window.clear()

    def get_memory_stats(self) -> dict[str, Any]:
        return {
            "window_size": self._window_size,
            "current_size": len(self._window),
        }
