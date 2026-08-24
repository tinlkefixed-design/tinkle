from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from tinkle.reality_engine import ClaimStatus
from tinkle.simulation_engine import MechanicsSimulationRequest, ParameterRange


class CandidateLifecycle(str, Enum):
    PROPOSED = "PROPOSED"
    EVALUATED = "EVALUATED"
    SUPPORTED = "SUPPORTED"
    REJECTED = "REJECTED"
    REQUIRES_DATA = "REQUIRES_DATA"


class ConstraintStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class ProvenanceBundle(BaseModel):
    originating_artifact: str | None = None
    hypothesis_refs: list[str] = Field(default_factory=list)
    prediction_refs: list[str] = Field(default_factory=list)
    experiment_refs: list[str] = Field(default_factory=list)
    simulation_refs: list[str] = Field(default_factory=list)
    analysis_refs: list[str] = Field(default_factory=list)
    input_hash: str | None = None
    model_id: str | None = None
    method: str = "caller_supplied"
    assumptions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class EngineeringRequirement(BaseModel):
    id: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=2000)
    target: float | str | None = None
    minimum: float | None = None
    maximum: float | None = None
    units: str | None = None
    source_artifact: str | None = None
    provenance: ProvenanceBundle = Field(default_factory=ProvenanceBundle)
    epistemic_state: ClaimStatus = ClaimStatus.UNKNOWN
    priority: int = Field(default=3, ge=1, le=5)
    hard_constraint: bool = True
    assumptions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class DesignParameter(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    value: float | str | None = None
    unit: str | None = None
    minimum: float | None = None
    maximum: float | None = None
    epistemic_state: ClaimStatus = ClaimStatus.UNKNOWN
    provenance: ProvenanceBundle = Field(default_factory=ProvenanceBundle)


class DesignCandidate(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=5000)
    components: list[str] = Field(default_factory=list)
    parameters: list[DesignParameter] = Field(default_factory=list)
    geometry_refs: list[str] = Field(default_factory=list)
    model_refs: list[str] = Field(default_factory=list)
    requirement_ids: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    provenance: ProvenanceBundle = Field(default_factory=ProvenanceBundle)
    epistemic_state: ClaimStatus = ClaimStatus.UNVALIDATED
    lifecycle: CandidateLifecycle = CandidateLifecycle.PROPOSED


class ConstraintResult(BaseModel):
    requirement_id: str
    required_condition: str
    actual_value: float | str | None = None
    status: ConstraintStatus
    margin: float | None = None
    provenance: ProvenanceBundle = Field(default_factory=ProvenanceBundle)
    epistemic_state: ClaimStatus = ClaimStatus.UNKNOWN


class DesignEvaluation(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    candidate_id: UUID
    requirements_evaluated: list[str] = Field(default_factory=list)
    constraints: list[ConstraintResult] = Field(default_factory=list)
    simulation_refs: list[str] = Field(default_factory=list)
    uncertainty_refs: list[str] = Field(default_factory=list)
    sensitivity_refs: list[str] = Field(default_factory=list)
    optimization_refs: list[str] = Field(default_factory=list)
    passed_constraints: list[str] = Field(default_factory=list)
    failed_constraints: list[str] = Field(default_factory=list)
    unknown_constraints: list[str] = Field(default_factory=list)
    score: float | None = None
    assumptions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    provenance: ProvenanceBundle = Field(default_factory=ProvenanceBundle)
    epistemic_state: ClaimStatus = ClaimStatus.SIMULATED


class EvaluationRequest(BaseModel):
    actual_values: dict[str, float | str] = Field(default_factory=dict)
    simulation: MechanicsSimulationRequest | None = None
    ranges: list[ParameterRange] = Field(default_factory=list)
    output: str = "velocity"
    objective_score: float | None = None


class CandidateComparison(BaseModel):
    status: str
    ranked_candidate_ids: list[UUID] = Field(default_factory=list)
    scores: dict[str, float] = Field(default_factory=dict)
    missing_information: dict[str, list[str]] = Field(default_factory=dict)
    rationale: list[str] = Field(default_factory=list)
    provenance: ProvenanceBundle = Field(default_factory=ProvenanceBundle)
    epistemic_state: ClaimStatus = ClaimStatus.UNKNOWN


class ComparisonRequest(BaseModel):
    candidate_ids: list[UUID] = Field(min_length=2, max_length=100)


class InventionDesignState(BaseModel):
    requirements: dict[str, EngineeringRequirement] = Field(default_factory=dict)
    candidates: dict[UUID, DesignCandidate] = Field(default_factory=dict)
    evaluations: dict[UUID, list[DesignEvaluation]] = Field(default_factory=dict)
    history: dict[UUID, list[dict[str, Any]]] = Field(default_factory=dict)


__all__ = [name for name in globals() if not name.startswith("_")]
