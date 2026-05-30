import logging
import os
from typing import AsyncIterator

import anthropic
import instructor
from pydantic import BaseModel

from app.ai.providers.base import LLMProvider, Message, ModelInfo, LLMProviderError

logger = logging.getLogger(__name__)


class AnthropicProvider:
    """Anthropic Claude provider."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "claude-sonnet-4-5",
        timeout: float = 120.0,
    ):
        key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise LLMProviderError(
                "ANTHROPIC_API_KEY not set. Add it to backend/.env or pass api_key explicitly."
            )
        self._client = anthropic.AsyncAnthropic(api_key=key, timeout=timeout)
        self._instructor = instructor.from_anthropic(self._client)
        self._model = model
        self._timeout = timeout

    async def generate_structured(
        self,
        prompt: str,
        schema: type[BaseModel],
        system: str | None = None,
        model: str | None = None,
        max_tokens: int = 4096,
    ) -> BaseModel:
        messages = [{"role": "user", "content": prompt}]
        try:
            result = await self._instructor.messages.create(
                model=model or self._model,
                max_tokens=max_tokens,
                system=system or "You are a helpful assistant.",
                messages=messages,
                response_model=schema,
            )
            return result
        except anthropic.APIError as e:
            logger.exception("Anthropic API error")
            raise LLMProviderError(f"Anthropic API error: {e}") from e
        except Exception as e:
            logger.exception("Unexpected error during structured generation")
            raise LLMProviderError(f"Generation failed: {e}") from e

    async def chat(
        self,
        messages: list[Message],
        system: str | None = None,
        stream: bool = True,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        anthropic_messages = [{"role": m.role, "content": m.content} for m in messages]

        if not stream:
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=max_tokens,
                system=system or "You are a helpful assistant.",
                messages=anthropic_messages,
            )
            yield response.content[0].text
            return

        async with self._client.messages.stream(
            model=self._model,
            max_tokens=max_tokens,
            system=system or "You are a helpful assistant.",
            messages=anthropic_messages,
        ) as stream_ctx:
            async for text in stream_ctx.text_stream:
                yield text

    def get_model_info(self) -> ModelInfo:
        return ModelInfo(
            provider="anthropic",
            model=self._model,
            context_window=200_000,
            supports_tools=True,
        )
