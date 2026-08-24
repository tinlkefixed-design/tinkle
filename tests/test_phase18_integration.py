from tinkle.research_engine import ResearchEngine, ResearchRequest
from tinkle.knowledge.engine import KnowledgeEngine
from tinkle.provenance.service import ProvenanceService
from tinkle.provenance.store import ProvenanceStore
from tinkle.guardian import Guardian
from tinkle.simulation_engine import SimulationEngine
from tinkle.hypothesis_universe import HypothesisUniverse, HypothesisRequest

def test_research_hypotheses_feed_hypothesis_universe():
    research = ResearchEngine(KnowledgeEngine(), ProvenanceService(ProvenanceStore()), Guardian(), SimulationEngine())
    result = research.research(ResearchRequest(question='new topic', hypotheses=['candidate A','candidate B']))
    universe = HypothesisUniverse().run(HypothesisRequest(question=result.question, hypotheses=result.hypotheses))
    assert len(universe.hypotheses) == 2
    assert universe.hypotheses[0].text == 'candidate A'
