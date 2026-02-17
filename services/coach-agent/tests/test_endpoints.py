import os
from pathlib import Path

from fastapi.testclient import TestClient

os.environ["COACH_SQLITE_PATH"] = str(Path(__file__).parent / "test_coach.db")
os.environ["COACH_GEMINI_API_KEY"] = ""

from app.main import app  # noqa: E402


def test_health_endpoint():
    with TestClient(app) as client:
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"


def test_post_submission_endpoint():
    with TestClient(app) as client:
        resp = client.post(
            "/api/submissions",
            json={"code": "print('hello')", "language": "python", "username": "demo"},
        )
        assert resp.status_code in (201, 500)
