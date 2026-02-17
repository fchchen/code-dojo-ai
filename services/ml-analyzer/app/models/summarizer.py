from __future__ import annotations

import time

import torch

from app.models.registry import ModelStatus, registry
from app.monitoring.metrics import INFERENCE_DURATION, INFERENCE_REQUESTS
from app.pipelines.preprocessing import preprocess

MODEL_NAME = "codet5-summarizer"


def summarize(code: str) -> dict:
    entry = registry.get(MODEL_NAME)
    if entry.status != ModelStatus.READY:
        INFERENCE_REQUESTS.labels(
            model_name=MODEL_NAME, endpoint="summarize", status="unavailable"
        ).inc()
        return {"summary": None, "error": f"Model not ready: {entry.status.value}"}

    preprocessed = preprocess(code)
    input_text = f"summarize: {preprocessed['code']}"

    start = time.time()
    try:
        inputs = entry.tokenizer(
            input_text, return_tensors="pt", max_length=512, truncation=True
        )
        with torch.no_grad():
            outputs = entry.model.generate(
                **inputs, max_new_tokens=128, num_beams=4, early_stopping=True
            )
        summary = entry.tokenizer.decode(outputs[0], skip_special_tokens=True)

        elapsed = time.time() - start
        INFERENCE_DURATION.labels(model_name=MODEL_NAME, endpoint="summarize").observe(elapsed)
        INFERENCE_REQUESTS.labels(
            model_name=MODEL_NAME, endpoint="summarize", status="success"
        ).inc()

        return {
            "summary": summary,
            "language": preprocessed["language"],
            "inference_time_ms": round(elapsed * 1000, 2),
        }
    except Exception as exc:
        INFERENCE_REQUESTS.labels(
            model_name=MODEL_NAME, endpoint="summarize", status="error"
        ).inc()
        return {"summary": None, "error": str(exc)}
