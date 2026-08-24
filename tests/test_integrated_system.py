from fastapi.testclient import TestClient
from tinkle.api.main import app
c=TestClient(app); H={'X-API-Key':'dev-key'}
def test_all_three_health(): assert c.get('/health').json()['data']['phases']==list(range(1,34))
def test_phase1_project_and_task():
 p=c.post('/api/v1/projects',headers=H,json={'name':'integration'}); assert p.status_code==200
 t=c.post('/api/v1/tasks',headers=H,json={'prompt':'integration task','project_id':p.json()['id']}); assert t.status_code==200
 assert c.get('/api/v1/tasks/'+t.json()['task']['id'],headers=H).status_code==200
def test_phase2_route():
 r=c.post('/api/v1/route',headers=H,json={'prompt':'write code','task_type':'coding','require_coding':True}); assert r.status_code==200 and r.json()['selected_model']=='coding-cloud'
def test_phase3_tool():
 r=c.post('/api/v1/tools/execute',headers=H,json={'tool':'calculator','input':{'expression':'6*7'}}); assert r.status_code==200 and r.json()['output']['value']==42
def test_cross_component_catalogs():
 assert len(c.get('/api/v1/models',headers=H).json()['models'])>=5
 assert len(c.get('/api/v1/tools',headers=H).json()['tools'])>=12

def test_phase12_guardian_and_multi_agent_integration():
    agent = c.post('/api/v1/multi-agent/run', headers=H, json={'goal':'analyze system'}).json()
    text = ' '.join(item['findings'][0] for item in agent['agents'] if item['findings'])
    review = c.post('/api/v1/guardian/review', headers=H, json={'result':text or 'No provider result available', 'evidence':['multi-agent-result']})
    assert review.status_code == 200
    assert review.json()['status'] == 'REVIEW_READY'


def test_phase13_math_integration():
    r = c.post('/api/v1/math/calculate', headers=H, json={'question':'calculate','expression':'6*7','mode':'exact'})
    assert r.status_code == 200
    assert r.json()['result'] == '42'
    assert r.json()['verification']['verified'] is True


def test_phase14_science_to_phase15_engineering_boundary():
    science = c.post('/api/v1/science/inspect', headers=H, json={'question':'materials behavior','domain':'Materials Science'}).json()
    engineering = c.post('/api/v1/engineering/inspect', headers=H, json={
        'problem':'Engineer a materials-based system',
        'domain':'Materials Engineering',
        'context': {'science_boundary': science},
    })
    assert engineering.status_code == 200
    assert engineering.json()['domain'] == 'Materials Engineering'
    assert engineering.json()['solution'] is None


def test_phase15_engineering_api_smoke_all_modules():
    domains = [
        'Mechanical Engineering', 'Electrical Engineering', 'Electronics', 'Robotics',
        'Control Systems', 'Thermal Engineering', 'Materials Engineering',
        'Energy Systems', 'Software Engineering'
    ]
    for domain in domains:
        r = c.post('/api/v1/engineering/inspect', headers=H, json={'problem':'smoke','domain':domain})
        assert r.status_code == 200
        assert r.json()['status'] == 'MODULE_READY'


def test_phase16_simulation_integration():
    r=c.post('/api/v1/simulation/run',headers=H,json={'model':{'state':'x','initial':1,'rate':2},'steps':2,'dt':0.5})
    assert r.status_code==200
    assert r.json()['results'][-1]['x']==3
    assert r.json()['status']=='SIMULATION_COMPLETE'


def test_phase21_skill_to_phase22_self_evaluation():
    skill = c.post('/api/v1/skills/evolve', headers=H, json={
        'name':'integration skill','procedure':['step'], 'tools':[], 'prerequisites':[],
        'benchmarks':['b1'], 'failure_modes':[], 'confidence':0.8
    })
    assert skill.status_code == 200
    task = c.post('/api/v1/tasks', headers=H, json={'prompt':'evaluate skill'}).json()['task']
    evaluation = c.post('/api/v1/self-evaluation/evaluate', headers=H, json={
        'task_id': task['id'], 'task_summary':'evaluate skill',
        'verified':['skill API'], 'improvements':['add benchmark coverage'],
        'remember':['skill versioning is explicit']
    })
    assert evaluation.status_code == 200
    assert evaluation.json()['evaluation']['lessons_stored'] == 2
