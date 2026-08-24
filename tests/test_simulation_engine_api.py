from fastapi.testclient import TestClient
from tinkle.api.main import app
c=TestClient(app); H={'X-API-Key':'dev-key'}

def test_simulation_api():
    r=c.post('/api/v1/simulation/run',headers=H,json={'model':{'state':'x','initial':2,'rate':3},'steps':2,'dt':1})
    assert r.status_code==200
    body=r.json()
    assert body['status']=='SIMULATION_COMPLETE'
    assert body['results'][-1]['x']==8
    assert body['stages']==['Model','Parameters','Simulation','Results','Visualization','Optimization']

def test_simulation_api_requires_auth():
    assert c.post('/api/v1/simulation/run',json={'model':{'state':'x','rate':1}}).status_code in (401,403)

def test_simulation_api_validation():
    r=c.post('/api/v1/simulation/run',headers=H,json={'model':{'state':'x','rate':'bad'}})
    assert r.status_code==422
