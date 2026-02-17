import pytest

from app.config import Settings
from app.llm.gemini_client import GeminiClient


@pytest.mark.asyncio
async def test_gemini_client_fallback_without_api_key():
    client = GeminiClient(Settings(gemini_api_key=None))
    result = await client.generate("Explain unit testing")
    assert "fallback" in result.lower()
