from fastapi.testclient import TestClient

from tinkle.api.main import app


H = {"X-API-Key": "dev-key"}


def test_engineering_api_inspect():
    c = TestClient(app)
    r = c.post(
        "/api/v1/engineering/inspect",
        headers=H,
        json={"problem": "Design a robotic mechanism", "domain": "Robotics"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["domain"] == "Robotics"
    assert body["status"] == "MODULE_READY"
    assert body["solution"] is None


def test_engineering_api_requires_auth():
    c = TestClient(app)
    assert c.get("/api/v1/engineering/modules").status_code in (401, 403)


def test_engineering_modules_api_lists_nine_domains():
    c = TestClient(app)
    r = c.get("/api/v1/engineering/modules", headers=H)
    assert r.status_code == 200
    assert {item["domain"] for item in r.json()["modules"]} == {
        "Mechanical Engineering",
        "Electrical Engineering",
        "Electronics",
        "Robotics",
        "Control Systems",
        "Thermal Engineering",
        "Materials Engineering",
        "Energy Systems",
        "Software Engineering",
    }
