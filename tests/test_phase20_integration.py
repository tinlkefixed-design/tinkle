from fastapi.testclient import TestClient
from tinkle.api.main import app

c = TestClient(app)
H = {"X-API-Key": "dev-key"}


def test_phase19_to_phase20_boundary():
    discovery = c.post('/api/v1/discovery/discover', headers=H, json={
        'question': 'cross-domain pattern',
        'observations': [
            {'domain': 'Physics', 'pattern': 'feedback', 'evidence': ['e1'], 'confidence': 0.8},
            {'domain': 'Biology', 'pattern': 'feedback', 'evidence': ['e2'], 'confidence': 0.7},
        ],
        'mathematical_structures': ['differential equation'],
    })
    assert discovery.status_code == 200
    failure = c.post('/api/v1/failure-atlas/record', headers=H, json={
        'failure': 'candidate verification failed',
        'cause': 'verification evidence insufficient',
        'conditions': ['candidate needs independent evidence'],
        'symptoms': ['verification status rejected'],
        'detection': ['verification result'],
        'prevention': ['require stronger evidence'],
        'lesson': 'do not promote an unverified discovery to fact',
    })
    assert failure.status_code == 200
    assert failure.json()['knowledge']['failure'] == 'candidate verification failed'


def test_phase20_health_contract():
    health = c.get('/health').json()['data']
    assert health['phase'] == 33
    assert health['phases'][-1] == 33


def test_phase20_to_phase21_skill_evolution_boundary():
    failure = c.post('/api/v1/failure-atlas/record', headers=H, json={
        'failure': 'skill benchmark failed',
        'cause': 'edge case not handled',
        'conditions': ['boundary input'],
        'symptoms': ['incorrect result'],
        'detection': ['benchmark'],
        'prevention': ['add edge-case step'],
        'lesson': 'revise the procedure before reuse',
    })
    assert failure.status_code == 200
    skill = c.post('/api/v1/skills/evolve', headers=H, json={
        'name': 'verified boundary handling',
        'procedure': ['identify boundary input', 'run verification', 'record result'],
        'tools': ['verification'],
        'prerequisites': ['structured input'],
        'benchmarks': ['boundary benchmark'],
        'failure_modes': [failure.json()['knowledge']['failure']],
        'confidence': 0.5,
        'benchmark_passed': True,
    })
    assert skill.status_code == 200
    assert skill.json()['skill']['version'] == 1
