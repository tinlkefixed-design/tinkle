from fastapi.testclient import TestClient
from tinkle.api.main import app
c=TestClient(app); H={"X-API-Key":"dev-key"}

def test_reframing_api():
    r=c.post("/api/v1/reframing",headers=H,json={"problem":"minimize cost while maximizing performance"})
    assert r.status_code==200
    assert r.json()["selected_representation"]=="optimization"

def test_reframing_auth():
    assert c.post("/api/v1/reframing",json={"problem":"x"}).status_code==401
