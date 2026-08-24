from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from tinkle.engineering_decision import DecisionCriterion, ProvenanceBundle
from tinkle.reality_engine import ClaimStatus


class ValidationStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    REQUIRED = "REQUIRED"
    IN_PROGRESS = "IN_PROGRESS"
    PASSED = "PASSED"
    FAILED = "FAILED"
    INCONCLUSIVE = "INCONCLUSIVE"
    BLOCKED = "BLOCKED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class EvidenceKind(str, Enum):
    DIRECT = "DIRECT"
    DERIVED = "DERIVED"
    SIMULATED = "SIMULATED"
    MEASURED = "MEASURED"
    SOURCE_BACKED = "SOURCE_BACKED"
    ASSUMED = "ASSUMED"
    UNKNOWN = "UNKNOWN"


class ReproducibilityStatus(str, Enum):
    REPRODUCIBLE = "REPRODUCIBLE"
    PARTIALLY_REPRODUCIBLE = "PARTIALLY_REPRODUCIBLE"
    NON_REPRODUCIBLE = "NON_REPRODUCIBLE"
    UNKNOWN = "UNKNOWN"


class ValidationGateState(str, Enum):
    VALIDATION_NOT_REQUIRED = "VALIDATION_NOT_REQUIRED"
    VALIDATION_REQUIRED = "VALIDATION_REQUIRED"
    VALIDATION_READY = "VALIDATION_READY"
    VALIDATED = "VALIDATED"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    VALIDATION_INCONCLUSIVE = "VALIDATION_INCONCLUSIVE"
    INVALIDATED = "INVALIDATED"
    DATA_INSUFFICIENT = "DATA_INSUFFICIENT"


class ValidationRequirement(BaseModel):
    id: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=3000)
    target_decision_id: UUID | None = None
    target_candidate_id: UUID | None = None
    criterion: str | None = None
    expected_evidence_type: EvidenceKind = EvidenceKind.MEASURED
    acceptance_condition: str = Field(min_length=1, max_length=2000)
    minimum_confidence: float | None = Field(default=None, ge=0, le=1)
    required_measurement_or_experiment: str | None = None
    units: str | None = None
    epistemic_state: ClaimStatus = ClaimStatus.UNKNOWN
    priority: int = Field(default=3, ge=1, le=5)
    provenance: ProvenanceBundle = Field(default_factory=ProvenanceBundle)
    assumptions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class ValidationRecord(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    target_type: str = Field(min_length=1, max_length=100)
    target_id: UUID
    validation_requirement_id: str
    method: str = Field(min_length=1, max_length=2000)
    expected_result: float | str | None = None
    observed_result: float | str | None = None
    units: str | None = None
    status: ValidationStatus = ValidationStatus.REQUIRED
    epistemic_state: ClaimStatus = ClaimStatus.UNKNOWN
    evidence_refs: list[str] = Field(default_factory=list)
    evaluator_id: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    assumptions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    uncertainty: dict[str, Any] = Field(default_factory=dict)
    provenance: ProvenanceBundle = Field(default_factory=ProvenanceBundle)
    input_hash: str | None = None
    result_hash: str | None = None


class EvidenceLink(BaseModel):
    sequence: int
    kind: EvidenceKind
    artifact_id: str
    source_id: str | None = None
    epistemic_state: ClaimStatus = ClaimStatus.UNKNOWN
    provenance: ProvenanceBundle = Field(default_factory=ProvenanceBundle)


class EvidenceChain(BaseModel):
    decision_id: UUID
    links: list[EvidenceLink] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    input_hash: str
    method_version: str = "evidence_chain_v1"
    provenance: ProvenanceBundle = Field(default_factory=ProvenanceBundle)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class DecisionTrace(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    root_decision_id: UUID
    requirement_ids: list[str] = Field(default_factory=list)
    candidate_ids: list[UUID] = Field(default_factory=list)
    evaluation_ids: list[UUID] = Field(default_factory=list)
    criteria: list[DecisionCriterion] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    validation_ids: list[UUID] = Field(default_factory=list)
    graph_relationships: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    provenance: ProvenanceBundle = Field(default_factory=ProvenanceBundle)
    canonical_input_hash: str
    method_version: str = "decision_trace_v1"
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ReproducibilityManifest(BaseModel):
    decision_id: UUID
    canonical_input_hash: str | None = None
    candidate_ids: list[UUID] = Field(default_factory=list)
    evaluation_ids: list[UUID] = Field(default_factory=list)
    criterion_definitions: list[DecisionCriterion] = Field(default_factory=list)
    criterion_weights: dict[str, float] = Field(default_factory=dict)
    evidence_ids: list[str] = Field(default_factory=list)
    validation_ids: list[UUID] = Field(default_factory=list)
    simulation_model_ids: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    uncertainty_configuration: dict[str, Any] = Field(default_factory=dict)
    method_versions: list[str] = Field(default_factory=lambda: ["decision_trace_v1", "reproducibility_manifest_v1"])
    software_metadata: dict[str, str] = Field(default_factory=dict)
    random_seed: int | None = None
    deterministic_mode: bool = True
    status: ReproducibilityStatus = ReproducibilityStatus.UNKNOWN
    missing_inputs: list[str] = Field(default_factory=list)
    provenance: ProvenanceBundle = Field(default_factory=ProvenanceBundle)
    canonical_manifest_hash: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class InvalidationCondition(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    decision_id: UUID
    description: str = Field(min_length=1, max_length=2000)
    trigger: str = Field(min_length=1, max_length=2000)
    evidence_refs: list[str] = Field(default_factory=list)
    active: bool = True
    triggered: bool = False
    triggered_by: list[str] = Field(default_factory=list)
    provenance: ProvenanceBundle = Field(default_factory=ProvenanceBundle)
    epistemic_state: ClaimStatus = ClaimStatus.UNKNOWN


class ValidationGate(BaseModel):
    decision_id: UUID
    state: ValidationGateState
    requirement_ids: list[str] = Field(default_factory=list)
    record_ids: list[UUID] = Field(default_factory=list)
    missing_requirements: list[str] = Field(default_factory=list)
    conflicting_evidence_ids: list[str] = Field(default_factory=list)
    invalidation_condition_ids: list[UUID] = Field(default_factory=list)
    explanation: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    provenance: ProvenanceBundle = Field(default_factory=ProvenanceBundle)
    epistemic_state: ClaimStatus = ClaimStatus.UNKNOWN


class ValidationEvent(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    decision_id: UUID
    event_type: str
    previous_state: ValidationGateState | None = None
    new_state: ValidationGateState | None = None
    artifact_id: UUID | None = None
    details: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    provenance: ProvenanceBundle = Field(default_factory=ProvenanceBundle)


__all__ = [name for name in globals() if not name.startswith("_")]
