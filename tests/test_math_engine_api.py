from fastapi.testclient import TestClient

from tinkle.api.main import app


def test_math_api_exact():
    c = TestClient(app)
    r = c.post(
        "/api/v1/math/calculate",
        headers={"X-API-Key": "dev-key"},
        json={"question": "two plus two", "expression": "2 + 2", "mode": "exact"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["result"] == "4"
    assert body["verification"]["verified"] is True


def test_math_api_requires_auth():
    c = TestClient(app)
    r = c.post(
        "/api/v1/math/calculate",
        json={"question": "two plus two", "expression": "2 + 2"},
    )
    assert r.status_code in (401, 403)
