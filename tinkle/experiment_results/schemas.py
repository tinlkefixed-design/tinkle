from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from tinkle.engineering_decision import ProvenanceBundle
from tinkle.reality_engine import ClaimStatus


class ResultQuality(str, Enum):
    UNKNOWN='UNKNOWN'; INCOMPLETE='INCOMPLETE'; SUSPECT='SUSPECT'; ACCEPTABLE='ACCEPTABLE'; HIGH_QUALITY='HIGH_QUALITY'; REJECTED='REJECTED'
class ComparisonStatus(str, Enum):
    MATCHES_WITHIN_UNCERTAINTY='MATCHES_WITHIN_UNCERTAINTY'; PARTIAL_MATCH='PARTIAL_MATCH'; DEVIATES='DEVIATES'; STRONGLY_DEVIATES='STRONGLY_DEVIATES'; INCOMPARABLE='INCOMPARABLE'; INSUFFICIENT_DATA='INSUFFICIENT_DATA'
class HypothesisImpactState(str, Enum):
    SUPPORTS='SUPPORTS'; WEAKLY_SUPPORTS='WEAKLY_SUPPORTS'; NEUTRAL='NEUTRAL'; WEAKLY_CONTRADICTS='WEAKLY_CONTRADICTS'; CONTRADICTS='CONTRADICTS'; INSUFFICIENT_DATA='INSUFFICIENT_DATA'; INCOMPARABLE='INCOMPARABLE'
class DecisionImpactState(str, Enum):
    NO_CHANGE='NO_CHANGE'; SUPPORTS_EXISTING_RECOMMENDATION='SUPPORTS_EXISTING_RECOMMENDATION'; WEAKENS_EXISTING_RECOMMENDATION='WEAKENS_EXISTING_RECOMMENDATION'; CONTRADICTS_EXISTING_RECOMMENDATION='CONTRADICTS_EXISTING_RECOMMENDATION'; REQUIRES_REEVALUATION='REQUIRES_REEVALUATION'; INSUFFICIENT_DATA='INSUFFICIENT_DATA'
class RepeatabilityState(str, Enum):
    UNKNOWN='UNKNOWN'; INCONSISTENT='INCONSISTENT'; PARTIALLY_REPRODUCIBLE='PARTIALLY_REPRODUCIBLE'; CONSISTENT='CONSISTENT'; REPRODUCIBILITY_NOT_ASSESSABLE='REPRODUCIBILITY_NOT_ASSESSABLE'
class EvidenceUpdateState(str, Enum):
    PROPOSED='PROPOSED'; NO_UPDATE='NO_UPDATE'; CONFLICTING='CONFLICTING'
class AnalysisStatus(str, Enum):
    ACTIVE='ACTIVE'; INVALIDATED='INVALIDATED'

class Observation(BaseModel):
    id: UUID = Field(default_factory=uuid4); variable: str; value: float|str|None=None; units: str|None=None; uncertainty: float|None=None; condition: str|None=None; timestamp: datetime=Field(default_factory=lambda: datetime.now(UTC)); evidence_state: ClaimStatus=ClaimStatus.MEASURED; source_reference: str|None=None
class ExperimentResult(BaseModel):
    id: UUID=Field(default_factory=uuid4); plan_id: UUID; experiment_id: UUID|None=None; source_reference: str; submitted_at: datetime=Field(default_factory=lambda: datetime.now(UTC)); observations: list[Observation]=Field(default_factory=list); measurements: dict[str,float|str]=Field(default_factory=dict); conditions: dict[str,str|float]=Field(default_factory=dict); units: dict[str,str]=Field(default_factory=dict); operator_or_source: str|None=None; instrument_reference: str|None=None; raw_data_reference: str|None=None; evidence_state: ClaimStatus=ClaimStatus.MEASURED; quality_status: ResultQuality=ResultQuality.UNKNOWN; limitations: list[str]=Field(default_factory=list); assumptions: list[str]=Field(default_factory=list); provenance: ProvenanceBundle=Field(default_factory=ProvenanceBundle); canonical_hash: str|None=None; status: AnalysisStatus=AnalysisStatus.ACTIVE
class PredictionComparison(BaseModel):
    prediction_id: UUID; observation_id: UUID; predicted_value: float|str|None=None; observed_value: float|str|None=None; predicted_units: str|None=None; observed_units: str|None=None; difference: float|None=None; relative_difference: float|None=None; uncertainty_overlap: bool|None=None; comparison_status: ComparisonStatus; assumptions:list[str]=Field(default_factory=list); limitations:list[str]=Field(default_factory=list); method:str='absolute_difference_v1'; canonical_hash:str
class HypothesisImpact(BaseModel):
    hypothesis_id: str; state: HypothesisImpactState; comparison_ids:list[UUID]=Field(default_factory=list); evidence_ids:list[UUID]=Field(default_factory=list); rationale:str; limitations:list[str]=Field(default_factory=list)
class EvidenceUpdate(BaseModel):
    previous_state: ClaimStatus; proposed_state: ClaimStatus; reason:str; supporting_evidence_ids:list[UUID]=Field(default_factory=list); conflicting_evidence_ids:list[UUID]=Field(default_factory=list); assumptions:list[str]=Field(default_factory=list); limitations:list[str]=Field(default_factory=list); confidence_or_strength:float|None=None; provenance:ProvenanceBundle=Field(default_factory=ProvenanceBundle); timestamp:datetime=Field(default_factory=lambda: datetime.now(UTC)); state:EvidenceUpdateState=EvidenceUpdateState.PROPOSED
class DecisionImpact(BaseModel):
    decision_id: UUID; state: DecisionImpactState; rationale:str; evidence_ids:list[UUID]=Field(default_factory=list); limitations:list[str]=Field(default_factory=list)
class ResultAnalysis(BaseModel):
    result_id:UUID; plan_id:UUID; observations:list[Observation]=Field(default_factory=list); prediction_comparisons:list[PredictionComparison]=Field(default_factory=list); hypothesis_impacts:list[HypothesisImpact]=Field(default_factory=list); evidence_updates:list[EvidenceUpdate]=Field(default_factory=list); conflicts:list[UUID]=Field(default_factory=list); missing_data:list[str]=Field(default_factory=list); quality_findings:list[str]=Field(default_factory=list); decision_impacts:list[DecisionImpact]=Field(default_factory=list); repeatability:RepeatabilityState=RepeatabilityState.UNKNOWN; reproducibility_manifest:dict[str,Any]=Field(default_factory=dict); canonical_hash:str; status:AnalysisStatus=AnalysisStatus.ACTIVE
class ResultEvent(BaseModel):
    event:str; result_id:UUID; details:dict[str,Any]=Field(default_factory=dict); timestamp:datetime=Field(default_factory=lambda: datetime.now(UTC)); provenance:ProvenanceBundle=Field(default_factory=ProvenanceBundle)
