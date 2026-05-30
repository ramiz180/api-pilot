"""Manual smoke test for Anthropic provider. Run with real ANTHROPIC_API_KEY.

Usage:
    cd backend
    .venv\\Scripts\\Activate.ps1
    $env:ANTHROPIC_API_KEY = "sk-ant-..."
    python scripts/smoke_test_llm.py
"""
import asyncio
import os

from pydantic import BaseModel

from app.ai.providers.anthropic_provider import AnthropicProvider
from app.ai.providers.base import Message


class Greeting(BaseModel):
    language: str
    text: str


async def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Set ANTHROPIC_API_KEY first.")
        return
    provider = AnthropicProvider()
    print(f"Model: {provider.get_model_info()}")
    print("Calling generate_structured...")
    result = await provider.generate_structured(
        prompt="Say hello in French. Return JSON with 'language' and 'text' fields.",
        schema=Greeting,
        system="You are a multilingual greeter.",
        max_tokens=200,
    )
    print(f"Got: {result}")
    print("Calling chat (streaming)...")
    async for chunk in provider.chat(
        [Message(role="user", content="Count to 5.")],
        max_tokens=100,
    ):
        print(chunk, end="", flush=True)
    print()


if __name__ == "__main__":
    asyncio.run(main())
