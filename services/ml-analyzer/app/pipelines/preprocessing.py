from __future__ import annotations

import re

LANGUAGE_PATTERNS: dict[str, list[str]] = {
    "python": [r"\bdef \w+", r"\bimport \w+", r"\bclass \w+.*:"],
    "java": [r"\bpublic\s+class\b", r"\bprivate\b", r"\bSystem\.out"],
    "javascript": [r"\bconst \w+", r"\bfunction\b", r"\bconsole\.log\b", r"=>"],
    "typescript": [r"\binterface \w+", r":\s*(string|number|boolean)\b", r"\bconst \w+.*:\s*\w+"],
}

MAX_CODE_LENGTH = 512


def detect_language(code: str) -> str:
    scores: dict[str, int] = {}
    for lang, patterns in LANGUAGE_PATTERNS.items():
        scores[lang] = sum(1 for p in patterns if re.search(p, code))
    best = max(scores, key=lambda k: scores[k])
    return best if scores[best] > 0 else "unknown"


def truncate_code(code: str, max_tokens: int = MAX_CODE_LENGTH) -> str:
    lines = code.splitlines()
    result: list[str] = []
    token_count = 0
    for line in lines:
        line_tokens = len(line.split())
        if token_count + line_tokens > max_tokens:
            break
        result.append(line)
        token_count += line_tokens
    return "\n".join(result) if result else lines[0] if lines else code


def preprocess(code: str, max_tokens: int = MAX_CODE_LENGTH) -> dict:
    language = detect_language(code)
    truncated = truncate_code(code, max_tokens)
    return {
        "code": truncated,
        "language": language,
        "original_length": len(code),
        "truncated": len(truncated) < len(code),
    }
