from fastapi.testclient import TestClient
from tinkle.api.main import app
from tinkle.core.schemas import MemoryType

c=TestClient(app); H={'X-API-Key':'dev-key'}

def test_memory_types_are_separate():
    r=c.post('/api/v1/memory',headers=H,json={'type':'episodic','content':'user opened project Alpha'})
    assert r.status_code==200
    r=c.post('/api/v1/memory',headers=H,json={'type':'decision','content':'chose Python because of ecosystem'})
    assert r.status_code==200
    r=c.get('/api/v1/memory',headers=H,params={'memory_type':'decision'})
    assert len(r.json()['items'])>=1
    assert all(x['type']=='decision' for x in r.json()['items'])

def test_memory_search():
    c.post('/api/v1/memory',headers=H,json={'type':'semantic','content':'quantum mechanics reference'})
    r=c.post('/api/v1/memory/search',headers=H,json={'query':'quantum'})
    assert r.status_code==200 and any('quantum' in x['content'] for x in r.json()['items'])

def test_memory_delete():
    item=c.post('/api/v1/memory',headers=H,json={'type':'failure','content':'test failure'}).json()
    r=c.delete('/api/v1/memory/'+item['id'],headers=H)
    assert r.status_code==200
    r=c.get('/api/v1/memory',headers=H,params={'memory_type':'failure'})
    assert all(x['id']!=item['id'] for x in r.json()['items'])

def test_export_contains_memory():
    c.post('/api/v1/memory',headers=H,json={'type':'skill','content':'learned testing workflow'})
    r=c.get('/api/v1/data/export',headers=H)
    assert r.status_code==200 and 'memory' in r.json()

def test_full_system_health_phase4():
    r=c.get('/health')
    assert r.json()['data']['phase']==33 and r.json()['data']['phases']==list(range(1,34))
