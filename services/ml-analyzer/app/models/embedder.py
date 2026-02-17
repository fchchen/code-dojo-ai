from __future__ import annotations

import time

import torch

from app.models.registry import ModelStatus, registry
from app.monitoring.metrics import INFERENCE_DURATION, INFERENCE_REQUESTS
from app.pipelines.preprocessing import preprocess

MODEL_NAME = "codeberta-embedder"


def embed(code: str) -> dict:
    entry = registry.get(MODEL_NAME)
    if entry.status != ModelStatus.READY:
        INFERENCE_REQUESTS.labels(
            model_name=MODEL_NAME, endpoint="embed", status="unavailable"
        ).inc()
        return {"embedding": None, "error": f"Model not ready: {entry.status.value}"}

    preprocessed = preprocess(code)

    start = time.time()
    try:
        inputs = entry.tokenizer(
            preprocessed["code"], return_tensors="pt", max_length=512,
            truncation=True, padding=True,
        )
        with torch.no_grad():
            outputs = entry.model(**inputs)

        # Mean pooling over token embeddings
        token_embeddings = outputs.last_hidden_state
        attention_mask = inputs["attention_mask"].unsqueeze(-1)
        masked = token_embeddings * attention_mask
        embedding = masked.sum(dim=1) / attention_mask.sum(dim=1)
        embedding_list = embedding.squeeze().tolist()

        elapsed = time.time() - start
        INFERENCE_DURATION.labels(model_name=MODEL_NAME, endpoint="embed").observe(elapsed)
        INFERENCE_REQUESTS.labels(
            model_name=MODEL_NAME, endpoint="embed", status="success"
        ).inc()

        return {
            "embedding": embedding_list,
            "dimensions": len(embedding_list),
            "language": preprocessed["language"],
            "inference_time_ms": round(elapsed * 1000, 2),
        }
    except Exception as exc:
        INFERENCE_REQUESTS.labels(
            model_name=MODEL_NAME, endpoint="embed", status="error"
        ).inc()
        return {"embedding": None, "error": str(exc)}
