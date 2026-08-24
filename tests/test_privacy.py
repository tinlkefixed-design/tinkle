from fastapi.testclient import TestClient
from tinkle.api.main import app

c = TestClient(app)
H = {"X-API-Key": "dev-key"}

def test_privacy_defaults_are_explicit():
    r = c.get('/api/v1/privacy', headers=H)
    assert r.status_code == 200
    s = r.json()['settings']
    assert s == {'store_data': True, 'allow_cloud_models': True, 'local_only': False, 'allow_delete': True, 'allow_export': True}

def test_local_mode_disables_cloud():
    r = c.post('/api/v1/privacy/local-mode', headers=H)
    assert r.status_code == 200
    s = r.json()['settings']
    assert s['local_only'] is True and s['allow_cloud_models'] is False

def test_privacy_blocks_cloud_route_and_storage():
    r = c.post('/api/v1/route', headers=H, json={'prompt':'private route','privacy':'public'})
    assert r.status_code == 200
    assert r.json()['provider'] == 'local'
    r = c.put('/api/v1/privacy', headers=H, json={'store_data': False})
    assert r.status_code == 200
    r = c.post('/api/v1/memory', headers=H, json={'type':'working','content':'must not persist'})
    assert r.status_code == 409

def test_privacy_can_reenable_defaults():
    r = c.put('/api/v1/privacy', headers=H, json={'store_data': True, 'allow_cloud_models': True, 'local_only': False})
    assert r.status_code == 200
    s = r.json()['settings']
    assert s['store_data'] is True and s['allow_cloud_models'] is True and s['local_only'] is False

def test_export_delete_controls_are_enforced():
    r = c.put('/api/v1/privacy', headers=H, json={'allow_export': False, 'allow_delete': False})
    assert r.status_code == 200
    assert c.get('/api/v1/data/export', headers=H).status_code == 403
    assert c.delete('/api/v1/data', headers=H).status_code == 403
    c.put('/api/v1/privacy', headers=H, json={'allow_export': True, 'allow_delete': True})

def test_privacy_requires_auth():
    assert c.get('/api/v1/privacy').status_code in {401, 403}
