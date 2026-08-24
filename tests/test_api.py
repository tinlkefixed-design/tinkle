from fastapi.testclient import TestClient
from tinkle.api.main import app

client = TestClient(app)
HEADERS = {"X-API-Key": "dev-key"}

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["data"]["phase"] == 33

def test_auth_required():
    r = client.post("/api/v1/tasks", json={"prompt": "x"})
    assert r.status_code in {401, 403}

def test_task_flow():
    r = client.post("/api/v1/tasks", headers=HEADERS, json={"prompt": "اختبار"})
    assert r.status_code == 200
    task = r.json()["task"]
    task_id = task["id"]
    r = client.get(f"/api/v1/tasks/{task_id}", headers=HEADERS)
    assert r.status_code == 200
    r = client.post(f"/api/v1/tasks/{task_id}/run", headers=HEADERS)
    assert r.status_code == 200
    assert r.json()["status"] == "completed"

def test_project_flow():
    r = client.post("/api/v1/projects", headers=HEADERS, json={"name": "Core"})
    assert r.status_code == 200
    project_id = r.json()["id"]
    r = client.get(f"/api/v1/projects/{project_id}", headers=HEADERS)
    assert r.status_code == 200
    r = client.delete(f"/api/v1/projects/{project_id}", headers=HEADERS)
    assert r.status_code == 200

def test_data_export_delete():
    client.post("/api/v1/tasks", headers=HEADERS, json={"prompt": "export me"})
    r = client.get("/api/v1/data/export", headers=HEADERS)
    assert r.status_code == 200
    assert r.json()["owner"] == "default"
    r = client.delete("/api/v1/data", headers=HEADERS)
    assert r.status_code == 200

def test_edge_cases():
    assert client.post("/api/v1/tasks", headers=HEADERS, json={"prompt": ""}).status_code == 422
    assert client.get("/api/v1/tasks/not-a-uuid", headers=HEADERS).status_code == 422
    assert client.get("/api/v1/projects/00000000-0000-0000-0000-000000000000",
                      headers=HEADERS).status_code == 404
