from fastapi.testclient import TestClient
from tinkle.api.main import app

client = TestClient(app)
HEADERS = {"X-API-Key": "dev-key"}


def test_multi_agent_api():
    r = client.post("/api/v1/multi-agent/run", headers=HEADERS, json={"goal": "Solve a problem"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] in {"FAILED", "PARTIAL", "COMPLETED"}
    assert len(body["agents"]) == 10
    assert len(body["agents"]) == 10
    assert body["agents"][0]["role"] == "Researcher"


def test_multi_agent_auth_required():
    r = client.post("/api/v1/multi-agent/run", json={"goal": "x"})
    assert r.status_code in {401, 403}
