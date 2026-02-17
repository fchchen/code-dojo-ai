import asyncio
from collections.abc import Awaitable, Callable

from app.config import Settings
from app.llm.gemini_client import GeminiClient
from app.schemas import AgentState, AgentStep, CoachingResult, SubmissionRequest
from app.tools.registry import TOOL_REGISTRY

StepEmitter = Callable[[AgentStep], Awaitable[None]]


class CoachAgent:
    def __init__(self, settings: Settings, llm_client: GeminiClient):
        self._settings = settings
        self._llm = llm_client

    async def execute(self, request: SubmissionRequest, emit: StepEmitter) -> CoachingResult:
        context: dict[str, object] = {}
        analyze_tool = TOOL_REGISTRY["analyze_code_quality"]
        best_practices_tool = TOOL_REGISTRY["generate_best_practices"]
        explain_tool = TOOL_REGISTRY["explain_main_concept"]
        improved_code_tool = TOOL_REGISTRY["generate_improved_code"]

        await emit(
            AgentStep(
                phase=AgentState.PLANNING,
                message="Planning analysis strategy for submission.",
            )
        )

        await emit(
            AgentStep(
                phase=AgentState.EXECUTING,
                message="Running ML analyzer summarize/review tools.",
                tool_name="analyze_code_quality",
            )
        )
        analysis = await analyze_tool(self._settings, request.code, request.language)
        context["analysis"] = analysis

        issues = list(analysis.get("issues", []))
        summary = str(analysis.get("summary", "No summary available"))

        await emit(
            AgentStep(
                phase=AgentState.REFLECTING,
                message="Generating best practices and concept explanation.",
            )
        )
        best_practices, concept = await asyncio.gather(
            best_practices_tool(self._llm, issues, request.language),
            explain_tool(self._llm, issues, request.language),
        )

        await emit(
            AgentStep(
                phase=AgentState.SYNTHESIZING,
                message="Synthesizing improved code sample.",
                tool_name="generate_improved_code",
            )
        )
        improved_code = await improved_code_tool(self._llm, request.code, request.language, issues)

        score = self._score_from_issue_count(len(issues))
        result = CoachingResult(
            summary=summary,
            score=score,
            issues=issues,
            improved_code=improved_code,
            best_practices=best_practices,
            concept_explanation=concept,
        )

        await emit(
            AgentStep(
                phase=AgentState.COMPLETE,
                message="Coaching analysis complete.",
            )
        )
        return result

    @staticmethod
    def _score_from_issue_count(issue_count: int) -> int:
        if issue_count <= 0:
            return 92
        if issue_count <= 2:
            return 82
        if issue_count <= 4:
            return 72
        return 62
