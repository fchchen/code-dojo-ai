import pytest

from app.agent.loop import CoachAgent, TOOL_REGISTRY
from app.config import Settings
from app.llm.gemini_client import GeminiClient
from app.schemas import AgentState, SubmissionRequest


@pytest.mark.asyncio
async def test_agent_loop_completes(monkeypatch):
    async def fake_analysis(settings, code, language):
        return {"summary": "Summary", "issues": ["Issue A"]}

    async def fake_practices(client, issues, language):
        return ["Practice"]

    async def fake_concept(client, issues, language):
        return "Concept"

    async def fake_code(client, code, language, issues):
        return "improved()"

    monkeypatch.setitem(TOOL_REGISTRY, "analyze_code_quality", fake_analysis)
    monkeypatch.setitem(TOOL_REGISTRY, "generate_best_practices", fake_practices)
    monkeypatch.setitem(TOOL_REGISTRY, "explain_main_concept", fake_concept)
    monkeypatch.setitem(TOOL_REGISTRY, "generate_improved_code", fake_code)

    agent = CoachAgent(Settings(), GeminiClient(Settings(gemini_api_key=None)))
    steps = []

    async def emit(step):
        steps.append(step)

    result = await agent.execute(SubmissionRequest(code="x=1"), emit)

    assert result.summary == "Summary"
    assert result.improved_code == "improved()"
    assert steps[-1].phase == AgentState.COMPLETE
