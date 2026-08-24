from concurrent.futures import ThreadPoolExecutor, as_completed
from time import perf_counter

from fastapi.testclient import TestClient

from tinkle.api.main import app

HEADERS = {"X-API-Key": "dev-key"}


def _health_request() -> tuple[int, float]:
    started = perf_counter()
    with TestClient(app) as client:
        response = client.get("/health")
    return response.status_code, (perf_counter() - started) * 1000


def _integration_request(i: int) -> tuple[int, float, bool]:
    started = perf_counter()
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/integration/smoke",
            headers=HEADERS,
            json={"prompt": f"stress-{i}"},
        )
    ok = response.status_code == 200 and response.json().get("tool", {}).get("ok") is True
    return response.status_code, (perf_counter() - started) * 1000, ok


def test_phase29_concurrent_health_stress():
    """Bounded concurrency test; this is a stress signal, not a production SLA."""
    requests = 160
    workers = 8
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(lambda _: _health_request(), range(requests)))

    statuses = [status for status, _ in results]
    latencies = [latency for _, latency in results]
    assert statuses == [200] * requests
    assert max(latencies) < 2000


def test_phase29_concurrent_full_integration_stress():
    """Exercise the Phase 28 cross-component path under bounded concurrent load."""
    requests = 96
    workers = 8
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(_integration_request, i) for i in range(requests)]
        results = [future.result() for future in as_completed(futures)]

    assert len(results) == requests
    assert all(status == 200 for status, _, _ in results)
    assert all(ok for _, _, ok in results)
    latencies = [latency for _, latency, _ in results]
    assert max(latencies) < 5000


def test_phase29_failure_recovery_after_stress():
    """A rejected request must not poison subsequent successful execution."""
    with TestClient(app) as client:
        denied = client.post(
            "/api/v1/integration/smoke",
            json={"prompt": "unauthorized"},
        )
        assert denied.status_code == 401

        recovered = client.post(
            "/api/v1/integration/smoke",
            headers=HEADERS,
            json={"prompt": "recovery"},
        )
        assert recovered.status_code == 200
        assert recovered.json()["tool"]["ok"] is True


def test_phase29_state_integrity_after_stress():
    with TestClient(app) as client:
        status = client.get("/api/v1/integration/status", headers=HEADERS)
        assert status.status_code == 200
        data = status.json()
        assert data["phase"] == 28
        assert data["integrated_phases"] == list(range(1, 28))
        assert len(data["components"]) == 27
