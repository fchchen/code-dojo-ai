from fastapi import APIRouter

from app.models.registry import registry

router = APIRouter(prefix="/api/models", tags=["models"])


@router.get("/status")
def model_status() -> dict:
    return {
        "models": registry.status(),
        "all_ready": registry.all_ready,
    }
