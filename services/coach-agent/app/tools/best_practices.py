from app.llm.gemini_client import GeminiClient


async def generate_best_practices(client: GeminiClient, issues: list[str], language: str | None) -> list[str]:
    issues_text = "\n".join(f"- {item}" for item in issues) or "- No explicit issues detected"
    prompt = (
        f"Generate 5 concise best-practice suggestions for {language or 'code'} based on these issues:\n"
        f"{issues_text}\n"
        "Return each item on a new line with no numbering."
    )
    text = await client.generate(prompt)
    lines = [line.strip(" -") for line in text.splitlines() if line.strip()]
    return lines[:5] if lines else ["Keep functions small and test edge cases."]
