"""
Summarization Memory Strategy.
Periodically summarizes the conversation and uses the summary as context.
Tests whether compression preserves factual information.
"""
from __future__ import annotations
from typing import Any

from app.strategies.base import MemoryStrategy
from app.domain.entities.message import Message
from app.domain.interfaces.llm_provider import LLMProvider


class SummarizationStrategy(MemoryStrategy):
    """
    Maintains a rolling summary of the conversation.
    Every `summarize_every` turns, the LLM summarizes the unsummarized portion.
    """

    def __init__(
        self,
        llm_provider: LLMProvider,
        summarize_every: int = 50,
        max_summary_tokens: int = 500,
    ) -> None:
        self._llm = llm_provider
        self._summarize_every = summarize_every
        self._max_summary_tokens = max_summary_tokens
        self._summary: str = ""
        self._unsummarized: list[Message] = []
        self._turn_count: int = 0

    @property
    def name(self) -> str:
        return "summarization"

    @property
    def description(self) -> str:
        return f"Summarizes conversation every {self._summarize_every} turns."

    def build_context(self, messages: list[Message], query: str | None = None) -> str:
        parts = []
        if self._summary:
            parts.append(f"Conversation summary:\n{self._summary}")
        if self._unsummarized:
            recent = "\n".join(
                f"{m.role.value.upper()}: {m.content}" for m in self._unsummarized[-10:]
            )
            parts.append(f"Recent messages:\n{recent}")
        return "\n\n".join(parts)

    def update_memory(self, message: Message) -> None:
        self._unsummarized.append(message)
        self._turn_count += 1
        if self._turn_count % self._summarize_every == 0:
            # Summarization is async in the pipeline — flag for deferred execution
            self._needs_summarization = True

    def retrieve(self, query: str, top_k: int = 5) -> list[str]:
        results = []
        if self._summary:
            results.append(self._summary)
        for msg in self._unsummarized[-top_k:]:
            results.append(msg.content)
        return results[:top_k]

    def clear(self) -> None:
        self._summary = ""
        self._unsummarized = []
        self._turn_count = 0

    async def summarize(self) -> None:
        """Trigger an LLM summarization of unsummarized messages. Called by the pipeline."""
        # TODO: implement — call self._llm.complete() with summarization prompt
        raise NotImplementedError

    def get_memory_stats(self) -> dict[str, Any]:
        return {
            "summary_length_chars": len(self._summary),
            "unsummarized_turns": len(self._unsummarized),
            "total_turns": self._turn_count,
        }
