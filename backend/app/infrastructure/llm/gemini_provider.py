"""Google Gemini LLM Provider."""
from __future__ import annotations
import time
import os
from app.infrastructure.llm.base import LLMProvider, LLMResponse

GEMINI_PRICING: dict[str, tuple[float, float]] = {
    "gemini-1.5-flash":   (0.075, 0.30),
    "gemini-1.5-pro":     (3.50,  10.50),
    "gemini-2.0-flash":   (0.10,  0.40),
}


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str | None = None, model: str = "gemini-1.5-flash") -> None:
        self._api_key = api_key or os.environ.get("GOOGLE_API_KEY", "")
        self._default_model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            import google.generativeai as genai
            genai.configure(api_key=self._api_key)
            self._client = genai.GenerativeModel(self._default_model)
        return self._client

    @property
    def provider_name(self) -> str:
        return "gemini"

    async def complete(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        import asyncio
        client = self._get_client()
        start = time.monotonic()

        # Gemini uses contents list; prepend system as first user message
        combined = f"{system_prompt}\n\n" + "\n".join(m["content"] for m in messages)

        response = await asyncio.to_thread(
            client.generate_content,
            combined,
            generation_config={"temperature": temperature, "max_output_tokens": max_tokens},
        )

        latency_ms = (time.monotonic() - start) * 1000
        content = response.text
        prompt_tokens = self.estimate_tokens(combined)
        completion_tokens = self.estimate_tokens(content)
        cost = self.calculate_cost(prompt_tokens, completion_tokens)

        return LLMResponse(
            content=content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            model=self._default_model,
            latency_ms=latency_ms,
            cost_usd=cost,
        )

    def estimate_tokens(self, text: str) -> int:
        return len(text) // 4

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        input_price, output_price = GEMINI_PRICING.get(self._default_model, (0.075, 0.30))
        return (prompt_tokens * input_price + completion_tokens * output_price) / 1_000_000
