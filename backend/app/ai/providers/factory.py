import os
from functools import lru_cache

from app.ai.providers.anthropic_provider import AnthropicProvider
from app.ai.providers.base import LLMProvider, LLMProviderError
from app.ai.providers.mock_provider import MockProvider
from app.ai.providers.openai_compatible_provider import OpenAICompatibleProvider


# Preset configurations for common OpenAI-compatible endpoints.
# Users override via env vars; these are sensible defaults.
PRESETS = {
    "nvidia_nim": {
        "base_url": "https://integrate.api.nvidia.com/v1",
        "model": "meta/llama-3.3-70b-instruct",
        "provider_name": "nvidia_nim",
        "context_window": 128_000,
        "api_key_env": "NVIDIA_API_KEY",
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "model": "llama-3.3-70b-versatile",
        "provider_name": "groq",
        "context_window": 128_000,
        "api_key_env": "GROQ_API_KEY",
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
        "provider_name": "openai",
        "context_window": 128_000,
        "api_key_env": "OPENAI_API_KEY",
    },
}


@lru_cache(maxsize=1)
def get_llm_provider() -> LLMProvider:
    """Return the configured LLM provider based on env vars.

    LLM_PROVIDER values:
      - "nvidia_nim" (default) — needs NVIDIA_API_KEY
      - "groq" — needs GROQ_API_KEY
      - "openai" — needs OPENAI_API_KEY
      - "anthropic" — needs ANTHROPIC_API_KEY
      - "mock" — for tests

    Optional overrides:
      LLM_BASE_URL — overrides preset base_url
      LLM_MODEL — overrides preset model
    """
    provider_name = os.environ.get("LLM_PROVIDER", "nvidia_nim").lower()

    if provider_name == "mock":
        return MockProvider()

    if provider_name == "anthropic":
        model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5")
        return AnthropicProvider(model=model)

    if provider_name in PRESETS:
        preset = PRESETS[provider_name]
        api_key = os.environ.get(preset["api_key_env"])
        if not api_key:
            raise LLMProviderError(
                f"{preset['api_key_env']} not set. "
                f"Get a free key at the provider's website and add to backend/.env."
            )
        base_url = os.environ.get("LLM_BASE_URL", preset["base_url"])
        model = os.environ.get("LLM_MODEL", preset["model"])
        return OpenAICompatibleProvider(
            api_key=api_key,
            base_url=base_url,
            model=model,
            provider_name=preset["provider_name"],
            context_window=preset["context_window"],
        )

    raise LLMProviderError(
        f"Unknown LLM_PROVIDER: {provider_name!r}. "
        f"Valid values: nvidia_nim, groq, openai, anthropic, mock."
    )


def reset_provider_cache() -> None:
    """Clear the provider cache. Used by tests after env changes."""
    get_llm_provider.cache_clear()
