"""
Ollama Local LLM Provider.
Enables running experiments on local models — no API cost, full privacy.
"""
from __future__ import annotations
import time
import os

from app.infrastructure.llm.base import LLMProvider, LLMResponse


class OllamaProvider(LLMProvider):
    """
    Wraps the Ollama HTTP API for locally-hosted models.
    Zero cost — token counts are estimated from character ratios.
    """

    def __init__(
        self,
        model: str = "llama3.2",
        base_url: str | None = None,
    ) -> None:
        self._model = model
        self._base_url = base_url or os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

    @property
    def provider_name(self) -> str:
        return "ollama"

    async def complete(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        import httpx
        start = time.monotonic()

        payload = {
            "model": self._model,
            "messages": [{"role": "system", "content": system_prompt}] + messages,
            "options": {"temperature": temperature, "num_predict": max_tokens},
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(f"{self._base_url}/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()

        latency_ms = (time.monotonic() - start) * 1000
        content = data["message"]["content"]
        prompt_tokens = self.estimate_tokens(system_prompt + str(messages))
        completion_tokens = self.estimate_tokens(content)

        return LLMResponse(
            content=content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            model=self._model,
            latency_ms=latency_ms,
            cost_usd=0.0,   # Local — no cost
        )

    def estimate_tokens(self, text: str) -> int:
        return len(text) // 4

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        return 0.0
