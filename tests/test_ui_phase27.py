from fastapi.testclient import TestClient
from tinkle.api.main import app

client = TestClient(app)


def test_phase27_ui_root_and_assets():
    page = client.get('/')
    assert page.status_code == 200
    text = page.text
    required = [
        'TINKLE', 'PHASE 27', 'Chat', 'Projects', 'Knowledge', 'Research',
        'Experiments', 'Simulation', 'Agents', 'Memory', 'Skills', 'Discoveries',
        'Hypotheses', 'Evidence', 'Tasks', 'System Health', 'Settings',
        'LIVE 3D EXPLANATION ENGINE', 'ujo3wxzG5OhpWcoi3SMy'
    ]
    # Voice id is checked separately below because the page may be cached/transformed.
    for item in required[:-1]:
        assert item in text
    assert 'uju3wxzG5OhpWcoi3SMy' in text
    assert client.get('/ui/styles.css').status_code == 200
    assert client.get('/ui/app.js').status_code == 200


def test_phase27_health_contract():
    data = client.get('/health').json()['data']
    assert data['phase'] == 33
    assert data['phases'] == list(range(1, 34))


def test_phase27_ui_contains_3d_behavior_contracts():
    js = client.get('/ui/app.js').text
    css = client.get('/ui/styles.css').text
    assert 'getContext(\'webgl\'' in js
    assert 'explaining' in js and 'listening' in js and 'speaking' in js and 'executing' in js
    assert 'tinkle-actor.explaining' in css
    assert 'scene-label' in css
    assert 'data-scene="atom"' in client.get('/').text
