from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.models.embedder import embed
from app.models.reviewer import review
from app.models.summarizer import summarize

router = APIRouter(prefix="/api/analyze", tags=["analyze"])


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
def summarize_code(request: CodeRequest) -> SummarizeResponse:
    result = summarize(request.code)
    if result.get("error") and result.get("summary") is None:
        raise HTTPException(status_code=503, detail=result["error"])
    return SummarizeResponse(**result)


@router.post("/review", response_model=ReviewResponse)
def review_code(request: CodeRequest) -> ReviewResponse:
    result = review(request.code)
    if result.get("error") and result.get("comments") is None:
        raise HTTPException(status_code=503, detail=result["error"])
    return ReviewResponse(**result)


@router.post("/embed", response_model=EmbedResponse)
def embed_code(request: CodeRequest) -> EmbedResponse:
    result = embed(request.code)
    if result.get("error") and result.get("embedding") is None:
        raise HTTPException(status_code=503, detail=result["error"])
    return EmbedResponse(**result)
