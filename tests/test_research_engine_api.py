from fastapi.testclient import TestClient
from tinkle.api.main import app
from tinkle.api.deps import auth

client=TestClient(app)
KEY='dev-key'

def test_research_api_auth():
    r=client.post('/api/v1/research/run', json={'question':'anything'})
    assert r.status_code == 401

def test_research_api():
    r=client.post('/api/v1/research/run', headers={'X-API-Key':KEY}, json={'question':'anything'})
    assert r.status_code == 200
    data=r.json()
    assert data['stages'][-1] == 'Report'
    assert data['status'] in {'UNKNOWN','SUPPORTED','VERIFIED','DISPUTED'}
