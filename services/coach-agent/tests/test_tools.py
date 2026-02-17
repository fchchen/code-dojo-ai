import pytest
import respx
from httpx import Response

from app.config import Settings
from app.tools.analyze_code import analyze_code_quality, close_shared_client


@pytest.fixture(autouse=True)
async def cleanup_analyzer_client():
    yield
    await close_shared_client()


@pytest.mark.asyncio
@respx.mock
async def test_analyze_code_calls_ml_analyzer():
    settings = Settings(ml_analyzer_url="http://ml-analyzer:8001")
    respx.post("http://ml-analyzer:8001/api/analyze/summarize").mock(
        return_value=Response(200, json={"summary": "Looks good"})
    )
    respx.post("http://ml-analyzer:8001/api/analyze/review").mock(
        return_value=Response(200, json={"comments": ["Handle edge cases"]})
    )

    result = await analyze_code_quality(settings, "print('x')", "python")

    assert result["summary"] == "Looks good"
    assert result["issues"] == ["Handle edge cases"]


@pytest.mark.asyncio
@respx.mock
async def test_analyze_code_falls_back_when_upstream_unavailable():
    settings = Settings(ml_analyzer_url="http://ml-analyzer:8001")
    respx.post("http://ml-analyzer:8001/api/analyze/summarize").mock(
        return_value=Response(503, json={"detail": "model unavailable"})
    )
    respx.post("http://ml-analyzer:8001/api/analyze/review").mock(
        return_value=Response(503, json={"detail": "model unavailable"})
    )

    result = await analyze_code_quality(settings, "print('x')", "python")

    assert result["summary"].startswith("ML summarizer unavailable")
    assert result["issues"] == ["Unable to fetch detailed review comments; focus on readability and tests."]
