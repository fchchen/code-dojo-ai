from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class AgentState(str, Enum):
    PLANNING = "planning"
    EXECUTING = "executing"
    REFLECTING = "reflecting"
    SYNTHESIZING = "synthesizing"
    COMPLETE = "complete"
    FAILED = "failed"


class SubmissionRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=10000)
    language: str | None = None
    username: str = Field(default="demo", min_length=1, max_length=128)

    @field_validator("code")
    @classmethod
    def no_blank_code(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("code must not be blank")
        return value


class AgentStep(BaseModel):
    phase: AgentState
    message: str
    tool_name: str | None = None
    meta: dict[str, Any] | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CoachingResult(BaseModel):
    summary: str
    score: int = Field(..., ge=0, le=100)
    issues: list[str] = Field(default_factory=list)
    improved_code: str
    best_practices: list[str] = Field(default_factory=list)
    concept_explanation: str | None = None


class SubmissionResponse(BaseModel):
    id: str
    username: str
    language: str | None = None
    status: AgentState
    result: CoachingResult | None = None
    error: str | None = None
    created_at: datetime
    updated_at: datetime


class SubmissionListResponse(BaseModel):
    items: list[SubmissionResponse]
    page: int
    page_size: int
    total: int


class SSEEvent(BaseModel):
    event: str
    data: dict[str, Any]
