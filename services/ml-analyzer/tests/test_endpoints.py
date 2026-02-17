from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.main import health
from app.routers import analyze as analyze_router
from app.routers import models as models_router
from app.routers.analyze import CodeRequest


@pytest.mark.asyncio
async def test_health_check_reports_status(monkeypatch):
    monkeypatch.setattr("app.main.registry", SimpleNamespace(all_ready=True))
    response = health()
    assert response == {"status": "healthy", "models_ready": True}


def test_model_status_endpoint(monkeypatch):
    fake_registry = SimpleNamespace(
        status=lambda: {"codet5-summarizer": {"model_id": "Salesforce/codet5-small", "status": "ready", "error": None}},
        all_ready=True,
    )
    monkeypatch.setattr(models_router, "registry", fake_registry)

    payload = models_router.model_status()
    assert payload["all_ready"] is True
    assert "codet5-summarizer" in payload["models"]


@pytest.mark.asyncio
async def test_summarize_success(monkeypatch):
    async def fake_run_in_threadpool(_fn, *_args, **_kwargs):
        return {"summary": "This function adds two numbers", "language": "python", "inference_time_ms": 150.0}

    monkeypatch.setattr(analyze_router, "run_in_threadpool", fake_run_in_threadpool)
    response = await analyze_router.summarize_code(CodeRequest(code="def add(a, b): return a + b"))
    assert response.summary == "This function adds two numbers"


@pytest.mark.asyncio
async def test_summarize_model_unavailable(monkeypatch):
    async def fake_run_in_threadpool(_fn, *_args, **_kwargs):
        return {"summary": None, "error": "Model not ready: not_loaded"}

    monkeypatch.setattr(analyze_router, "run_in_threadpool", fake_run_in_threadpool)
    with pytest.raises(HTTPException) as exc_info:
        await analyze_router.summarize_code(CodeRequest(code="x = 1"))
    assert exc_info.value.status_code == 503


def test_summarize_empty_code_rejected():
    with pytest.raises(ValidationError):
        CodeRequest(code="")


@pytest.mark.asyncio
async def test_review_success(monkeypatch):
    async def fake_run_in_threadpool(_fn, *_args, **_kwargs):
        return {"comments": ["Consider using a list comprehension"], "language": "python", "inference_time_ms": 200.0}

    monkeypatch.setattr(analyze_router, "run_in_threadpool", fake_run_in_threadpool)
    response = await analyze_router.review_code(CodeRequest(code="for i in range(10): pass"))
    assert len(response.comments or []) == 1


@pytest.mark.asyncio
async def test_embed_success(monkeypatch):
    async def fake_run_in_threadpool(_fn, *_args, **_kwargs):
        return {"embedding": [0.1] * 768, "dimensions": 768, "language": "python", "inference_time_ms": 50.0}

    monkeypatch.setattr(analyze_router, "run_in_threadpool", fake_run_in_threadpool)
    response = await analyze_router.embed_code(CodeRequest(code="x = 1"))
    assert response.dimensions == 768
