import json
from datetime import datetime, timezone

import aiosqlite

from app.schemas import AgentState, AgentStep, CoachingResult, SubmissionResponse


class SubmissionRepository:
    def __init__(self, db_path: str):
        self._db_path = db_path

    async def init_db(self) -> None:
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS submissions (
                    id TEXT PRIMARY KEY,
                    username TEXT NOT NULL,
                    language TEXT,
                    code TEXT NOT NULL,
                    status TEXT NOT NULL,
                    summary TEXT,
                    score INTEGER,
                    issues_json TEXT,
                    improved_code TEXT,
                    best_practices_json TEXT,
                    concept_explanation TEXT,
                    error TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS submission_steps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    submission_id TEXT NOT NULL,
                    phase TEXT NOT NULL,
                    tool_name TEXT,
                    message TEXT NOT NULL,
                    event_ts TEXT NOT NULL,
                    meta_json TEXT,
                    FOREIGN KEY(submission_id) REFERENCES submissions(id)
                )
                """
            )
            await db.commit()

    async def create_submission(self, submission_id: str, username: str, language: str | None, code: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                """
                INSERT INTO submissions (
                    id, username, language, code, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    submission_id,
                    username,
                    language,
                    code,
                    AgentState.EXECUTING.value,
                    now,
                    now,
                ),
            )
            await db.commit()

    async def add_step(self, submission_id: str, step: AgentStep) -> None:
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                """
                INSERT INTO submission_steps (
                    submission_id, phase, tool_name, message, event_ts, meta_json
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    submission_id,
                    step.phase.value,
                    step.tool_name,
                    step.message,
                    step.timestamp.isoformat(),
                    json.dumps(step.meta) if step.meta else None,
                ),
            )
            await db.execute(
                "UPDATE submissions SET updated_at = ? WHERE id = ?",
                (datetime.now(timezone.utc).isoformat(), submission_id),
            )
            await db.commit()

    async def complete_submission(self, submission_id: str, result: CoachingResult) -> None:
        now = datetime.now(timezone.utc).isoformat()
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                """
                UPDATE submissions
                SET status = ?,
                    summary = ?,
                    score = ?,
                    issues_json = ?,
                    improved_code = ?,
                    best_practices_json = ?,
                    concept_explanation = ?,
                    error = NULL,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    AgentState.COMPLETE.value,
                    result.summary,
                    result.score,
                    json.dumps(result.issues),
                    result.improved_code,
                    json.dumps(result.best_practices),
                    result.concept_explanation,
                    now,
                    submission_id,
                ),
            )
            await db.commit()

    async def fail_submission(self, submission_id: str, error: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                """
                UPDATE submissions
                SET status = ?, error = ?, updated_at = ?
                WHERE id = ?
                """,
                (AgentState.FAILED.value, error, now, submission_id),
            )
            await db.commit()

    async def get_submission(self, submission_id: str) -> SubmissionResponse | None:
        async with aiosqlite.connect(self._db_path) as db:
            cursor = await db.execute(
                """
                SELECT id, username, language, status, summary, score, issues_json,
                       improved_code, best_practices_json, concept_explanation, error,
                       created_at, updated_at
                FROM submissions WHERE id = ?
                """,
                (submission_id,),
            )
            row = await cursor.fetchone()
        if row is None:
            return None
        return self._to_submission_response(row)

    async def list_submissions(self, page: int, page_size: int) -> tuple[list[SubmissionResponse], int]:
        offset = (page - 1) * page_size
        async with aiosqlite.connect(self._db_path) as db:
            total_cursor = await db.execute("SELECT COUNT(*) FROM submissions")
            total_row = await total_cursor.fetchone()
            rows_cursor = await db.execute(
                """
                SELECT id, username, language, status, summary, score, issues_json,
                       improved_code, best_practices_json, concept_explanation, error,
                       created_at, updated_at
                FROM submissions
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                (page_size, offset),
            )
            rows = await rows_cursor.fetchall()
        total = int(total_row[0] if total_row else 0)
        return [self._to_submission_response(row) for row in rows], total

    @staticmethod
    def _to_submission_response(row: tuple) -> SubmissionResponse:
        (
            submission_id,
            username,
            language,
            status,
            summary,
            score,
            issues_json,
            improved_code,
            best_practices_json,
            concept_explanation,
            error,
            created_at,
            updated_at,
        ) = row

        result = None
        if status == AgentState.COMPLETE.value:
            result = CoachingResult(
                summary=summary or "",
                score=score or 0,
                issues=json.loads(issues_json or "[]"),
                improved_code=improved_code or "",
                best_practices=json.loads(best_practices_json or "[]"),
                concept_explanation=concept_explanation,
            )

        return SubmissionResponse(
            id=submission_id,
            username=username,
            language=language,
            status=AgentState(status),
            result=result,
            error=error,
            created_at=datetime.fromisoformat(created_at),
            updated_at=datetime.fromisoformat(updated_at),
        )
