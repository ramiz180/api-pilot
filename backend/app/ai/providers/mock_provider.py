import asyncio
from typing import AsyncIterator

from pydantic import BaseModel

from app.ai.providers.base import Message, ModelInfo


class MockProvider:
    """Mock LLM provider for tests. Returns pre-seeded fixtures or default instances.

    Usage:
        provider = MockProvider()
        provider.seed_structured(MyModel, MyModel(...))
        result = await provider.generate_structured("prompt", MyModel)
    """

    def __init__(self):
        self._structured_responses: dict[type[BaseModel], BaseModel] = {}
        self._chat_response: str = "Mock chat response."
        self.calls: list[dict] = []  # records every call for assertions

    def seed_structured(self, schema: type[BaseModel], response: BaseModel) -> None:
        if not isinstance(response, schema):
            raise TypeError(f"response must be an instance of {schema}")
        self._structured_responses[schema] = response

    def seed_chat(self, text: str) -> None:
        self._chat_response = text

    async def generate_structured(
        self,
        prompt: str,
        schema: type[BaseModel],
        system: str | None = None,
        model: str | None = None,
        max_tokens: int = 4096,
    ) -> BaseModel:
        self.calls.append({
            "method": "generate_structured",
            "prompt": prompt,
            "schema": schema.__name__,
            "system": system,
        })
        await asyncio.sleep(0)  # yield to event loop
        if schema in self._structured_responses:
            return self._structured_responses[schema]
        # No seeded response — try to construct a default instance.
        # Will fail loudly if schema has required fields, which is the right behavior.
        return schema()

    async def chat(
        self,
        messages: list[Message],
        system: str | None = None,
        stream: bool = True,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        self.calls.append({
            "method": "chat",
            "messages": [m.model_dump() for m in messages],
            "system": system,
        })
        for chunk in self._chat_response.split(" "):
            await asyncio.sleep(0)
            yield chunk + " "

    def get_model_info(self) -> ModelInfo:
        return ModelInfo(
            provider="mock",
            model="mock-model",
            context_window=999999,
            supports_tools=True,
        )
