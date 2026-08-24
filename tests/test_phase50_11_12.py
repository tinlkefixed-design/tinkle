from fastapi.testclient import TestClient
from tinkle.api.main import app, tool_executor, tool_registry
from tinkle.sandbox.runner import SandboxRunner
from tinkle.security.redteam import run_red_team

H = {'X-API-Key': 'dev-key'}
c = TestClient(app)

def test_phase50_11_redteam_all_cases_pass():
    results = run_red_team(executor=tool_executor, registry=tool_registry, sandbox=SandboxRunner())
    assert results and all(r.passed for r in results), results

def test_phase50_12_end_to_end_user_to_core_boundaries():
    assert c.get('/health').status_code == 200
    assert c.get('/', follow_redirects=True).status_code == 200
    assert c.get('/ui/app.js').status_code == 200
    project = c.post('/api/v1/projects', headers=H, json={'name': 'e2e'}); assert project.status_code == 200
    pid = project.json()['id']
    task = c.post('/api/v1/tasks', headers=H, json={'prompt': 'e2e task', 'project_id': pid}); assert task.status_code == 200
    mid = c.post('/api/v1/memory', headers=H, json={'type':'working','content':'e2e memory','project_id':pid}); assert mid.status_code == 200
    assert c.post('/api/v1/memory/search', headers=H, json={'query':'e2e memory'}).status_code == 200
    assert c.post('/api/v1/tools/execute', headers=H, json={'tool':'calculator','input':{'expression':'21*2'}}).json()['output']['value'] == 42
    assert c.post('/api/v1/math/calculate', headers=H, json={'question':'e2e','expression':'21*2','mode':'exact'}).json()['verification']['verified'] is True
    assert c.get('/api/v1/integration/status', headers=H).status_code == 200
    smoke = c.post('/api/v1/integration/smoke', headers=H, json={'prompt':'e2e integration'}); assert smoke.status_code == 200
    assert smoke.json()['memory_id']

def test_phase50_12_auth_and_owner_boundary():
    assert c.get('/api/v1/models').status_code == 401
    assert c.get('/api/v1/projects/not-a-uuid', headers={'X-API-Key':'bad'}).status_code == 401
