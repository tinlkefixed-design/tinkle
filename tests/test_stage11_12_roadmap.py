from fastapi.testclient import TestClient
from tinkle.api.main import app
from tinkle.experiment_engine import ExperimentEngine, ExperimentRequest
from tinkle.prototype_engine import PrototypeEngine, PrototypeRequest
from tinkle.innovation_platform import InnovationPlatform, ResearchMission

H={'X-API-Key':'dev-key'}
c=TestClient(app)

def test_stage11_experiment_safety_gate_and_ranking():
    e=ExperimentEngine()
    low=ExperimentRequest(objective='distinguish H1/H2',hypotheses=['H1','H2'],measurements=['y'],risk_level='LOW')
    high=ExperimentRequest(objective='high energy test',hypotheses=['H1'],risk_level='HIGH',safety_requirements=['shielding'])
    assert e.plan(low).status.value=='PROPOSED'
    assert e.plan(high).status.value=='APPROVAL_REQUIRED'
    assert e.rank([low,high])

def test_stage11_prototype_plan():
    p=PrototypeEngine().plan(PrototypeRequest(title='Proto',objective='test',materials=['steel'],manufacturing_method='CNC'))
    assert p.bom==[]
    assert p.safety_gate=='STANDARD_SAFETY_REVIEW'
    assert p.assembly_sequence
    assert p.test_procedure

def test_stage12_report_never_auto_validates():
    r=InnovationPlatform().build_report(ResearchMission(mission='find a better heat exchanger'),simulations=[{'result':'good'}],experiment_requests=[ExperimentRequest(objective='compare candidates',hypotheses=['A','B'],measurements=['efficiency'])])
    assert r.verification_status=='NOT_VALIDATED'
    assert 'SIMULATED' in r.evidence_labels
    assert r.final_confidence==0.0

def test_stage11_12_api():
    x=c.post('/api/v1/experiments/plan',headers=H,json={'objective':'test','risk_level':'HIGH','safety_requirements':['guard']})
    assert x.status_code==200 and x.json()['human_approval_required'] is True
    x=c.post('/api/v1/prototypes/plan',headers=H,json={'title':'p','objective':'test','risk_level':'HIGH'})
    assert x.status_code==200 and x.json()['safety_gate']=='HUMAN_APPROVAL_REQUIRED'
    x=c.post('/api/v1/innovation-platform/report',headers=H,json={'mission':{'mission':'mission'}})
    assert x.status_code==200 and x.json()['verification_status']=='NOT_VALIDATED'
