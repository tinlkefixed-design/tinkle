from tinkle.invention_engine import InventionGenerationEngine, InventionRequest, NoveltyClass
from tinkle.cross_domain_engine import CrossDomainInnovationEngine, CrossDomainRequest, DomainObservation

def test_invention_design_space_and_provenance():
    r=InventionGenerationEngine().generate(InventionRequest(problem='cool a device',architectures=['A','B'],mechanisms=['M1','M2'],materials=['X'],processes=['P'],known_designs=['A M1 X P None']))
    assert r.search_space_size==4 and r.generated_count==4
    assert all(x.status=='CANDIDATE' and x.provenance['source']=='CALCULATED' for x in r.candidates)
    assert any(x.novelty==NoveltyClass.KNOWN for x in r.candidates)

def test_cross_domain_principle_is_inferred_not_fact():
    r=CrossDomainInnovationEngine().generate(CrossDomainRequest(problem='new pump',target_domain='mechanical',observations=[
        DomainObservation(domain='Biology',mechanism='vascular branching',function='distribute flow',evidence_refs=['E1']),
        DomainObservation(domain='Fluid Dynamics',mechanism='manifold branching',function='distribute flow',evidence_refs=['E2'])]))
    assert r.principles and r.principles[0].status=='CANDIDATE'
    assert r.principles[0].provenance['source']=='INFERRED'
    assert r.principles[0].provenance['analogy_is_not_proof'] is True
