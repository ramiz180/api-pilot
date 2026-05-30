import os

import pytest
from pydantic import BaseModel

from app.ai.providers.anthropic_provider import AnthropicProvider
from app.ai.providers.base import LLMProviderError, Message
from app.ai.providers.factory import get_llm_provider, reset_provider_cache
from app.ai.providers.mock_provider import MockProvider


class SampleOutput(BaseModel):
    name: str
    count: int


@pytest.fixture(autouse=True)
def _force_mock(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    reset_provider_cache()
    yield
    reset_provider_cache()


async def test_factory_returns_mock_when_env_set():
    provider = get_llm_provider()
    assert isinstance(provider, MockProvider)


async def test_factory_caches_instance():
    p1 = get_llm_provider()
    p2 = get_llm_provider()
    assert p1 is p2


async def test_mock_seeded_structured_response():
    provider = get_llm_provider()
    assert isinstance(provider, MockProvider)
    provider.seed_structured(SampleOutput, SampleOutput(name="hi", count=3))
    result = await provider.generate_structured("anything", SampleOutput)
    assert isinstance(result, SampleOutput)
    assert result.name == "hi"
    assert result.count == 3


async def test_mock_records_calls():
    provider = get_llm_provider()
    assert isinstance(provider, MockProvider)
    provider.seed_structured(SampleOutput, SampleOutput(name="a", count=1))
    await provider.generate_structured("my prompt", SampleOutput, system="be terse")
    assert len(provider.calls) == 1
    call = provider.calls[0]
    assert call["method"] == "generate_structured"
    assert call["prompt"] == "my prompt"
    assert call["schema"] == "SampleOutput"
    assert call["system"] == "be terse"


async def test_mock_chat_streams_chunks():
    provider = get_llm_provider()
    assert isinstance(provider, MockProvider)
    provider.seed_chat("hello world from mock")
    chunks = []
    async for chunk in provider.chat([Message(role="user", content="hi")]):
        chunks.append(chunk)
    assert "".join(chunks).strip() == "hello world from mock"


async def test_mock_get_model_info():
    provider = get_llm_provider()
    info = provider.get_model_info()
    assert info.provider == "mock"


async def test_unknown_provider_raises(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "bogus")
    reset_provider_cache()
    with pytest.raises(LLMProviderError, match="Unknown LLM_PROVIDER"):
        get_llm_provider()


async def test_anthropic_provider_requires_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(LLMProviderError, match="ANTHROPIC_API_KEY"):
        AnthropicProvider(api_key=None)


async def test_anthropic_provider_model_info():
    """AnthropicProvider constructor works with a fake key (no API call)."""
    provider = AnthropicProvider(api_key="fake-key-for-test", model="claude-sonnet-4-5")
    info = provider.get_model_info()
    assert info.provider == "anthropic"
    assert info.model == "claude-sonnet-4-5"
    assert info.supports_tools is True
