from tinkle.knowledge.engine import KnowledgeEngine
from tinkle.knowledge.schemas import KnowledgeDocument
from tinkle.provenance.service import ProvenanceService
from tinkle.provenance.store import ProvenanceStore
from tinkle.provenance.schemas import ProvenanceRecord, ProvenanceStatus
from tinkle.guardian import Guardian
from tinkle.simulation_engine import SimulationEngine
from tinkle.research_engine import ResearchEngine, ResearchRequest

def make_engine():
    knowledge=KnowledgeEngine(); doc=KnowledgeDocument(title='Solar note', source='local://solar', content='Solar panels convert light into electrical energy.')
    knowledge.ingest(doc)
    provenance=ProvenanceService(ProvenanceStore())
    provenance.record(ProvenanceRecord(claim='Solar panels convert light into electrical energy.', source='local://solar', confidence=.9, status=ProvenanceStatus.verified))
    return ResearchEngine(knowledge, provenance, Guardian(), SimulationEngine())

def test_research_pipeline_and_verification():
    result=make_engine().research(ResearchRequest(question='solar electrical energy'))
    assert result.status == 'VERIFIED'
    assert [s.value for s in result.stages] == ['Question','Search','Sources','Evidence','Knowledge','Hypotheses','Analysis','Simulation','Criticism','Verification','Report']
    assert result.evidence
    assert result.verification['status'] == 'VERIFIED'

def test_research_without_evidence_is_unknown():
    knowledge=KnowledgeEngine(); engine=ResearchEngine(knowledge, ProvenanceService(ProvenanceStore()), Guardian(), SimulationEngine())
    result=engine.research(ResearchRequest(question='unindexed topic'))
    assert result.status == 'UNKNOWN'
    assert result.verification['status'] == 'UNKNOWN'

def test_simulation_boundary_is_integrated():
    result=make_engine().research(ResearchRequest(question='solar', simulate=True, simulation={'model':{'state':'x','rate':1,'initial':0},'parameters':{},'steps':2,'dt':1}))
    assert result.simulation['status'] == 'COMPLETE'
