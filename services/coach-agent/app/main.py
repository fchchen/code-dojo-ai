from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from app.agent.loop import CoachAgent
from app.config import get_settings
from app.llm.gemini_client import GeminiClient
from app.repository import SubmissionRepository
from app.routers import submissions
from app.tools.analyze_code import close_shared_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    db_path = Path(settings.sqlite_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    repository = SubmissionRepository(settings.sqlite_path)
    await repository.init_db()

    llm_client = GeminiClient(settings)
    app.state.settings = settings
    app.state.repository = repository
    app.state.agent = CoachAgent(settings, llm_client)

    yield

    await close_shared_client()
    await repository.close()


async def health() -> dict:
    return {"status": "healthy"}


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Code Dojo AI - Coach Agent", version="0.1.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(submissions.router)
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
    app.get("/health")(health)
    return app


app = create_app()
