from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from transformers import AutoModel, AutoTokenizer, T5ForConditionalGeneration

from app.monitoring.metrics import MODEL_LOAD_TIME, MODELS_LOADED

logger = logging.getLogger(__name__)


class ModelStatus(str, Enum):
    NOT_LOADED = "not_loaded"
    LOADING = "loading"
    READY = "ready"
    ERROR = "error"


@dataclass
class ModelEntry:
    name: str
    model_id: str
    task: str
    status: ModelStatus = ModelStatus.NOT_LOADED
    model: Any = field(default=None, repr=False)
    tokenizer: Any = field(default=None, repr=False)
    error: str | None = None


class ModelRegistry:
    def __init__(self) -> None:
        self._models: dict[str, ModelEntry] = {}

    def register(self, name: str, model_id: str, task: str) -> None:
        self._models[name] = ModelEntry(name=name, model_id=model_id, task=task)

    def load(self, name: str) -> None:
        entry = self._models.get(name)
        if entry is None:
            raise KeyError(f"Model '{name}' is not registered")

        entry.status = ModelStatus.LOADING
        start = time.time()
        try:
            if "t5" in entry.model_id.lower() or "codet5" in entry.model_id.lower():
                entry.model = T5ForConditionalGeneration.from_pretrained(entry.model_id)
            else:
                entry.model = AutoModel.from_pretrained(entry.model_id)
            entry.tokenizer = AutoTokenizer.from_pretrained(entry.model_id)

            entry.model.eval()
            entry.status = ModelStatus.READY
            elapsed = time.time() - start
            MODEL_LOAD_TIME.labels(model_name=name).observe(elapsed)
            MODELS_LOADED.inc()
            logger.info("Loaded model %s in %.2fs", name, elapsed)
        except Exception as exc:
            entry.status = ModelStatus.ERROR
            entry.error = str(exc)
            logger.error("Failed to load model %s: %s", name, exc)

    def load_all(self) -> None:
        for name in self._models:
            self.load(name)

    def get(self, name: str) -> ModelEntry:
        entry = self._models.get(name)
        if entry is None:
            raise KeyError(f"Model '{name}' is not registered")
        return entry

    def is_ready(self, name: str) -> bool:
        entry = self._models.get(name)
        return entry is not None and entry.status == ModelStatus.READY

    def status(self) -> dict[str, dict]:
        return {
            name: {"model_id": e.model_id, "status": e.status.value, "error": e.error}
            for name, e in self._models.items()
        }

    @property
    def all_ready(self) -> bool:
        return all(e.status == ModelStatus.READY for e in self._models.values())


registry = ModelRegistry()
