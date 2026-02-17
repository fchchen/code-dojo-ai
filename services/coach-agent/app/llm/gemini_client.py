import asyncio
import logging
from typing import Any

from app.config import Settings

logger = logging.getLogger(__name__)


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
        except Exception as exc:
            logger.warning("Gemini client initialization failed; using fallback responses: %s", exc)
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
        except Exception as exc:
            logger.warning("Gemini generation failed; using fallback responses: %s", exc)
            return self._offline_fallback(prompt)

    @staticmethod
    def _offline_fallback(prompt: str) -> str:
        lowered = prompt.lower()
        if "return only code" in lowered:
            return (
                "# Fallback code example (LLM unavailable)\n"
                "def improve_example(items):\n"
                "    if not items:\n"
                "        return []\n"
                "    return [item for item in items if item is not None]\n"
            )
        if "best-practice" in lowered:
            return (
                "Fallback: add input validation for edge cases.\n"
                "Fallback: keep functions focused on one responsibility.\n"
                "Fallback: name variables to reflect intent.\n"
                "Fallback: add tests for normal and error paths.\n"
                "Fallback: log failures with actionable context."
            )
        if "explain the key concept" in lowered:
            return (
                "Fallback explanation: focus on readability first by making control flow explicit.\n\n"
                "Then reduce risk by validating inputs and handling error paths before core logic.\n\n"
                "Finally, add tests around the changed behavior so refactors remain safe."
            )
        trimmed = " ".join(prompt.split())
        return f"Fallback guidance (LLM unavailable): {trimmed[:220]}"
