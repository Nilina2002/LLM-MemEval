"""OpenRouter LLM Provider — routes to many models via a unified API."""
from __future__ import annotations
import time
import os
from app.infrastructure.llm.base import LLMProvider, LLMResponse


class OpenRouterProvider(LLMProvider):
    """
    OpenRouter provides access to hundreds of models (GPT, Claude, Llama, Mistral, etc.)
    through a single OpenAI-compatible API endpoint.
    Useful for model comparison experiments.
    """

    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, api_key: str | None = None, model: str = "openai/gpt-4o-mini") -> None:
        self._api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "")
        self._default_model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            import openai
            self._client = openai.AsyncOpenAI(
                api_key=self._api_key,
                base_url=self.BASE_URL,
            )
        return self._client

    @property
    def provider_name(self) -> str:
        return "openrouter"

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
        # OpenRouter returns cost in usage metadata when available
        cost_usd = getattr(usage, "total_cost", None) or self.calculate_cost(
            usage.prompt_tokens, usage.completion_tokens
        )

        return LLMResponse(
            content=response.choices[0].message.content,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
            model=response.model,
            latency_ms=latency_ms,
            cost_usd=cost_usd,
        )

    def estimate_tokens(self, text: str) -> int:
        return len(text) // 4

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        # OpenRouter pricing varies by model; use generic estimate
        return (prompt_tokens * 1.0 + completion_tokens * 2.0) / 1_000_000
