from __future__ import annotations
from typing import Any
from .schemas import *
from tinkle.experiment_engine import ExperimentEngine, ExperimentRequest
from tinkle.prototype_engine import PrototypeEngine, PrototypeRequest, PrototypeLevel

class InnovationPlatform:
    """Stage 12 facade. It composes existing engines and refuses unsupported claims."""
    def __init__(self):
        self.experiments=ExperimentEngine(); self.prototypes=PrototypeEngine()

    def build_report(self, mission: ResearchMission, *, problem=None, knowledge=None, gaps=None, constraints=None, hypotheses=None, models=None, inventions=None, principles=None, simulations=None, failures=None, falsification=None, experiment_requests=None, prototype_requests=None, risks=None, unknowns=None) -> DiscoveryReport:
        exp=self.experiments.rank(experiment_requests or [])
        prot=[self.prototypes.plan(r, PrototypeLevel.LOW_FIDELITY) for r in (prototype_requests or [])]
        evidence=[]
        for s in simulations or []: evidence.append('SIMULATED')
        for f in failures or []: evidence.append('INFERRED')
        # No auto-validation: real experimental evidence must be supplied and independently reproduced later.
        return DiscoveryReport(mission_id=mission.id,mission=mission.mission,problem=problem or {},existing_knowledge=knowledge or [],knowledge_gaps=gaps or [],constraints=constraints or [],hypotheses=hypotheses or mission.hypotheses,mathematical_models=models or [],candidate_inventions=inventions or mission.candidate_inventions,cross_domain_principles=principles or [],simulations=simulations or [],failures=failures or [],falsification_results=falsification or [],experiments=exp,prototypes=prot,risks=risks or [],unknowns=unknowns or [],novelty_assessment='UNKNOWN',verification_status='NOT_VALIDATED',final_confidence=0.0,evidence_labels=sorted(set(evidence)),provenance={'platform':'TINKLE_AUTONOMOUS_SCIENTIFIC_INNOVATION_PLATFORM','stage':'12','claim_policy':'Simulation is not experimental evidence; no discovery is promoted automatically.'})
