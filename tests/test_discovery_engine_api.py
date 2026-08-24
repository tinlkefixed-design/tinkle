from fastapi.testclient import TestClient
from tinkle.api.main import app
c=TestClient(app); H={'X-API-Key':'dev-key'}

def test_discovery_api():
    r=c.post('/api/v1/discovery/discover',headers=H,json={
        'question':'shared pattern',
        'observations':[
            {'domain':'Physics','pattern':'feedback loop','evidence':['p1'],'confidence':0.8},
            {'domain':'Biology','pattern':'feedback loop','evidence':['b1'],'confidence':0.7}
        ],
        'mathematical_structures':['differential equation']
    })
    assert r.status_code == 200
    assert r.json()['status'] == 'DISCOVERY_CANDIDATES_FOUND'
    assert r.json()['candidates'][0]['status'] == 'NEEDS_VERIFICATION'

def test_discovery_requires_auth():
    r=c.post('/api/v1/discovery/discover',json={'question':'x'})
    assert r.status_code in (401,403)
