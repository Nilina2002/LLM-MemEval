"""
OpenAI LLM Provider.
Wraps the openai Python SDK behind the LLMProvider interface.
"""
from __future__ import annotations
import time
import os
from typing import Any

from app.infrastructure.llm.base import LLMProvider, LLMResponse

# Model pricing per 1M tokens (input, output) as of mid-2025
OPENAI_PRICING: dict[str, tuple[float, float]] = {
    "gpt-4o": (5.00, 15.00),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4-turbo": (10.00, 30.00),
    "gpt-3.5-turbo": (0.50, 1.50),
}


class OpenAIProvider(LLMProvider):
    """
    OpenAI provider. Supports all GPT models including gpt-4o-mini for cost efficiency.
    """

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini") -> None:
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self._default_model = model
        self._client = None  # Lazy-initialized

    def _get_client(self):
        if self._client is None:
            import openai
            self._client = openai.AsyncOpenAI(api_key=self._api_key)
        return self._client

    @property
    def provider_name(self) -> str:
        return "openai"

    async def complete(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        client = self._get_client()
        start = time.monotonic()

        full_messages = [{"role": "system", "content": system_prompt}] + messages

        response = await client.chat.completions.create(
            model=self._default_model,
            messages=full_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        latency_ms = (time.monotonic() - start) * 1000
        usage = response.usage
        cost = self.calculate_cost(usage.prompt_tokens, usage.completion_tokens)

        return LLMResponse(
            content=response.choices[0].message.content,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
            model=response.model,
            latency_ms=latency_ms,
            cost_usd=cost,
            raw_response=response.model_dump(),
        )

    def estimate_tokens(self, text: str) -> int:
        # Rough approximation without tiktoken
        return len(text) // 4

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        input_price, output_price = OPENAI_PRICING.get(self._default_model, (5.0, 15.0))
        return (prompt_tokens * input_price + completion_tokens * output_price) / 1_000_000
