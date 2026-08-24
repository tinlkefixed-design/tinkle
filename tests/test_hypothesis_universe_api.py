from fastapi.testclient import TestClient
from tinkle.api.main import app
client=TestClient(app)

def test_hypothesis_api_auth():
    r=client.post('/api/v1/hypothesis-universe/run',json={'question':'x','hypotheses':['h']})
    assert r.status_code == 401

def test_hypothesis_api():
    r=client.post('/api/v1/hypothesis-universe/run',headers={'X-API-Key':'dev-key'},json={'question':'x','hypotheses':['h1','h2']})
    assert r.status_code == 200
    assert r.json()['hypotheses'][0]['id'] == 'H1'
