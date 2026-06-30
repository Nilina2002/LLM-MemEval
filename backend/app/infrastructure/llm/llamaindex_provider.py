"""
LlamaIndex Ollama Provider.
Uses LlamaIndex's Ollama LLM integration for local model inference via llama3.
"""
from __future__ import annotations
import time
import os

from app.infrastructure.llm.base import LLMProvider, LLMResponse


class LlamaIndexOllamaProvider(LLMProvider):
    """
    Wraps LlamaIndex's Ollama LLM class for locally-hosted models.
    Provides the same zero-cost local inference as OllamaProvider but
    routed through the LlamaIndex abstraction layer.
    """

    def __init__(
        self,
        model: str = "llama3",
        base_url: str | None = None,
    ) -> None:
        self._model = model
        self._base_url = base_url or os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

    @property
    def provider_name(self) -> str:
        return "llamaindex"

    async def complete(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        from llama_index.llms.ollama import Ollama
        from llama_index.core.llms import ChatMessage, MessageRole

        llm = Ollama(
            model=self._model,
            base_url=self._base_url,
            temperature=temperature,
            request_timeout=120.0,
            context_window=max_tokens,
        )

        chat_messages = [
            ChatMessage(role=MessageRole.SYSTEM, content=system_prompt)
        ]
        for msg in messages:
            role = MessageRole.USER if msg["role"] == "user" else MessageRole.ASSISTANT
            chat_messages.append(ChatMessage(role=role, content=msg["content"]))

        start = time.monotonic()
        response = await llm.achat(chat_messages)
        latency_ms = (time.monotonic() - start) * 1000

        content = str(response.message.content)
        prompt_tokens = self.estimate_tokens(system_prompt + str(messages))
        completion_tokens = self.estimate_tokens(content)

        return LLMResponse(
            content=content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            model=self._model,
            latency_ms=latency_ms,
            cost_usd=0.0,
        )

    def estimate_tokens(self, text: str) -> int:
        return len(text) // 4

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        return 0.0
