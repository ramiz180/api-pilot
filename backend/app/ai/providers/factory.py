import os
from functools import lru_cache

from app.ai.providers.base import LLMProvider, LLMProviderError
from app.ai.providers.anthropic_provider import AnthropicProvider
from app.ai.providers.mock_provider import MockProvider


@lru_cache(maxsize=1)
def get_llm_provider() -> LLMProvider:
    """Return the configured LLM provider based on env vars.

    Env vars:
        LLM_PROVIDER: "anthropic" | "mock" (default: "anthropic")
        ANTHROPIC_MODEL: model name (default: "claude-sonnet-4-5")
        ANTHROPIC_API_KEY: required if provider is "anthropic"

    Cached so the same instance is reused across the process.
    Tests should call `get_llm_provider.cache_clear()` after changing env vars.
    """
    provider_name = os.environ.get("LLM_PROVIDER", "anthropic").lower()

    if provider_name == "anthropic":
        model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5")
        return AnthropicProvider(model=model)
    elif provider_name == "mock":
        return MockProvider()
    else:
        raise LLMProviderError(f"Unknown LLM_PROVIDER: {provider_name!r}")


def reset_provider_cache() -> None:
    """Clear the provider cache. Used by tests after env changes."""
    get_llm_provider.cache_clear()
