"""
LLM Provider Factory.
Creates the correct LLMProvider from an LLMConfig.
The rest of the framework imports this function — never specific provider classes.
"""
from __future__ import annotations
from app.core.config.experiment_config import LLMConfig
from app.domain.interfaces.llm_provider import LLMProvider
from app.core.config.settings import settings
from app.core.exceptions import ConfigurationError


def create_llm_provider(config: LLMConfig) -> LLMProvider:
    """
    Instantiate the appropriate LLMProvider from configuration.

    Args:
        config: LLMConfig from the experiment configuration.

    Returns:
        Configured LLMProvider ready for use.

    Raises:
        ConfigurationError: If the provider is not supported.
    """
    # Resolve API key: use explicit value or fall back to environment variable
    api_key = _resolve_api_key(config)

    match config.provider:
        case "openai":
            from app.infrastructure.llm.openai_provider import OpenAIProvider
            return OpenAIProvider(api_key=api_key, model=config.model)

        case "claude":
            from app.infrastructure.llm.claude_provider import ClaudeProvider
            return ClaudeProvider(api_key=api_key, model=config.model)

        case "gemini":
            from app.infrastructure.llm.gemini_provider import GeminiProvider
            return GeminiProvider(api_key=api_key, model=config.model)

        case "groq":
            from app.infrastructure.llm.groq_provider import GroqProvider
            return GroqProvider(api_key=api_key, model=config.model)

        case "openrouter":
            from app.infrastructure.llm.openrouter_provider import OpenRouterProvider
            return OpenRouterProvider(api_key=api_key, model=config.model)

        case "ollama":
            from app.infrastructure.llm.ollama_provider import OllamaProvider
            return OllamaProvider(
                model=config.model,
                base_url=config.base_url or settings.OLLAMA_BASE_URL,
            )

        case "llamaindex":
            from app.infrastructure.llm.llamaindex_provider import LlamaIndexOllamaProvider
            return LlamaIndexOllamaProvider(
                model=config.model,
                base_url=config.base_url or settings.OLLAMA_BASE_URL,
            )

        case _:
            raise ConfigurationError(
                f"Unknown LLM provider '{config.provider}'. "
                "Supported: openai, claude, gemini, groq, openrouter, ollama, llamaindex."
            )


def _resolve_api_key(config: LLMConfig) -> str | None:
    """Resolve API key from config or environment."""
    if config.api_key_env_var:
        import os
        return os.environ.get(config.api_key_env_var, "")

    # Default environment variables per provider
    env_map = {
        "openai":      settings.OPENAI_API_KEY,
        "claude":      settings.ANTHROPIC_API_KEY,
        "gemini":      settings.GOOGLE_API_KEY,
        "groq":        settings.GROQ_API_KEY,
        "openrouter":  settings.OPENROUTER_API_KEY,
        "ollama":      None,    # No key needed for local Ollama
        "llamaindex":  None,    # No key needed — routes through Ollama locally
    }
    return env_map.get(config.provider)
