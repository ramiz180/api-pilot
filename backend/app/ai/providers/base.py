from typing import Protocol, AsyncIterator
from pydantic import BaseModel


class Message(BaseModel):
    """One chat message."""
    role: str  # "system" | "user" | "assistant"
    content: str


class ModelInfo(BaseModel):
    """Static info about the provider's model."""
    provider: str       # "anthropic" | "mock"
    model: str          # e.g. "claude-sonnet-4-5"
    context_window: int
    supports_tools: bool


class LLMProvider(Protocol):
    async def generate_structured(
        self,
        prompt: str,
        schema: type[BaseModel],
        system: str | None = None,
        model: str | None = None,
        max_tokens: int = 4096,
    ) -> BaseModel:
        """Generate a response that conforms to the given Pydantic schema."""
        ...

    async def chat(
        self,
        messages: list[Message],
        system: str | None = None,
        stream: bool = True,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        """Stream a chat response. Yields text chunks."""
        ...

    def get_model_info(self) -> ModelInfo: ...


class LLMProviderError(Exception):
    """Raised when the provider fails (network, auth, malformed output, etc)."""
