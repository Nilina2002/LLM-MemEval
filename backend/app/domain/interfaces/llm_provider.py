"""
Abstract interface for all LLM providers.
The rest of the framework never imports provider-specific code.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Normalized response from any LLM provider."""
    content: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str
    latency_ms: float
    cost_usd: float
    raw_response: dict | None = None  # Provider-specific payload for debugging


class LLMProvider(ABC):
    """
    Abstract LLM provider. Implementations wrap OpenAI, Claude, Gemini, Groq,
    Ollama, and OpenRouter. The benchmark and strategies call only this interface.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Identifier: 'openai', 'claude', 'gemini', 'groq', 'ollama', 'openrouter'."""
        ...

    @abstractmethod
    async def complete(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """
        Send a prompt to the LLM and return a normalized response.

        Args:
            system_prompt: System-level instructions.
            messages: Conversation history in OpenAI format [{role, content}].
            temperature: Sampling temperature.
            max_tokens: Response token limit.

        Returns:
            Normalized LLMResponse with content, token counts, cost, and latency.
        """
        ...

    @abstractmethod
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for a string without making an API call."""
        ...

    @abstractmethod
    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate cost in USD for a given token usage."""
        ...
