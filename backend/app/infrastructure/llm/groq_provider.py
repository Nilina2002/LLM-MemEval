"""Groq LLM Provider — fast inference for Llama and Mixtral models."""
from __future__ import annotations
import time
import os
from app.infrastructure.llm.base import LLMProvider, LLMResponse

GROQ_PRICING: dict[str, tuple[float, float]] = {
    "llama-3.3-70b-versatile": (0.59, 0.79),
    "llama-3.1-8b-instant": (0.05, 0.08),
    "mixtral-8x7b-32768": (0.24, 0.24),
}


class GroqProvider(LLMProvider):
    def __init__(self, api_key: str | None = None, model: str = "llama-3.1-8b-instant") -> None:
        self._api_key = api_key or os.environ.get("GROQ_API_KEY", "")
        self._default_model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            from groq import AsyncGroq
            self._client = AsyncGroq(api_key=self._api_key)
        return self._client

    @property
    def provider_name(self) -> str:
        return "groq"

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
        return LLMResponse(
            content=response.choices[0].message.content,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
            model=response.model,
            latency_ms=latency_ms,
            cost_usd=self.calculate_cost(usage.prompt_tokens, usage.completion_tokens),
        )

    def estimate_tokens(self, text: str) -> int:
        return len(text) // 4

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        input_price, output_price = GROQ_PRICING.get(self._default_model, (0.5, 0.5))
        return (prompt_tokens * input_price + completion_tokens * output_price) / 1_000_000
