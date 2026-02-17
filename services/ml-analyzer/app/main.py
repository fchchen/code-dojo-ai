import logging
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
    logger.info("Registering models...")
    registry.register("codet5-summarizer", "Salesforce/codet5-small", "summarization")
    registry.register("codereviewer", "microsoft/codereviewer", "code-review")
    registry.register("codeberta-embedder", "huggingface/CodeBERTa-small-v1", "embedding")
    logger.info("Loading models...")
    registry.load_all()
    logger.info("Model status: %s", registry.status())
    yield
    logger.info("Shutting down ML Analyzer")


app = FastAPI(title="Code Dojo AI - ML Analyzer", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router)
app.include_router(models.router)

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/health")
def health() -> dict:
    return {"status": "healthy", "models_ready": registry.all_ready}
