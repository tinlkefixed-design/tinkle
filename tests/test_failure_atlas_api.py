from fastapi.testclient import TestClient
from tinkle.api.main import app

c = TestClient(app)
H = {"X-API-Key": "dev-key"}


def test_failure_atlas_api():
    r = c.post("/api/v1/failure-atlas/record", headers=H, json={
        "failure": "test failure",
        "cause": "test cause",
        "conditions": ["condition"],
        "symptoms": ["symptom"],
        "detection": ["detector"],
        "prevention": ["prevention"],
        "lesson": "lesson",
    })
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "FAILURE_KNOWLEDGE_RECORDED"
    assert body["knowledge"]["cause"] == "test cause"


def test_failure_atlas_requires_auth():
    r = c.post("/api/v1/failure-atlas/record", json={
        "failure": "test failure", "cause": "test cause", "lesson": "lesson"
    })
    assert r.status_code == 401
