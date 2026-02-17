from collections.abc import Awaitable, Callable

from app.config import Settings
from app.llm.gemini_client import GeminiClient
from app.schemas import AgentState, AgentStep, CoachingResult, SubmissionRequest
from app.tools.analyze_code import analyze_code_quality
from app.tools.best_practices import generate_best_practices
from app.tools.explain_concept import explain_main_concept
from app.tools.generate_example import generate_improved_code

StepEmitter = Callable[[AgentStep], Awaitable[None]]


class CoachAgent:
    def __init__(self, settings: Settings, llm_client: GeminiClient):
        self._settings = settings
        self._llm = llm_client

    async def execute(self, request: SubmissionRequest, emit: StepEmitter) -> CoachingResult:
        context: dict[str, object] = {}

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
        analysis = await analyze_code_quality(self._settings, request.code, request.language)
        context["analysis"] = analysis

        issues = list(analysis.get("issues", []))
        summary = str(analysis.get("summary", "No summary available"))

        await emit(
            AgentStep(
                phase=AgentState.REFLECTING,
                message="Generating best practices and concept explanation.",
            )
        )
        best_practices = await generate_best_practices(self._llm, issues, request.language)
        concept = await explain_main_concept(self._llm, issues, request.language)

        await emit(
            AgentStep(
                phase=AgentState.SYNTHESIZING,
                message="Synthesizing improved code sample.",
                tool_name="generate_improved_code",
            )
        )
        improved_code = await generate_improved_code(self._llm, request.code, request.language, issues)

        score = max(40, min(95, 90 - (len(issues) * 7)))
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
