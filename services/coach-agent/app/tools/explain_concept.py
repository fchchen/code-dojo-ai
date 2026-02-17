from app.llm.gemini_client import GeminiClient


async def explain_main_concept(client: GeminiClient, issues: list[str], language: str | None) -> str:
    focus = issues[0] if issues else "code quality"
    prompt = (
        f"Explain the key concept behind this {language or 'code'} improvement area in 3 short paragraphs: {focus}."
    )
    return await client.generate(prompt)
