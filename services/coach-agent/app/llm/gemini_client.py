import asyncio
from typing import Any

from app.config import Settings


class GeminiClient:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._client: Any | None = None

    def _ensure_client(self) -> Any | None:
        if self._client is not None:
            return self._client
        if not self._settings.gemini_api_key:
            return None
        try:
            from google import genai

            self._client = genai.Client(api_key=self._settings.gemini_api_key)
            return self._client
        except Exception:
            return None

    async def generate(self, prompt: str) -> str:
        client = self._ensure_client()
        if client is None:
            return self._offline_fallback(prompt)

        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(
                    lambda: client.models.generate_content(
                        model=self._settings.gemini_model,
                        contents=prompt,
                    )
                ),
                timeout=self._settings.llm_timeout_seconds,
            )
            text = getattr(result, "text", None)
            return text.strip() if text else self._offline_fallback(prompt)
        except Exception:
            return self._offline_fallback(prompt)

    @staticmethod
    def _offline_fallback(prompt: str) -> str:
        trimmed = " ".join(prompt.split())
        return f"Generated fallback guidance based on: {trimmed[:300]}"
