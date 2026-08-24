from fastapi.testclient import TestClient
from tinkle.api.main import app, integrated_execution
from tinkle.multi_agent.engine import MultiAgentSystem
from tinkle.multi_agent.schemas import MultiAgentResult, AgentResult, AgentRole

c=TestClient(app)
H={'X-API-Key':'dev-key'}

def test_integrated_execution_wires_pipeline_without_provider(monkeypatch):
    class FakeMulti:
        def run(self, req):
            return MultiAgentResult(
                goal=req.goal,
                roles=[AgentRole.verifier],
                agents=[AgentResult(role=AgentRole.verifier, objective='verify', input_summary=req.goal, findings=['verified test result'], status='COMPLETED', model_id='fake', provider='fake')],
                status='COMPLETED',
                synthesis='Verified test result.'
            )
    monkeypatch.setattr(integrated_execution, 'multi_agent', FakeMulti())
    r=c.post('/api/v1/execute', headers=H, json={'prompt':'test integrated reasoning','context':{'constraints':['bounded']}})
    assert r.status_code == 200
    data=r.json()
    assert data['workflow']==['Meta-Mind','Planner','Multi-Agent','Guardian']
    assert data['status']=='COMPLETED'
    assert data['plan']['status']=='PLANNED'
    assert data['multi_agent']['status']=='COMPLETED'
    assert data['guardian']['status']=='REVIEW_READY'

def test_integrated_execution_reports_provider_failure(monkeypatch):
    class FailedMulti:
        def run(self, req):
            return MultiAgentResult(goal=req.goal, roles=[AgentRole.verifier], agents=[AgentResult(role=AgentRole.verifier, objective='verify', input_summary=req.goal, findings=[], status='FAILED', error='ProviderUnavailableError: no provider')], status='FAILED', synthesis=None)
    monkeypatch.setattr(integrated_execution, 'multi_agent', FailedMulti())
    r=c.post('/api/v1/execute', headers=H, json={'prompt':'test provider failure'})
    assert r.status_code == 200
    assert r.json()['status']=='FAILED'
    assert 'No synthesis' in r.json()['final_result']

def test_integrated_execution_repairs_high_guardian_finding(monkeypatch):
    class FakeMulti:
        def __init__(self): self.calls = 0
        def run(self, req):
            self.calls += 1
            text = 'initial result' if self.calls == 1 else 'repaired result'
            return MultiAgentResult(
                goal=req.goal,
                roles=[AgentRole.verifier],
                agents=[AgentResult(role=AgentRole.verifier, objective='verify', input_summary=req.goal, findings=[text], status='COMPLETED', model_id='fake', provider='fake')],
                status='COMPLETED',
                synthesis=text,
            )
    fake = FakeMulti()
    monkeypatch.setattr(integrated_execution, 'multi_agent', fake)
    original = integrated_execution.guardian
    class FakeGuardian:
        def __init__(self): self.calls = 0
        def review(self, req):
            from tinkle.guardian.schemas import GuardianResult, GuardianFinding, GuardianCategory
            self.calls += 1
            if self.calls == 1:
                return GuardianResult(result=req.result, findings=[GuardianFinding(category=GuardianCategory.errors, severity='high', statement='Fix the result', basis='test')], categories_checked=list(GuardianCategory), conclusion='REVIEW_REQUIRED')
            return GuardianResult(result=req.result, findings=[], categories_checked=list(GuardianCategory), conclusion='REVIEW_REQUIRED: no high-priority marker was detected, but Guardian does not certify correctness.')
    monkeypatch.setattr(integrated_execution, 'guardian', FakeGuardian())
    r=c.post('/api/v1/execute', headers=H, json={'prompt':'repair me','context':{'retry_limit':1}})
    assert r.status_code == 200
    data=r.json()
    assert data['status'] == 'COMPLETED'
    assert data['final_result'] == 'repaired result'
    assert len(data['guardian_iterations']) == 2
    assert fake.calls == 2
    monkeypatch.setattr(integrated_execution, 'guardian', original)
