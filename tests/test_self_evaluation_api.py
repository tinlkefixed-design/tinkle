from fastapi.testclient import TestClient
from tinkle.api.main import app

c = TestClient(app)
H = {'X-API-Key': 'dev-key'}


def test_self_evaluation_api_and_memory():
    task = c.post('/api/v1/tasks', headers=H, json={'prompt': 'evaluate this'}).json()['task']
    r = c.post('/api/v1/self-evaluation/evaluate', headers=H, json={
        'task_id': task['id'],
        'task_summary': 'evaluate this',
        'assumptions': ['known input'],
        'potential_errors': ['edge'],
        'verified': ['test'],
        'unknowns': ['provider'],
        'failures': ['none'],
        'improvements': ['keep test'],
        'remember': ['provider unavailable'],
    })
    assert r.status_code == 200
    assert r.json()['evaluation']['lessons_stored'] == 3
    g = c.get('/api/v1/self-evaluation/' + task['id'], headers=H)
    assert g.status_code == 200


def test_self_evaluation_auth():
    r = c.post('/api/v1/self-evaluation/evaluate', json={'task_summary': 'x'})
    assert r.status_code in (401, 403)
