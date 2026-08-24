from fastapi.testclient import TestClient
from tinkle.api.main import app

c=TestClient(app)
H={'X-API-Key':'dev-key'}


def test_skill_api_create_and_list():
    r=c.post('/api/v1/skills/evolve',headers=H,json={'name':'test skill','procedure':['step 1'],'tools':['math'],'prerequisites':[],'benchmarks':['b1'],'failure_modes':[],'confidence':0.8})
    assert r.status_code==200
    skill_id=r.json()['skill']['id']
    assert r.json()['skill']['version']==1
    g=c.get('/api/v1/skills/'+skill_id,headers=H)
    assert g.status_code==200
    ls=c.get('/api/v1/skills',headers=H)
    assert ls.status_code==200 and ls.json()['count']>=1


def test_skill_api_auth():
    r=c.get('/api/v1/skills')
    assert r.status_code in (401,403)
