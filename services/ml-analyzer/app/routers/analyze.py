from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/analyze", tags=["analyze"])


def _summarize_fn():
    from app.models.summarizer import summarize

    return summarize


def _review_fn():
    from app.models.reviewer import review

    return review


def _embed_fn():
    from app.models.embedder import embed

    return embed


class CodeRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=10000)
    language: str | None = None


class SummarizeResponse(BaseModel):
    summary: str | None
    language: str | None = None
    inference_time_ms: float | None = None
    error: str | None = None


class ReviewResponse(BaseModel):
    comments: list[str] | None
    language: str | None = None
    inference_time_ms: float | None = None
    error: str | None = None


class EmbedResponse(BaseModel):
    embedding: list[float] | None
    dimensions: int | None = None
    language: str | None = None
    inference_time_ms: float | None = None
    error: str | None = None


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_code(request: CodeRequest) -> SummarizeResponse:
    result = await run_in_threadpool(_summarize_fn(), request.code)
    if result.get("error") and result.get("summary") is None:
        raise HTTPException(status_code=503, detail=result["error"])
    return SummarizeResponse(**result)


@router.post("/review", response_model=ReviewResponse)
async def review_code(request: CodeRequest) -> ReviewResponse:
    result = await run_in_threadpool(_review_fn(), request.code)
    if result.get("error") and result.get("comments") is None:
        raise HTTPException(status_code=503, detail=result["error"])
    return ReviewResponse(**result)


@router.post("/embed", response_model=EmbedResponse)
async def embed_code(request: CodeRequest) -> EmbedResponse:
    result = await run_in_threadpool(_embed_fn(), request.code)
    if result.get("error") and result.get("embedding") is None:
        raise HTTPException(status_code=503, detail=result["error"])
    return EmbedResponse(**result)
