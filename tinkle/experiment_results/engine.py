from __future__ import annotations

import hashlib
import json
from typing import Any
from uuid import UUID

from tinkle.experiment_planning import ExperimentPlanningEngine
from tinkle.reality_engine import ClaimStatus
from tinkle.research_graph import (
    EdgeCreate,
    GraphProvenance,
    NodeType,
    RelationshipType,
    ResearchGraph,
    ResearchGraphNode,
)
from tinkle.research_graph.store import DuplicateGraphError

from .schemas import *


class ExperimentResultsEngine:
    """Analyze externally supplied results; never executes experiments or mutates decisions."""
    def __init__(self, planner:ExperimentPlanningEngine|None=None, graph:ResearchGraph|None=None):
        self.planner=planner or ExperimentPlanningEngine(graph=graph); self.graph=graph or self.planner.graph
        self.results:dict[UUID,ExperimentResult]={}; self.analyses:dict[UUID,ResultAnalysis]={}; self.history:dict[UUID,list[ResultEvent]]={}
    def create_result(self,result:ExperimentResult)->ExperimentResult:
        plan=self.planner.get_plan(result.plan_id)
        if result.evidence_state not in {ClaimStatus.MEASURED,ClaimStatus.SOURCE_BACKED,ClaimStatus.SIMULATED}: raise ValueError('Invalid result evidence state')
        if not result.observations and not result.measurements: raise ValueError('Result requires observations or measurements')
        result.canonical_hash=self._hash(result.model_dump(mode='json',exclude={'id','submitted_at','canonical_hash'})); self.results[result.id]=result
        self.history[result.id]=[ResultEvent(event='RESULT_SUBMITTED',result_id=result.id,provenance=result.provenance)]
        result_node=self.graph.create_node(ResearchGraphNode(type=NodeType.RESULT,name=str(result.id),description=result.source_reference,properties={'plan_id':str(plan.id)},epistemic_state=result.evidence_state))
        plan_nodes=self.graph.search_graph(__import__('tinkle.research_graph',fromlist=['GraphSearchRequest']).GraphSearchRequest(query=f'Plan {plan.id}',node_type=NodeType.EXPERIMENT))
        if plan_nodes:
            try:self.graph.create_edge(EdgeCreate(source_id=plan_nodes[0].id,target_id=result_node.id,relationship=RelationshipType.PRODUCES_RESULT,epistemic_state=result.evidence_state,provenance=GraphProvenance(notes='Phase 11 external result')))
            except DuplicateGraphError:pass
        return result
    def analyze(self,result_id:UUID)->ResultAnalysis:
        result=self._result(result_id); plan=self.planner.get_plan(result.plan_id); missing=self._missing(result,plan); observations=list(result.observations)+[Observation(variable=k,value=v,units=result.units.get(k),evidence_state=result.evidence_state,source_reference=result.source_reference) for k,v in result.measurements.items()]
        comparisons=[]
        for prediction in plan.predictions:
            for observation in observations:
                if prediction.expected_value is not None and observation.value is not None:
                    comparisons.append(self._compare(prediction,observation))
        impacts=[HypothesisImpact(hypothesis_id=out.hypothesis_id,state=HypothesisImpactState.SUPPORTS if any(c.comparison_status==ComparisonStatus.MATCHES_WITHIN_UNCERTAINTY for c in comparisons) else HypothesisImpactState.INSUFFICIENT_DATA,comparison_ids=[c.prediction_id for c in comparisons],evidence_ids=[result.id],rationale='Numerical comparison is evidence impact only; it does not establish truth.') for out in plan.expected_outcomes if out.hypothesis_id]
        quality=ResultQuality.ACCEPTABLE if not missing and result.evidence_state==ClaimStatus.MEASURED else ResultQuality.INCOMPLETE if missing else ResultQuality.UNKNOWN
        update=EvidenceUpdate(previous_state=ClaimStatus.UNKNOWN,proposed_state=result.evidence_state,reason='External result was explicitly supplied; no automatic validation promotion.',supporting_evidence_ids=[result.id],limitations=['Phase 9 validation remains authoritative.'])
        decision_impacts=[]
        if plan.decision_id: decision_impacts=[DecisionImpact(decision_id=plan.decision_id,state=DecisionImpactState.SUPPORTS_EXISTING_RECOMMENDATION if any(c.comparison_status==ComparisonStatus.MATCHES_WITHIN_UNCERTAINTY for c in comparisons) else DecisionImpactState.INSUFFICIENT_DATA,rationale='Decision was not mutated automatically.',evidence_ids=[result.id])]
        payload={'result':result.model_dump(mode='json',exclude={'id','submitted_at','canonical_hash'}),'comparisons':[x.model_dump(mode='json') for x in comparisons],'missing':missing}; analysis=ResultAnalysis(result_id=result.id,plan_id=plan.id,observations=observations,prediction_comparisons=comparisons,hypothesis_impacts=impacts,evidence_updates=[update],missing_data=missing,quality_findings=[quality.value],decision_impacts=decision_impacts,reproducibility_manifest={'method':'result_analysis_v1','input_hash':result.canonical_hash},canonical_hash=self._hash(payload)); self.analyses[result.id]=analysis; self.history[result.id].append(ResultEvent(event='ANALYSIS_CREATED',result_id=result.id)); return analysis
    def _compare(self,prediction,observation):
        if prediction.units and observation.units and prediction.units!=observation.units:return PredictionComparison(prediction_id=prediction.id,observation_id=observation.id,predicted_value=prediction.expected_value,observed_value=observation.value,predicted_units=prediction.units,observed_units=observation.units,comparison_status=ComparisonStatus.INCOMPARABLE,canonical_hash='')
        if not isinstance(prediction.expected_value,(int,float)) or not isinstance(observation.value,(int,float)):return PredictionComparison(prediction_id=prediction.id,observation_id=observation.id,predicted_value=prediction.expected_value,observed_value=observation.value,comparison_status=ComparisonStatus.INSUFFICIENT_DATA,canonical_hash='')
        difference=float(observation.value)-float(prediction.expected_value); scale=max(abs(float(prediction.expected_value)),1e-12); relative=abs(difference)/scale; overlap=observation.uncertainty is not None and bool(prediction.uncertainty)
        status=ComparisonStatus.MATCHES_WITHIN_UNCERTAINTY if overlap and relative<=.1 else ComparisonStatus.PARTIAL_MATCH if relative<=.1 else ComparisonStatus.STRONGLY_DEVIATES if relative>.5 else ComparisonStatus.DEVIATES
        data={'prediction':str(prediction.id),'observation':str(observation.id),'difference':difference,'relative':relative,'status':status.value}; return PredictionComparison(prediction_id=prediction.id,observation_id=observation.id,predicted_value=prediction.expected_value,observed_value=observation.value,predicted_units=prediction.units,observed_units=observation.units,difference=difference,relative_difference=relative,uncertainty_overlap=overlap,comparison_status=status,canonical_hash=self._hash(data))
    def invalidate(self,result_id:UUID,reason:str):
        result=self._result(result_id); result.status=AnalysisStatus.INVALIDATED; self.history[result_id].append(ResultEvent(event='ANALYSIS_INVALIDATED',result_id=result_id,details={'reason':reason})); return result
    def get_analysis(self,result_id:UUID): return self.analyses.get(result_id) or self.analyze(result_id)
    def _result(self,result_id):
        try:return self.results[result_id]
        except KeyError as e:raise KeyError(f'Experiment result not found: {result_id}') from e
    @staticmethod
    def _missing(result,plan):
        missing=[]
        if not result.source_reference:missing.append('source_reference')
        if not result.conditions:missing.append('conditions')
        if any(o.units is None for o in result.observations):missing.append('observation_units')
        if not plan.predictions:missing.append('prediction_references')
        return missing
    @staticmethod
    def _hash(value:Any):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()
