from fastapi.testclient import TestClient
from tinkle.api.main import app

client=TestClient(app)
HEAD={'X-API-Key':'dev-key'}

def test_visual3d_catalog_and_library():
    r=client.get('/api/v1/visual3d/catalog',headers=HEAD)
    assert r.status_code==200
    ids={x['id'] for x in r.json()['models']}
    assert {'atom','molecule','dna','cell','solar_system','turbine','gearbox','bridge','circuit','robot_arm'} <= ids
    r=client.post('/api/v1/visual3d/scene',headers=HEAD,json={'kind':'library','name':'dna'})
    assert r.status_code==200
    assert r.json()['scene']['title']=='DNA'
    assert r.json()['scene']['objects']

def test_visual3d_cad_and_generator():
    r=client.post('/api/v1/visual3d/cad',headers=HEAD,json={'primitive':'gear','parameters':{'radius':1,'teeth':24,'thickness':.2}})
    assert r.status_code==200
    obj=r.json()['scene']['objects'][0]
    assert obj['geometry']=='lines'
    r=client.post('/api/v1/visual3d/scene',headers=HEAD,json={'kind':'generate','prompt':'a DNA molecule with relationships'})
    assert r.status_code==200
    assert r.json()['provenance']['mode']=='PROCEDURAL_GENERATOR'

def test_visual3d_physics():
    for kind in ['gravity','projectile','spring','orbit','heat','fluid']:
        r=client.post('/api/v1/visual3d/simulate',headers=HEAD,json={'kind':kind,'steps':5,'dt':.02,'parameters':{}})
        assert r.status_code==200, (kind,r.text)
        assert len(r.json()['frames'])==6
        assert r.json()['limitations']
