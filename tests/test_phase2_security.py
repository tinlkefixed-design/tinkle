from fastapi.testclient import TestClient
from tinkle.api.main import app
c = TestClient(app)

def test_bad_key():
    r = c.post("/api/v1/route", headers={"X-API-Key":"bad"}, json={"prompt":"x"})
    assert r.status_code == 401

def test_prompt_validation():
    r = c.post("/api/v1/route", headers={"X-API-Key":"dev-key"}, json={"prompt":""})
    assert r.status_code == 422
