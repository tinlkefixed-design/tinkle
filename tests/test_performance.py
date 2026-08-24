import time
from fastapi.testclient import TestClient
from tinkle.api.main import app

client = TestClient(app)

def test_health_performance_smoke():
    start = time.perf_counter()
    for _ in range(50):
        r = client.get("/health")
        assert r.status_code == 200
    elapsed = time.perf_counter() - start
    # A smoke benchmark, not a production SLA.
    assert elapsed < 5.0
