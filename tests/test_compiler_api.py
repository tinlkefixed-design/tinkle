from fastapi.testclient import TestClient
from tinkle.api.main import app

c = TestClient(app)
H = {"X-API-Key": "dev-key"}


def test_compiler_api():
    r = c.post("/api/v1/compiler/compile", headers=H, json={"problem": "calculate x = 5"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "COMPILED"
    assert "structured_problem" in body


def test_compiler_requires_auth():
    r = c.post("/api/v1/compiler/compile", json={"problem": "calculate x = 5"})
    assert r.status_code in (401, 403)
