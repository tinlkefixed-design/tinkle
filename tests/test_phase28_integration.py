from fastapi.testclient import TestClient
from tinkle.api.main import app

client = TestClient(app)
HEADERS = {"X-API-Key": "dev-key"}


def test_phase28_health_contract():
    data = client.get('/health').json()['data']
    assert data['phase'] == 33
    assert data['phases'] == list(range(1, 34))


def test_phase28_status_contains_all_previous_phases():
    r = client.get('/api/v1/integration/status', headers=HEADERS)
    assert r.status_code == 200
    data = r.json()
    assert data['phase'] == 28
    assert data['integrated_phases'] == list(range(1, 28))
    assert len(data['components']) == 27
    assert data['boundaries']['event_bus'] is True
    assert data['boundaries']['observer_bridge'] is True


def test_phase28_smoke_cross_component_workflow():
    r = client.post('/api/v1/integration/smoke', headers=HEADERS, json={'prompt': 'Explain how Tinkle should handle a reasoning task.'})
    assert r.status_code == 200
    data = r.json()
    assert data['workflow'] == ['Memory', 'Model Router', 'Tool System', 'Observer', 'Event Bus']
    assert data['tool']['name'] == 'calculator'
    assert data['tool']['ok'] is True
    assert data['tool']['output']['value'] == 4
    assert data['observer_total_events'] >= 1
    assert data['latency_ms'] >= 0


def test_phase28_requires_auth():
    assert client.get('/api/v1/integration/status').status_code == 401
    assert client.post('/api/v1/integration/smoke', json={'prompt': 'x'}).status_code == 401
