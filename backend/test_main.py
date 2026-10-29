from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    assert client.get("/api/health").status_code == 200


def test_demo_review_without_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    response = client.post("/api/review", json={"language": "Python", "code": "print('hello')"})
    assert response.status_code == 200
    assert response.json()["source"] == "demo"
    assert "score" in response.json()
