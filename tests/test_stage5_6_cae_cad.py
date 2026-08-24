from fastapi.testclient import TestClient
from tinkle.api.main import app
from tinkle.cae_engine import CAEEngine, CAERequest
from tinkle.cad_engine import CADEngine, CADAssemblyRequest, CADPart
client=TestClient(app); H={'X-API-Key':'dev-key'}

def test_axial_bar_and_thermal():
    r=CAEEngine().run(CAERequest(kind='axial_bar',length_m=1,area_m2=1e-4,youngs_modulus_pa=200e9,nodes=5,loads_n={4:1000}))
    assert r.status=='CAE_ANALYSIS_COMPLETE'; assert r.results['max_abs_stress_pa']>0; assert r.results['solver_checks']['finite_solution']
    t=CAEEngine().run(CAERequest(kind='thermal_1d',length_m=2,area_m2=.01,conductivity_w_mk=10,temperature_left_c=100,temperature_right_c=20,nodes=5))
    assert t.results['temperature_c'][0]==100 and t.results['temperature_c'][-1]==20

def test_buckling_and_cad_exports():
    b=CAEEngine().run(CAERequest(kind='buckling_column',length_m=1,second_moment_m4=1e-8))
    assert b.results['euler_critical_load_n']>0
    for fmt in ('json','obj','stl'):
        r=CADEngine().build(CADAssemblyRequest(name='exo-test',export=fmt,parts=[CADPart(name='link',primitive='box',parameters={'width':.1,'height':.3,'depth':.05})]))
        assert r.status=='CAD_ASSEMBLY_READY'; assert len(r.assembly['mesh']['vertices'])==8
        if fmt!='json': assert r.export_data and ('solid' in r.export_data if fmt=='stl' else '\nv ' in '\n'+r.export_data)

def test_api_stage5_6():
    r=client.post('/api/v1/cae/analyze',headers=H,json={'kind':'buckling_column','length_m':1,'second_moment_m4':1e-8})
    assert r.status_code==200
    r=client.post('/api/v1/cad/assembly',headers=H,json={'name':'test','export':'obj','parts':[{'name':'base','primitive':'box','parameters':{'width':1,'height':.2,'depth':1}}]})
    assert r.status_code==200 and r.json()['export_data'].startswith('v ')
