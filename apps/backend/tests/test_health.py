from app.main import app
from fastapi.testclient import TestClient


def test_health():
    client = TestClient(app)
    res = client.get("/healthz")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
