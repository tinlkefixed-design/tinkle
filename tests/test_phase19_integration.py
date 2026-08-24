from fastapi.testclient import TestClient
from tinkle.api.main import app

c=TestClient(app); H={'X-API-Key':'dev-key'}

def test_phase18_hypothesis_to_phase19_discovery_boundary():
    h = c.post('/api/v1/hypothesis-universe/run', headers=H, json={
        'question':'shared principle',
        'hypotheses':['A shared mechanism exists']
    })
    assert h.status_code == 200
    d = c.post('/api/v1/discovery/discover', headers=H, json={
        'question':'shared principle',
        'observations':[
            {'domain':'Physics','pattern':'feedback loop','evidence':['physics-source']},
            {'domain':'Biology','pattern':'feedback loop','evidence':['biology-source']},
        ]
    })
    assert d.status_code == 200
    assert d.json()['cross_domain'] is True
    assert d.json()['candidates'][0]['status'] == 'NEEDS_VERIFICATION'
