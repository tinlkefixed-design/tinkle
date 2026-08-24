from fastapi.testclient import TestClient
from tinkle.api.main import app
c=TestClient(app); H={"X-API-Key":"dev-key"}

def test_plan_api():
    r=c.post("/api/v1/metamind/plan",headers=H,json={"prompt":"research quantum computing"})
    assert r.status_code==200
    assert r.json()["task_type"]=="research"

def test_route_hint_api():
    r=c.post("/api/v1/metamind/route-hint",headers=H,json={"prompt":"write python code"})
    assert r.status_code==200
    assert r.json()["task_type"]=="coding"

def test_auth():
    assert c.post("/api/v1/metamind/plan",json={"prompt":"hello"}).status_code==401
