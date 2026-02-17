import asyncio
from contextlib import suppress
import json
from time import perf_counter
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sse_starlette.sse import EventSourceResponse

from app.agent.loop import CoachAgent
from app.monitoring.metrics import ACTIVE_STREAMS, SUBMISSIONS_FAILED, SUBMISSIONS_TOTAL, SUBMISSION_DURATION
from app.repository import SubmissionRepository
from app.schemas import AgentState, AgentStep, SSEEvent, SubmissionListResponse, SubmissionRequest, SubmissionResponse

router = APIRouter(prefix="/api/submissions", tags=["submissions"])


def get_repo(request: Request) -> SubmissionRepository:
    return request.app.state.repository


def get_agent(request: Request) -> CoachAgent:
    return request.app.state.agent


@router.post("", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def create_submission(
    payload: SubmissionRequest,
    repo: SubmissionRepository = Depends(get_repo),
    agent: CoachAgent = Depends(get_agent),
) -> SubmissionResponse:
    submission_id = str(uuid4())
    await repo.create_submission(submission_id, payload.username, payload.language, payload.code)

    start = perf_counter()

    async def emit(step: AgentStep) -> None:
        await repo.add_step(submission_id, step)

    try:
        result = await agent.execute(payload, emit)
        await repo.complete_submission(submission_id, result)
        SUBMISSIONS_TOTAL.inc()
    except Exception as exc:
        await repo.fail_submission(submission_id, str(exc))
        SUBMISSIONS_FAILED.inc()
        raise HTTPException(status_code=500, detail="submission processing failed") from exc
    finally:
        SUBMISSION_DURATION.observe(perf_counter() - start)

    response = await repo.get_submission(submission_id)
    if response is None:
        raise HTTPException(status_code=500, detail="submission not found after completion")
    return response


@router.post("/stream")
async def create_submission_stream(
    payload: SubmissionRequest,
    repo: SubmissionRepository = Depends(get_repo),
    agent: CoachAgent = Depends(get_agent),
) -> EventSourceResponse:
    submission_id = str(uuid4())
    await repo.create_submission(submission_id, payload.username, payload.language, payload.code)
    queue: asyncio.Queue[tuple[str, dict | None]] = asyncio.Queue()
    start = perf_counter()

    async def emit(step: AgentStep) -> None:
        await repo.add_step(submission_id, step)
        await queue.put(
            (
                "agent.step",
                {
                    "submissionId": submission_id,
                    "phase": step.phase.value,
                    "message": step.message,
                    "toolName": step.tool_name,
                    "meta": step.meta,
                    "timestamp": step.timestamp.isoformat(),
                },
            )
        )

    async def worker() -> None:
        try:
            result = await agent.execute(payload, emit)
            await repo.complete_submission(submission_id, result)
            await queue.put(("submission.completed", {"submissionId": submission_id, "result": result.model_dump()}))
            SUBMISSIONS_TOTAL.inc()
        except Exception as exc:
            await repo.fail_submission(submission_id, str(exc))
            await queue.put(("submission.failed", {"submissionId": submission_id, "error": str(exc)}))
            SUBMISSIONS_FAILED.inc()
        finally:
            SUBMISSION_DURATION.observe(perf_counter() - start)
            await queue.put(("done", None))

    task = asyncio.create_task(worker())

    async def event_generator():
        ACTIVE_STREAMS.inc()
        try:
            created_event = SSEEvent(
                event="submission.created",
                data={"submissionId": submission_id, "status": AgentState.EXECUTING.value},
            )
            yield {"event": created_event.event, "data": json.dumps(created_event.data)}

            while True:
                event_name, data = await queue.get()
                if event_name == "done":
                    break
                yield {"event": event_name, "data": json.dumps(data or {})}
        finally:
            ACTIVE_STREAMS.dec()
            if task.done():
                await task
            else:
                task.cancel()
                with suppress(asyncio.CancelledError):
                    await task

    return EventSourceResponse(event_generator())


@router.get("/{submission_id}", response_model=SubmissionResponse)
async def get_submission(submission_id: str, repo: SubmissionRepository = Depends(get_repo)) -> SubmissionResponse:
    submission = await repo.get_submission(submission_id)
    if submission is None:
        raise HTTPException(status_code=404, detail="submission not found")
    return submission


@router.get("", response_model=SubmissionListResponse)
async def list_submissions(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    repo: SubmissionRepository = Depends(get_repo),
) -> SubmissionListResponse:
    items, total = await repo.list_submissions(page, page_size)
    return SubmissionListResponse(items=items, page=page, page_size=page_size, total=total)
