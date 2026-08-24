from fastapi.testclient import TestClient
from tinkle.api.main import app


def test_guardian_api():
    c = TestClient(app)
    h = {"X-API-Key": "dev-key"}
    r = c.post(
        "/api/v1/guardian/review",
        headers=h,
        json={"result": "A proposed result", "evidence": ["source-a"]},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "REVIEW_READY"
    assert len(body["findings"]) == 7
