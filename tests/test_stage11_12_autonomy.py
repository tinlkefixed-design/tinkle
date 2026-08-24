from fastapi.testclient import TestClient
from tinkle.api.main import app
from tinkle.design_optimization import DesignOptimizationEngine, OptimizationRequest, OptimizationVariable
from tinkle.innovation_campaign import InnovationCampaignEngine, InnovationCampaignRequest
from tinkle.exoskeleton_engine import ExoskeletonRequest

H={'X-API-Key':'dev-key'}; c=TestClient(app)

def design():
    return ExoskeletonRequest(name='Test Suit',user_mass_kg=70,assisted_load_kg=10,assistance_fraction=.4,joints=[{'name':'knee','degree_of_freedom':1,'lever_arm_m':.04,'angular_speed_rad_s':2.0,'efficiency':.85,'safety_factor':1.5}],continuous_runtime_h=1,battery_usable_fraction=.8,system_efficiency=.75)

def test_optimization_complete_and_feasible():
    r=DesignOptimizationEngine().run(OptimizationRequest(design=design(),variables=[OptimizationVariable(name='speed_scale',minimum=.8,maximum=1.0,step=.1),OptimizationVariable(name='lever_scale',minimum=.8,maximum=1.0,step=.1)],objectives=['minimize_peak_power','minimize_battery'],max_peak_power_w=5000,evaluations=20,seed=4))
    assert r.status=='OPTIMIZATION_COMPLETE'; assert r.evaluations==20; assert r.best.feasible

def test_campaign_has_gates_and_no_execution():
    r=InnovationCampaignEngine().run(InnovationCampaignRequest(mission='improve suit efficiency',design=design(),variables=[OptimizationVariable(name='speed_scale',minimum=.8,maximum=1.0,step=.1)],objectives=['minimize_peak_power'],evaluations=12))
    assert r.status=='CAMPAIGN_PLAN_COMPLETE'; assert r.decision_gates; assert 'experiments' in r.recommended_experiment or 'objective' in r.recommended_experiment

def test_optimization_api():
    payload={'design':design().model_dump(mode='json'),'variables':[{'name':'speed_scale','minimum':.8,'maximum':1.0,'step':.1}],'objectives':['minimize_peak_power'],'evaluations':10}
    x=c.post('/api/v1/design-optimization/run',headers=H,json=payload)
    assert x.status_code==200 and x.json()['status']=='OPTIMIZATION_COMPLETE'
