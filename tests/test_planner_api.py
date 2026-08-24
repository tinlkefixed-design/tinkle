from fastapi.testclient import TestClient
from tinkle.api.main import app

client = TestClient(app)
HEADERS = {"X-API-Key": "dev-key"}


def test_planner_api():
    r = client.post("/api/v1/planner/plan", headers=HEADERS, json={"goal": "Plan a verified task"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "PLANNED"
    assert len(body["tasks"]) == 4
    assert body["verification"]["name"] == "VERIFICATION"
    assert body["final_result"]["name"] == "FINAL RESULT"


def test_planner_auth_required():
    r = client.post("/api/v1/planner/plan", json={"goal": "x"})
    assert r.status_code in {401, 403}
