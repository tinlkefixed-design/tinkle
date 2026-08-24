from fastapi.testclient import TestClient
from tinkle.api.main import app
c=TestClient(app); H={"X-API-Key":"dev-key"}

def test_provenance_api():
    d={"claim":"Mars has two moons","source":"NASA","author":"NASA","confidence":0.95,
       "status":"verified","evidence":["observation"],"supporting_sources":["catalog"]}
    r=c.post("/api/v1/provenance/records",headers=H,json=d)
    assert r.status_code==200
    r=c.post("/api/v1/provenance/report",headers=H,json={"claim":"Mars has two moons"})
    assert r.status_code==200 and r.json()["status"]=="verified"

def test_provenance_auth():
    assert c.post("/api/v1/provenance/report",json={"claim":"x"}).status_code==401
