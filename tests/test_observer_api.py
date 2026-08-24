from fastapi.testclient import TestClient
from tinkle.api.main import app

client = TestClient(app)
HEADERS={'x-api-key':'dev-key'}

def test_observer_api_observe_and_snapshot():
    r=client.post('/api/v1/observer/observe', headers=HEADERS, json={'metric':'Accuracy','value':0.95,'source':'integration-test'})
    assert r.status_code == 200
    r=client.get('/api/v1/observer/snapshot', headers=HEADERS)
    assert r.status_code == 200
    body=r.json()
    assert body['phase']==23
    assert body['total_events'] >= 1

def test_observer_requires_auth():
    assert client.get('/api/v1/observer/snapshot').status_code == 401
