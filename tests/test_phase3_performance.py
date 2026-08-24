import time
from fastapi.testclient import TestClient
from tinkle.api.main import app
c=TestClient(app); H={"X-API-Key":"dev-key"}
def test_tool_latency_smoke():
    t=time.perf_counter()
    for _ in range(100):
        assert c.post("/api/v1/tools/execute",headers=H,json={"tool":"calculator","input":{"expression":"1+1"}}).status_code==200
    assert time.perf_counter()-t < 8
