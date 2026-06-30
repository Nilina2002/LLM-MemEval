"""
Anthropic Claude LLM Provider.
"""
from __future__ import annotations
import time
import os

from app.infrastructure.llm.base import LLMProvider, LLMResponse

CLAUDE_PRICING: dict[str, tuple[float, float]] = {
    "claude-haiku-4-5-20251001": (0.80, 4.00),
    "claude-sonnet-4-6": (3.00, 15.00),
    "claude-opus-4-8": (15.00, 75.00),
}


class ClaudeProvider(LLMProvider):
    def __init__(self, api_key: str | None = None, model: str = "claude-haiku-4-5-20251001") -> None:
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self._default_model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            import anthropic
            self._client = anthropic.AsyncAnthropic(api_key=self._api_key)
        return self._client

    @property
    def provider_name(self) -> str:
        return "claude"

    async def complete(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        client = self._get_client()
        start = time.monotonic()

        response = await client.messages.create(
            model=self._default_model,
            system=system_prompt,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        latency_ms = (time.monotonic() - start) * 1000
        prompt_tokens = response.usage.input_tokens
        completion_tokens = response.usage.output_tokens
        cost = self.calculate_cost(prompt_tokens, completion_tokens)

        return LLMResponse(
            content=response.content[0].text,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            model=response.model,
            latency_ms=latency_ms,
            cost_usd=cost,
        )

    def estimate_tokens(self, text: str) -> int:
        return len(text) // 4

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        input_price, output_price = CLAUDE_PRICING.get(self._default_model, (3.0, 15.0))
        return (prompt_tokens * input_price + completion_tokens * output_price) / 1_000_000
