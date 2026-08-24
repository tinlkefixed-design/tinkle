from fastapi.testclient import TestClient

from tinkle.api.main import app


def test_science_api_inspect():
    c = TestClient(app)
    r = c.post(
        "/api/v1/science/inspect",
        headers={"X-API-Key": "dev-key"},
        json={"question": "What is the question?", "domain": "Physics"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["domain"] == "Physics"
    assert body["status"] == "MODULE_READY"
    assert body["answer"] is None


def test_science_api_requires_auth():
    c = TestClient(app)
    r = c.get("/api/v1/science/modules")
    assert r.status_code in (401, 403)


def test_science_modules_api_lists_six_domains():
    c = TestClient(app)
    r = c.get("/api/v1/science/modules", headers={"X-API-Key": "dev-key"})
    assert r.status_code == 200
    assert {item["domain"] for item in r.json()["modules"]} == {
        "Physics", "Chemistry", "Biology", "Materials Science", "Energy", "Astronomy"
    }


def test_science_api_solve():
    c = TestClient(app)
    r = c.post(
        "/api/v1/science/solve",
        headers={"X-API-Key": "dev-key"},
        json={
            "domain": "Physics",
            "problem": "kinematics",
            "model": "kinematics_v1",
            "inputs": {"initial_velocity": 0, "acceleration": 9.81, "time": 2},
        },
    )
    assert r.status_code == 200
    assert r.json()["status"] == "CALCULATED"
    assert r.json()["calculation"]["outputs"]["final_velocity"] == 19.62
