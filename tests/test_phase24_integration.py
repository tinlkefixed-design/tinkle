from fastapi.testclient import TestClient
from tinkle.api.main import app

client=TestClient(app)
H={'x-api-key':'dev-key'}


def test_phase23_to_24_controlled_lifecycle_api():
    payload={
        'improvement_type':'Evaluation improvement',
        'title':'Improve evaluation workflow',
        'rationale':'Observer indicates evaluation gaps',
        'target':'evaluation workflow',
        'expected_benefit':'clearer evaluation results',
        'risks':['regression'],
        'evidence':['observer:integration'],
    }
    r=client.post('/api/v1/self-improvement/proposals',headers=H,json=payload)
    assert r.status_code==200
    pid=r.json()['proposal']['id']
    stages=[
        ({'sandbox_ref':'sandbox://phase24'},'Sandbox'),
        ({},'Implementation'),
        ({'result':'tests-pass'},'Tests'),
        ({'result':'benchmark-pass'},'Benchmarks'),
        ({'result':'security-pass'},'Security Review'),
        ({'result':'comparison-pass'},'Comparison'),
        ({'result':'human-review-complete'},'Human Approval'),
    ]
    for body, expected in stages:
        r=client.post(f'/api/v1/self-improvement/proposals/{pid}/advance',headers=H,json=body)
        assert r.status_code==200
        assert r.json()['proposal']['stage']==expected
    # Production requires explicit approval and is only a readiness record.
    r=client.post(f'/api/v1/self-improvement/proposals/{pid}/advance',headers=H,json={'human_approved':True})
    assert r.status_code==200
    body=r.json()['proposal']
    assert body['stage']=='Production'
    assert body['human_approved'] is True
    assert body['production_applied'] is False


def test_phase24_health_and_unauthenticated_access():
    health=client.get('/health')
    assert health.status_code==200
    assert health.json()['data']['phase']==33
    assert client.get('/api/v1/self-improvement/proposals').status_code==401
