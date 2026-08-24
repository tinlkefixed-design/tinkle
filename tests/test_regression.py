from fastapi.testclient import TestClient
from tinkle.api.main import app

def test_regression_core_contract():
    c = TestClient(app)
    h = {"X-API-Key": "dev-key"}
    assert c.get("/health").json()["ok"] is True
    task = c.post("/api/v1/tasks", headers=h, json={"prompt": "regression"}).json()["task"]
    assert c.post(f"/api/v1/tasks/{task['id']}/run", headers=h).json()["status"] == "completed"
