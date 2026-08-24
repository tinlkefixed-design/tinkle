from fastapi.testclient import TestClient
from tinkle.api.main import app

client=TestClient(app)
H={'x-api-key':'dev-key'}

def payload():
    return {
        'improvement_type':'Workflow improvement',
        'title':'Improve retrieval workflow',
        'rationale':'Observed retrieval misses',
        'target':'research workflow',
        'expected_benefit':'fewer misses',
        'risks':['regression'],
        'evidence':['observer:event-1'],
    }

def test_self_improvement_proposal_api():
    r=client.post('/api/v1/self-improvement/proposals',headers=H,json=payload())
    assert r.status_code==200
    body=r.json()
    assert body['proposal']['stage']=='Proposal'
    assert body['next_stage']=='Sandbox'

def test_self_improvement_auth():
    assert client.get('/api/v1/self-improvement/proposals').status_code==401
