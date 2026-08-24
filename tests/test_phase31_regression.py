from fastapi.testclient import TestClient
from tinkle.api.main import app

H = {"X-API-Key": "dev-key"}


def test_phase31_health_preserves_all_prior_phases():
    c = TestClient(app)
    data = c.get('/health').json()['data']
    assert data['phase'] == 33
    assert data['phases'] == list(range(1, 34))


def test_phase31_preserves_core_task_project_contracts():
    c = TestClient(app)
    task = c.post('/api/v1/tasks', headers=H, json={'prompt': 'phase31 regression'} )
    assert task.status_code == 200
    task_id = task.json()['task']['id']
    assert c.get(f'/api/v1/tasks/{task_id}', headers=H).status_code == 200
    assert c.post(f'/api/v1/tasks/{task_id}/run', headers=H).status_code == 200
    project = c.post('/api/v1/projects', headers=H, json={'name': 'phase31-regression'})
    assert project.status_code == 200
    project_id = project.json()['id']
    assert c.get(f'/api/v1/projects/{project_id}', headers=H).status_code == 200
    assert c.delete(f'/api/v1/projects/{project_id}', headers=H).status_code == 200


def test_phase31_preserves_phase30_benchmark_contract():
    c = TestClient(app)
    categories = c.get('/api/v1/benchmark-arena/categories', headers=H)
    assert categories.status_code == 200
    assert len(categories.json()['categories']) == 13
    run = c.post('/api/v1/benchmark-arena/run', headers=H, json={'version': 'v2.8.0'})
    assert run.status_code == 200
    assert run.json()['total'] == 13


def test_phase31_preserves_auth_boundaries():
    c = TestClient(app)
    assert c.get('/api/v1/benchmark-arena/categories').status_code == 401
    assert c.get('/api/v1/models').status_code == 401
