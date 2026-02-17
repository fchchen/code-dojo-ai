import asyncio

import httpx

from app.config import Settings

_client_lock = asyncio.Lock()
_shared_client: httpx.AsyncClient | None = None
_shared_timeout_seconds: float | None = None


async def _get_shared_client(timeout_seconds: float) -> httpx.AsyncClient:
    global _shared_client, _shared_timeout_seconds
    if _shared_client is not None and _shared_timeout_seconds == timeout_seconds:
        return _shared_client

    async with _client_lock:
        if _shared_client is not None and _shared_timeout_seconds == timeout_seconds:
            return _shared_client
        if _shared_client is not None:
            await _shared_client.aclose()
        _shared_client = httpx.AsyncClient(timeout=httpx.Timeout(timeout_seconds))
        _shared_timeout_seconds = timeout_seconds
        return _shared_client


async def close_shared_client() -> None:
    global _shared_client, _shared_timeout_seconds
    async with _client_lock:
        if _shared_client is not None:
            await _shared_client.aclose()
            _shared_client = None
            _shared_timeout_seconds = None


async def analyze_code_quality(settings: Settings, code: str, language: str | None) -> dict:
    payload = {"code": code, "language": language}
    client = await _get_shared_client(settings.request_timeout_seconds)
    base_url = settings.ml_analyzer_url.rstrip("/")
    summary = "ML summarizer unavailable; generated fallback summary."
    comments: list[str] = []

    try:
        summary_resp = await client.post(f"{base_url}/api/analyze/summarize", json=payload)
        summary_resp.raise_for_status()
        summary = summary_resp.json().get("summary") or summary
    except httpx.HTTPError:
        pass

    try:
        review_resp = await client.post(f"{base_url}/api/analyze/review", json=payload)
        review_resp.raise_for_status()
        comments = review_resp.json().get("comments") or comments
    except httpx.HTTPError:
        pass

    if not comments:
        comments = ["Unable to fetch detailed review comments; focus on readability and tests."]

    return {
        "summary": summary,
        "issues": comments,
    }
