from datetime import datetime, timezone

import pytest

from app.routers import submissions as submissions_router
from app.schemas import AgentState, CoachingResult, SubmissionRequest, SubmissionResponse


class FakeRepo:
    def __init__(self):
        self._submission_id: str | None = None
        self._result: CoachingResult | None = None

    async def create_submission(self, submission_id: str, username: str, language: str | None, code: str) -> None:
        self._submission_id = submission_id

    async def add_step(self, submission_id: str, step) -> None:
        return None

    async def complete_submission(self, submission_id: str, result: CoachingResult) -> None:
        self._result = result

    async def fail_submission(self, submission_id: str, error: str) -> None:
        raise AssertionError(f"Unexpected failure: {error}")

    async def get_submission(self, submission_id: str) -> SubmissionResponse | None:
        if submission_id != self._submission_id or self._result is None:
            return None
        now = datetime.now(timezone.utc)
        return SubmissionResponse(
            id=submission_id,
            username="demo",
            language="python",
            status=AgentState.COMPLETE,
            result=self._result,
            error=None,
            created_at=now,
            updated_at=now,
        )


class FakeAgent:
    async def execute(self, request: SubmissionRequest, emit) -> CoachingResult:
        return CoachingResult(
            summary="Stub summary",
            score=88,
            issues=["Stub issue"],
            improved_code="print('improved')",
            best_practices=["Stub practice"],
            concept_explanation="Stub concept",
        )


@pytest.mark.asyncio
async def test_health_endpoint():
    from app.main import health

    response = await health()
    assert response["status"] == "healthy"


@pytest.mark.asyncio
async def test_post_submission_endpoint():
    payload = SubmissionRequest(code="print('hello')", language="python", username="demo")
    response = await submissions_router.create_submission(payload, repo=FakeRepo(), agent=FakeAgent())

    assert response.status == AgentState.COMPLETE
    assert response.result is not None
    assert response.result.summary == "Stub summary"
