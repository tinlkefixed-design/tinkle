from fastapi.testclient import TestClient
from tinkle.api.main import app

H = {'X-API-Key': 'dev-key'}


def test_phase33_health_and_sizing():
    c = TestClient(app)
    health = c.get('/health')
    assert health.status_code == 200
    data = health.json()['data']
    assert data['phase'] == 33
    assert data['phases'] == list(range(1, 34))

    r = c.get('/api/v1/hardware-sizing', headers=H)
    assert r.status_code == 200
    payload = r.json()
    assert payload['phase'] == 33
    assert payload['status'] == 'sized'
    assert payload['tiers']['current_tinkle_runtime']['gpu_required'] is False
    assert 'Blueprint does not specify' in payload['constraints'][0]


def test_phase33_hardware_sizing_requires_auth():
    c = TestClient(app)
    assert c.get('/api/v1/hardware-sizing').status_code == 401
