from fastapi.testclient import TestClient
from tinkle.api.main import app
c=TestClient(app); H={"X-API-Key":"dev-key"}

def test_knowledge_ingest_search():
    d={"title":"Doc","source":"unit","content":"Mars has two moons.","metadata":{"project_id":"mars"}}
    r=c.post("/api/v1/knowledge/documents",headers=H,json=d)
    assert r.status_code==200
    r=c.post("/api/v1/knowledge/search",headers=H,json={"query":"Mars moons","project_id":"mars"})
    assert r.status_code==200
    assert r.json()["status"]=="SUPPORTED"

def test_knowledge_auth():
    assert c.post("/api/v1/knowledge/search",json={"query":"x"}).status_code==401
