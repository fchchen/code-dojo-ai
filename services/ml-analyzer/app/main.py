import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from app.models.registry import registry
from app.routers import analyze, models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    skip_model_load = os.getenv("ML_SKIP_MODEL_LOAD", "").strip().lower() in {"1", "true", "yes"}
    if skip_model_load:
        logger.info("Skipping model registration/loading because ML_SKIP_MODEL_LOAD is set")
    else:
        logger.info("Registering models...")
        registry.register("codet5-summarizer", "Salesforce/codet5-small", "summarization")
        registry.register("codereviewer", "Salesforce/codet5-base", "code-review")
        registry.register("codeberta-embedder", "huggingface/CodeBERTa-small-v1", "embedding")
        logger.info("Loading models...")
        registry.load_all()
        logger.info("Model status: %s", registry.status())
    yield
    logger.info("Shutting down ML Analyzer")


def health() -> dict:
    ready = registry.all_ready
    return {"status": "healthy" if ready else "degraded", "models_ready": ready}


def _cors_origins() -> list[str]:
    return [
        item.strip()
        for item in os.getenv(
            "ML_CORS_ORIGINS",
            "http://localhost,http://127.0.0.1,http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if item.strip()
    ]


def create_app() -> FastAPI:
    app = FastAPI(title="Code Dojo AI - ML Analyzer", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(),
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(analyze.router)
    app.include_router(models.router)

    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
    app.get("/health")(health)
    return app


app = create_app()
