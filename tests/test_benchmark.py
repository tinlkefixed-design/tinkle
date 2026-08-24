def test_core_benchmark_contract():
    # Benchmark contract for Phase 1: the core request path must exist,
    # authenticate, create a task, execute the lifecycle, and return structure.
    from fastapi.testclient import TestClient
    from tinkle.api.main import app
    c = TestClient(app)
    h = {"X-API-Key": "dev-key"}
    r = c.post("/api/v1/tasks", headers=h, json={"prompt": "benchmark"})
    assert r.status_code == 200
    task_id = r.json()["task"]["id"]
    r = c.post(f"/api/v1/tasks/{task_id}/run", headers=h)
    assert r.status_code == 200
    assert r.json()["status"] == "completed"
