from fastapi.testclient import TestClient
from tinkle.api.main import app

c = TestClient(app)
H = {"X-API-Key": "dev-key"}

def test_security_status_is_authenticated():
    r = c.get('/api/v1/security/status', headers=H)
    assert r.status_code in {200, 409}
    assert r.json()['phase'] == 25
    assert r.json()['policy']['sandbox_required_for_sensitive_tools'] is True

def test_security_status_rejects_bad_key():
    r = c.get('/api/v1/security/status', headers={"X-API-Key": "bad"})
    assert r.status_code == 401

def test_sensitive_tool_executes_inside_sandbox():
    r = c.post('/api/v1/tools/execute', headers=H, json={"tool":"python","input":{"code":"print(1+1)"}})
    assert r.status_code == 200
    assert r.json()['ok'] is True
    assert r.json()['output']['stdout'].strip() == '2'

def test_tool_input_security_limit():
    payload = {"tool":"calculator","input":{"expression":"x" * 70000}}
    r = c.post('/api/v1/tools/execute', headers=H, json=payload)
    assert r.status_code == 200
    assert r.json()['ok'] is False
    assert 'size limit' in r.json()['error']

def test_health_is_phase_25():
    r = c.get('/health')
    assert r.status_code == 200
    data = r.json()['data']
    assert data['phase'] == 33
    assert data['phases'] == list(range(1, 34))

def test_permission_mapping_is_explicit():
    from tinkle.core.config import settings
    from tinkle.core.schemas import Permission
    assert settings.permissions_for_key('dev-key') == {Permission.read, Permission.write, Permission.execute, Permission.admin}

def test_production_rate_limiter_blocks_after_policy_limit():
    from tinkle.security.policy import RateLimiter, SecurityPolicy
    limiter = RateLimiter(SecurityPolicy(max_requests_per_minute=2), enabled=True)
    assert limiter.allow('probe') is True
    assert limiter.allow('probe') is True
    assert limiter.allow('probe') is False
