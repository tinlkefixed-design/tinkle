from fastapi.testclient import TestClient

from tinkle.api.main import app
from tinkle.system_integration import CheckStatus, ReleaseStatus, SystemIntegrationEngine


def test_health_inventory_and_integrity():
    engine=SystemIntegrationEngine()
    health=engine.health(); inventory=engine.capabilities(); integrity=engine.integrity()
    assert health.status==CheckStatus.PASS
    assert len(inventory.capabilities)==11
    assert all(item.status.value=='NOT_VALIDATED' for item in inventory.capabilities)
    assert integrity.status==CheckStatus.PASS

def test_reproducibility_and_readiness_are_deterministic():
    engine=SystemIntegrationEngine()
    first=engine.reproducibility(); second=engine.reproducibility()
    assert first.canonical_hash==second.canonical_hash
    readiness=engine.readiness()
    assert readiness.status==ReleaseStatus.READY_FOR_DEVELOPER_TESTING
    assert 'production' in ' '.join(readiness.limitations)

def test_api_authentication_and_reports():
    client=TestClient(app)
    assert client.get('/api/v1/system/health').status_code==401
    response=client.get('/api/v1/system/health',headers={'X-API-Key':'dev-key'})
    assert response.status_code==200
    assert response.json()['status']=='PASS'
    assert client.get('/api/v1/system/capabilities',headers={'X-API-Key':'dev-key'}).status_code==200

def test_missing_dependency_boundary_is_explicit():
    engine=SystemIntegrationEngine()
    checks=engine.health().checks
    assert all(check.status in {CheckStatus.PASS,CheckStatus.WARN,CheckStatus.UNKNOWN,CheckStatus.NOT_APPLICABLE} for check in checks)
