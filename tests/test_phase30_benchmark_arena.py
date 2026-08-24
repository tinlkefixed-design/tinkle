from fastapi.testclient import TestClient
from tinkle.api.main import app

c=TestClient(app); H={'X-API-Key':'dev-key'}

def test_categories():
    r=c.get('/api/v1/benchmark-arena/categories',headers=H)
    assert r.status_code==200
    assert len(r.json()['categories'])==13

def test_run_and_compare():
    a=c.post('/api/v1/benchmark-arena/run',headers=H,json={'version':'v2.5.0'}); assert a.status_code==200
    assert a.json()['score']==100.0
    b=c.post('/api/v1/benchmark-arena/run',headers=H,json={'version':'v2.8.0'}); assert b.status_code==200
    assert b.json()['total']==13
    r=c.post('/api/v1/benchmark-arena/compare',headers=H,json={'from_version':'v2.5.0','to_version':'v2.8.0'})
    assert r.status_code==200 and r.json()['score_delta']==0.0

def test_unknown_category_rejected():
    r=c.post('/api/v1/benchmark-arena/run',headers=H,json={'checks':{'MadeUp':True}})
    assert r.status_code==422

def test_unauthorized():
    assert c.get('/api/v1/benchmark-arena/categories').status_code==401
