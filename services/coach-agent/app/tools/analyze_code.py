import httpx

from app.config import Settings


async def analyze_code_quality(settings: Settings, code: str, language: str | None) -> dict:
    payload = {"code": code, "language": language}
    timeout = httpx.Timeout(settings.request_timeout_seconds)
    base_url = settings.ml_analyzer_url.rstrip("/")
    summary = "ML summarizer unavailable; generated fallback summary."
    comments: list[str] = []

    async with httpx.AsyncClient(timeout=timeout) as client:
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
