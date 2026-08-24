from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient

from tinkle.api.main import app
from tinkle.core.jobs import JobQueue
from tinkle.core.blueprint_audit import build_audit
from tinkle.benchmark_arena import BenchmarkArena

HEADERS = {"X-API-Key": "dev-key"}


def test_phase50_15_high_concurrency_health_integrity():
    """Higher bounded load than the legacy stress test; no failures or state corruption."""
    def one(_):
        with TestClient(app) as client:
            r = client.get("/health")
            return r.status_code, r.json()

    with ThreadPoolExecutor(max_workers=16) as pool:
        results = list(pool.map(one, range(256)))

    assert all(status == 200 for status, _ in results)
    assert all(payload.get("data", {}).get("status") == "ok" for _, payload in results)


def test_phase50_15_integration_recovery_after_concurrent_load():
    def one(i):
        with TestClient(app) as client:
            r = client.post("/api/v1/integration/smoke", headers=HEADERS, json={"prompt": f"stress-{i}"})
            return r.status_code, r.json()

    with ThreadPoolExecutor(max_workers=12) as pool:
        results = list(pool.map(one, range(128)))

    assert all(status == 200 for status, _ in results)
    assert all(body.get("tool", {}).get("ok") is True for _, body in results)

    with TestClient(app) as client:
        r = client.post("/api/v1/integration/smoke", json={"prompt": "must-deny"})
        assert r.status_code == 401
        r = client.post("/api/v1/integration/smoke", headers=HEADERS, json={"prompt": "must-recover"})
        assert r.status_code == 200


def test_phase50_15_durable_job_restart_recovery():
    with TemporaryDirectory() as td:
        db = str(Path(td) / "jobs.db")
        q1 = JobQueue(db)
        job = q1.enqueue("long-research")
        running = q1.next()
        assert running is not None and running.status == "running"
        q1._db.close()

        q2 = JobQueue(db)
        recovered = q2.get(job.id)
        assert recovered is not None
        assert recovered.status == "queued"
        assert q2.size() == 1
        q2.update(job.id, "completed")
        assert q2.get(job.id).status == "completed"
        q2._db.close()


def test_phase50_15_benchmark_repeatability():
    arena = BenchmarkArena()
    first = arena.run(version="v2.44.0")
    second = arena.run(version="v2.44.0")
    assert first["total"] == second["total"] == 13
    assert first["score"] == second["score"] == 100.0
    assert first["passed"] == second["passed"] == 13


def test_phase50_15_blueprint_audit_has_no_unknown_statuses():
    audit = build_audit()
    assert audit["total_items"] == 76
    assert audit["counts"]["NOT_VERIFIED"] == 0
    assert all(item["status"] in {"PASS", "PARTIAL", "NOT_VERIFIED"} for item in audit["items"])
