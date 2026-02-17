from collections.abc import Awaitable, Callable
from typing import Any

from app.tools.analyze_code import analyze_code_quality
from app.tools.best_practices import generate_best_practices
from app.tools.explain_concept import explain_main_concept
from app.tools.generate_example import generate_improved_code

ToolFn = Callable[..., Awaitable[Any]]

TOOL_REGISTRY: dict[str, ToolFn] = {
    "analyze_code_quality": analyze_code_quality,
    "generate_best_practices": generate_best_practices,
    "generate_improved_code": generate_improved_code,
    "explain_main_concept": explain_main_concept,
}

TOOL_DESCRIPTIONS: dict[str, str] = {
    "analyze_code_quality": "Summarize and review code via ML Analyzer",
    "generate_best_practices": "Produce targeted best-practice suggestions",
    "generate_improved_code": "Generate improved example implementation",
    "explain_main_concept": "Explain important improvement concept",
}
