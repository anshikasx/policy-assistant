from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_query_returns_expected_shape():
    response = client.post("/query", json={"question": "What is the leave policy?"})
    assert response.status_code == 200
    body = response.json()
    assert "answer" in body
    assert isinstance(body["citations"], list)
    assert body["latency_ms"] >= 0


def test_query_rejects_short_question():
    response = client.post("/query", json={"question": "hi"})
    assert response.status_code == 422