from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client with mocked model loading."""
    with patch("app.models.registry.registry") as mock_registry:
        mock_registry.status.return_value = {}
        mock_registry.all_ready = True

        from app.main import app
        with TestClient(app) as c:
            yield c, mock_registry


class TestHealthEndpoint:
    def test_health_check(self, client):
        c, mock_reg = client
        response = c.get("/health")
        assert response.status_code == 200
        assert "status" in response.json()


class TestModelStatusEndpoint:
    def test_returns_model_status(self, client):
        c, mock_reg = client
        mock_reg.status.return_value = {
            "codet5-summarizer": {"model_id": "Salesforce/codet5-small", "status": "ready", "error": None},
        }
        mock_reg.all_ready = True
        response = c.get("/api/models/status")
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        assert data["all_ready"] is True


class TestSummarizeEndpoint:
    @patch("app.routers.analyze.summarize")
    def test_summarize_success(self, mock_summarize, client):
        mock_summarize.return_value = {
            "summary": "This function adds two numbers",
            "language": "python",
            "inference_time_ms": 150.0,
        }
        c, _ = client
        response = c.post("/api/analyze/summarize", json={"code": "def add(a, b): return a + b"})
        assert response.status_code == 200
        assert response.json()["summary"] == "This function adds two numbers"

    @patch("app.routers.analyze.summarize")
    def test_summarize_model_unavailable(self, mock_summarize, client):
        mock_summarize.return_value = {"summary": None, "error": "Model not ready: not_loaded"}
        c, _ = client
        response = c.post("/api/analyze/summarize", json={"code": "x = 1"})
        assert response.status_code == 503

    def test_summarize_empty_code_rejected(self, client):
        c, _ = client
        response = c.post("/api/analyze/summarize", json={"code": ""})
        assert response.status_code == 422


class TestReviewEndpoint:
    @patch("app.routers.analyze.review")
    def test_review_success(self, mock_review, client):
        mock_review.return_value = {
            "comments": ["Consider using a list comprehension"],
            "language": "python",
            "inference_time_ms": 200.0,
        }
        c, _ = client
        response = c.post("/api/analyze/review", json={"code": "for i in range(10): pass"})
        assert response.status_code == 200
        assert len(response.json()["comments"]) == 1


class TestEmbedEndpoint:
    @patch("app.routers.analyze.embed")
    def test_embed_success(self, mock_embed, client):
        mock_embed.return_value = {
            "embedding": [0.1] * 768,
            "dimensions": 768,
            "language": "python",
            "inference_time_ms": 50.0,
        }
        c, _ = client
        response = c.post("/api/analyze/embed", json={"code": "x = 1"})
        assert response.status_code == 200
        assert response.json()["dimensions"] == 768
