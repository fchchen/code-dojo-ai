from app.llm.gemini_client import GeminiClient


async def generate_improved_code(
    client: GeminiClient,
    code: str,
    language: str | None,
    issues: list[str],
) -> str:
    issues_text = "\n".join(f"- {item}" for item in issues) or "- Improve clarity and maintainability"
    prompt = (
        f"Rewrite this {language or 'code'} to address the issues below. "
        "Return only code.\n"
        f"Issues:\n{issues_text}\n"
        f"Original code:\n{code}"
    )
    return await client.generate(prompt)
