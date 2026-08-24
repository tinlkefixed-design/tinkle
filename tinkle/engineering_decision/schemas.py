from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from tinkle.invention_design import DesignEvaluation, ProvenanceBundle
from tinkle.reality_engine import ClaimStatus


class DecisionState(str, Enum):
    UNDECIDED = "UNDECIDED"
    DATA_INSUFFICIENT = "DATA_INSUFFICIENT"
    CONSTRAINED = "CONSTRAINED"
    TRADEOFF_REQUIRED = "TRADEOFF_REQUIRED"
    RECOMMENDED = "RECOMMENDED"
    SELECTED = "SELECTED"
    REQUIRES_VALIDATION = "REQUIRES_VALIDATION"


class CriterionDirection(str, Enum):
    MAXIMIZE = "MAXIMIZE"
    MINIMIZE = "MINIMIZE"
    TARGET = "TARGET"


class DecisionCriterion(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    direction: CriterionDirection = CriterionDirection.MAXIMIZE
    weight: float | None = Field(default=None, gt=0)
    values: dict[str, float | str | None] = Field(default_factory=dict)
    evidence_refs: list[str] = Field(default_factory=list)
    epistemic_state: ClaimStatus = ClaimStatus.UNKNOWN
    assumptions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class DecisionEvidence(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    description: str = Field(min_length=1, max_length=3000)
    artifact_refs: list[str] = Field(default_factory=list)
    source: str | None = None
    epistemic_state: ClaimStatus = ClaimStatus.UNKNOWN
    provenance: ProvenanceBundle = Field(default_factory=ProvenanceBundle)
    assumptions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class DecisionOption(BaseModel):
    candidate_id: UUID
    evaluation_id: UUID | None = None
    evaluation: DesignEvaluation | None = None
    constraint_results: list[str] = Field(default_factory=list)
    simulation_refs: list[str] = Field(default_factory=list)
    uncertainty_refs: list[str] = Field(default_factory=list)
    sensitivity_refs: list[str] = Field(default_factory=list)
    research_refs: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class Tradeoff(BaseModel):
    criterion: str
    option_a: UUID
    option_b: UUID
    evidence_refs: list[str] = Field(default_factory=list)
    direction: str = "UNKNOWN"
    magnitude: float | None = None
    uncertainty: str = "UNKNOWN"
    limitation: str = "Magnitude is unavailable without comparable numeric evidence."
    epistemic_state: ClaimStatus = ClaimStatus.UNKNOWN


class DecisionRequest(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str = Field(min_length=1, max_length=300)
    objective: str = Field(min_length=1, max_length=3000)
    requirement_refs: list[str] = Field(default_factory=list)
    candidate_refs: list[UUID] = Field(min_length=2, max_length=100)
    constraint_refs: list[str] = Field(default_factory=list)
    evaluation_refs: list[UUID] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    criteria: list[DecisionCriterion] = Field(min_length=1, max_length=50)
    unresolved_unknowns: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    provenance: ProvenanceBundle = Field(default_factory=ProvenanceBundle)
    epistemic_state: ClaimStatus = ClaimStatus.UNKNOWN
    allow_constraint_relaxation: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class DecisionEvent(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    artifact_id: UUID
    event_type: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    previous_state: DecisionState | None = None
    new_state: DecisionState | None = None
    details: dict[str, Any] = Field(default_factory=dict)
    provenance: ProvenanceBundle = Field(default_factory=ProvenanceBundle)


class EngineeringDecision(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    request_id: UUID
    state: DecisionState
    options: list[DecisionOption] = Field(default_factory=list)
    recommendation: UUID | None = None
    selected_candidate: UUID | None = None
    criteria: list[DecisionCriterion] = Field(default_factory=list)
    tradeoffs: list[Tradeoff] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    hard_constraint_failures: dict[str, list[str]] = Field(default_factory=dict)
    scores: dict[str, float] = Field(default_factory=dict)
    normalized_values: dict[str, dict[str, float]] = Field(default_factory=dict)
    criterion_weights: dict[str, float] = Field(default_factory=dict)
    exclusions: dict[str, list[str]] = Field(default_factory=dict)
    method: str = "explicit_weighted_sum_v1"
    input_hash: str
    explanation: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    validation_requirements: list[str] = Field(default_factory=list)
    provenance: ProvenanceBundle = Field(default_factory=ProvenanceBundle)
    epistemic_state: ClaimStatus = ClaimStatus.UNKNOWN
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class DecisionStateResult(BaseModel):
    decision: EngineeringDecision


__all__ = [name for name in globals() if not name.startswith("_")]
