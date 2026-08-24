from fastapi.testclient import TestClient
from tinkle.api.main import app

client = TestClient(app)

def test_bad_credentials_do_not_create_task():
    r = client.post("/api/v1/tasks", headers={"X-API-Key": "bad"}, json={"prompt": "x"})
    assert r.status_code in {401, 403}

def test_large_prompt_rejected():
    prompt = "x" * 10001
    r = client.post("/api/v1/tasks", headers={"X-API-Key": "dev-key"}, json={"prompt": prompt})
    assert r.status_code == 422

def test_not_found_is_safe():
    r = client.get(
        "/api/v1/tasks/00000000-0000-0000-0000-000000000000",
        headers={"X-API-Key": "dev-key"},
    )
    assert r.status_code == 404
    assert "Traceback" not in r.text
