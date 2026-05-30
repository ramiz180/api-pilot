import logging
import os
from typing import AsyncIterator

import instructor
import openai
from openai import AsyncOpenAI
from pydantic import BaseModel

from app.ai.providers.base import LLMProvider, LLMProviderError, Message, ModelInfo

logger = logging.getLogger(__name__)


class OpenAICompatibleProvider:
    """Works with any OpenAI-compatible endpoint.

    Verified targets:
      - NVIDIA NIM: base_url="https://integrate.api.nvidia.com/v1"
        Models: "meta/llama-3.3-70b-instruct", "meta/llama-3.1-70b-instruct"
      - Groq: base_url="https://api.groq.com/openai/v1"
        Models: "llama-3.3-70b-versatile"
      - OpenAI: base_url="https://api.openai.com/v1" (default)
        Models: "gpt-4o-mini", "gpt-4o"
      - Local Ollama: base_url="http://localhost:11434/v1"
    """

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        provider_name: str = "openai_compatible",
        context_window: int = 128_000,
        timeout: float = 120.0,
        instructor_mode: instructor.Mode = instructor.Mode.JSON,
    ):
        if not api_key:
            raise LLMProviderError("API key is required for OpenAICompatibleProvider")
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url, timeout=timeout)
        self._instructor = instructor.from_openai(self._client, mode=instructor_mode)
        self._model = model
        self._provider_name = provider_name
        self._context_window = context_window
        self._base_url = base_url

    async def generate_structured(
        self,
        prompt: str,
        schema: type[BaseModel],
        system: str | None = None,
        model: str | None = None,
        max_tokens: int = 4096,
    ) -> BaseModel:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            result = await self._instructor.chat.completions.create(
                model=model or self._model,
                max_tokens=max_tokens,
                messages=messages,
                response_model=schema,
            )
            return result
        except openai.APIError as e:
            logger.exception("OpenAI-compatible API error from %s", self._base_url)
            raise LLMProviderError(f"LLM API error ({self._provider_name}): {e}") from e
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
        openai_messages = []
        if system:
            openai_messages.append({"role": "system", "content": system})
        openai_messages.extend({"role": m.role, "content": m.content} for m in messages)

        if not stream:
            response = await self._client.chat.completions.create(
                model=self._model,
                max_tokens=max_tokens,
                messages=openai_messages,
            )
            yield response.choices[0].message.content or ""
            return

        stream_resp = await self._client.chat.completions.create(
            model=self._model,
            max_tokens=max_tokens,
            messages=openai_messages,
            stream=True,
        )
        async for chunk in stream_resp:
            delta = chunk.choices[0].delta.content if chunk.choices else None
            if delta:
                yield delta

    def get_model_info(self) -> ModelInfo:
        return ModelInfo(
            provider=self._provider_name,
            model=self._model,
            context_window=self._context_window,
            supports_tools=True,
        )
