from __future__ import annotations

import time

import torch

from app.models.registry import ModelStatus, registry
from app.monitoring.metrics import INFERENCE_DURATION, INFERENCE_REQUESTS
from app.pipelines.preprocessing import preprocess

MODEL_NAME = "codereviewer"


def review(code: str) -> dict:
    entry = registry.get(MODEL_NAME)
    if entry.status != ModelStatus.READY:
        INFERENCE_REQUESTS.labels(
            model_name=MODEL_NAME, endpoint="review", status="unavailable"
        ).inc()
        return {"comments": None, "error": f"Model not ready: {entry.status.value}"}

    preprocessed = preprocess(code)
    prompt = f"review code quality issues:\n{preprocessed['code']}"

    start = time.time()
    try:
        inputs = entry.tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
        with torch.no_grad():
            outputs = entry.model.generate(
                **inputs, max_new_tokens=256, num_beams=4, early_stopping=True
            )
        comment = entry.tokenizer.decode(outputs[0], skip_special_tokens=True)

        elapsed = time.time() - start
        INFERENCE_DURATION.labels(model_name=MODEL_NAME, endpoint="review").observe(elapsed)
        INFERENCE_REQUESTS.labels(
            model_name=MODEL_NAME, endpoint="review", status="success"
        ).inc()

        return {
            "comments": [comment] if comment else [],
            "language": preprocessed["language"],
            "inference_time_ms": round(elapsed * 1000, 2),
        }
    except Exception as exc:
        INFERENCE_REQUESTS.labels(
            model_name=MODEL_NAME, endpoint="review", status="error"
        ).inc()
        return {"comments": None, "error": str(exc)}
