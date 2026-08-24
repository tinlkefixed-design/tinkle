import time
from fastapi.testclient import TestClient
from tinkle.api.main import app
c = TestClient(app)
H = {"X-API-Key":"dev-key"}

def test_router_smoke_performance():
    start = time.perf_counter()
    for _ in range(100):
        r = c.post("/api/v1/route", headers=H, json={"prompt":"test","task_type":"simple"})
        assert r.status_code == 200
    assert time.perf_counter() - start < 8
