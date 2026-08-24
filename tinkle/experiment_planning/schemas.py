from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from tinkle.engineering_decision import ProvenanceBundle
from tinkle.reality_engine import ClaimStatus


class PlanStatus(str, Enum):
    DRAFT = "DRAFT"
    READY = "READY"
    BLOCKED = "BLOCKED"
    REQUIRES_DATA = "REQUIRES_DATA"
    REQUIRES_VALIDATION = "REQUIRES_VALIDATION"
    APPROVED_FOR_REVIEW = "APPROVED_FOR_REVIEW"
    EXECUTED_EXTERNALLY = "EXECUTED_EXTERNALLY"
    RESULTS_PENDING = "RESULTS_PENDING"
    COMPLETED = "COMPLETED"
    INVALIDATED = "INVALIDATED"


class VariableRole(str, Enum):
    INDEPENDENT = "INDEPENDENT"
    DEPENDENT = "DEPENDENT"
    CONTROL = "CONTROL"
    NUISANCE = "NUISANCE"
    ENVIRONMENTAL = "ENVIRONMENTAL"
    DERIVED = "DERIVED"


class PredictionStatus(str, Enum):
    PREDICTED = "PREDICTED"


class ResearchObjective(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str = Field(min_length=1, max_length=300)
    description: str = Field(min_length=1, max_length=3000)
    source_refs: list[str] = Field(default_factory=list)
    hypothesis_ids: list[str] = Field(default_factory=list)
    requirement_ids: list[str] = Field(default_factory=list)
    priority: int = Field(default=3, ge=1, le=5)
    epistemic_state: ClaimStatus = ClaimStatus.UNKNOWN
    assumptions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class ExperimentObjective(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    objective_type: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=3000)
    research_objective_id: UUID | None = None
    hypothesis_ids: list[str] = Field(default_factory=list)
    candidate_ids: list[UUID] = Field(default_factory=list)
    decision_id: UUID | None = None
    validation_requirement_ids: list[str] = Field(default_factory=list)
    epistemic_state: ClaimStatus = ClaimStatus.UNKNOWN
    provenance: ProvenanceBundle = Field(default_factory=ProvenanceBundle)


class ExperimentalVariable(BaseModel):
    id: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=200)
    units: str | None = None
    role: VariableRole
    allowed_minimum: float | None = None
    allowed_maximum: float | None = None
    nominal_value: float | str | None = None
    epistemic_state: ClaimStatus = ClaimStatus.UNKNOWN
    source: str | None = None
    uncertainty: dict[str, Any] = Field(default_factory=dict)


class MeasurementSpecification(BaseModel):
    id: str = Field(min_length=1, max_length=100)
    variable_id: str
    measurement_method: str | None = None
    units: str | None = None
    expected_minimum: float | None = None
    expected_maximum: float | None = None
    resolution: float | None = Field(default=None, gt=0)
    precision_requirement: float | None = Field(default=None, gt=0)
    required_evidence_state: ClaimStatus = ClaimStatus.MEASURED
    acquisition_requirements: list[str] = Field(default_factory=list)
    uncertainty_requirement: str | None = None


class ExperimentalCondition(BaseModel):
    id: str = Field(min_length=1, max_length=100)
    parameter_values: dict[str, float | str] = Field(default_factory=dict)
    parameter_ranges: dict[str, tuple[float, float]] = Field(default_factory=dict)
    environment: dict[str, str | float] = Field(default_factory=dict)
    assumptions: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    epistemic_state: ClaimStatus = ClaimStatus.UNKNOWN


class Prediction(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    source_refs: list[str] = Field(default_factory=list)
    expected_value: float | str | None = None
    expected_minimum: float | None = None
    expected_maximum: float | None = None
    units: str | None = None
    uncertainty: dict[str, Any] = Field(default_factory=dict)
    model_ref: str | None = None
    simulation_ref: str | None = None
    assumptions: list[str] = Field(default_factory=list)
    epistemic_state: ClaimStatus = ClaimStatus.SIMULATED
    status: PredictionStatus = PredictionStatus.PREDICTED


class ExpectedOutcome(BaseModel):
    expected_observation: str
    expected_minimum: float | None = None
    expected_maximum: float | None = None
    competing_outcome: str | None = None
    interpretation: str
    hypothesis_id: str | None = None
    epistemic_state: ClaimStatus = ClaimStatus.UNKNOWN


class ReproducibilityManifest(BaseModel):
    planner_version: str = "experiment_planning_v1"
    method_version: str = "estimated_information_value_v1"
    input_ids: list[str] = Field(default_factory=list)
    hypothesis_ids: list[str] = Field(default_factory=list)
    candidate_ids: list[UUID] = Field(default_factory=list)
    criteria: dict[str, float] = Field(default_factory=dict)
    variables: list[ExperimentalVariable] = Field(default_factory=list)
    measurements: list[MeasurementSpecification] = Field(default_factory=list)
    uncertainty_configuration: dict[str, Any] = Field(default_factory=dict)
    simulation_refs: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    canonical_hash: str


class ExperimentPlan(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    research_objective_id: UUID
    objective: ExperimentObjective
    hypothesis_ids: list[str] = Field(default_factory=list)
    candidate_ids: list[UUID] = Field(default_factory=list)
    decision_id: UUID | None = None
    validation_requirement_ids: list[str] = Field(default_factory=list)
    variables: list[ExperimentalVariable] = Field(default_factory=list)
    controls: list[str] = Field(default_factory=list)
    conditions: list[ExperimentalCondition] = Field(default_factory=list)
    measurements: list[MeasurementSpecification] = Field(default_factory=list)
    predictions: list[Prediction] = Field(default_factory=list)
    expected_outcomes: list[ExpectedOutcome] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)
    required_evidence: list[str] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    estimated_information_value: float = 0.0
    estimated_cost: float | None = None
    estimated_complexity: float | None = None
    reproducibility_manifest: ReproducibilityManifest | None = None
    provenance: ProvenanceBundle = Field(default_factory=ProvenanceBundle)
    deterministic_hash: str
    status: PlanStatus = PlanStatus.DRAFT
    human_review_required: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ExperimentPlanRequest(BaseModel):
    research_objective_id: UUID
    experiment_objective_id: UUID
    variable_ids: list[str] = Field(default_factory=list)
    measurement_ids: list[str] = Field(default_factory=list)
    condition_ids: list[str] = Field(default_factory=list)
    prediction_ids: list[UUID] = Field(default_factory=list)
    candidate_ids: list[UUID] = Field(default_factory=list)
    decision_id: UUID | None = None
    validation_requirement_ids: list[str] = Field(default_factory=list)
    controls: list[str] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    estimated_cost: float | None = Field(default=None, ge=0)
    estimated_complexity: float | None = Field(default=None, ge=0)


class ExperimentResultReference(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    experiment_plan_id: UUID
    evidence_ids: list[str] = Field(default_factory=list)
    measurement_ids: list[str] = Field(default_factory=list)
    source: str = Field(min_length=1, max_length=1000)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    external_reference: str | None = None
    epistemic_state: ClaimStatus = ClaimStatus.UNKNOWN
    provenance: ProvenanceBundle = Field(default_factory=ProvenanceBundle)


class PlanInvalidation(BaseModel):
    plan_id: UUID
    reason: str = Field(min_length=1, max_length=2000)
    evidence_refs: list[str] = Field(default_factory=list)


class PlanComparison(BaseModel):
    ranked_plan_ids: list[UUID] = Field(default_factory=list)
    status: str
    scores: dict[str, float] = Field(default_factory=dict)
    missing_data: dict[str, list[str]] = Field(default_factory=dict)
    rationale: list[str] = Field(default_factory=list)


class PlanningState(BaseModel):
    research_objectives: dict[UUID, ResearchObjective] = Field(default_factory=dict)
    experiment_objectives: dict[UUID, ExperimentObjective] = Field(default_factory=dict)
    variables: dict[str, ExperimentalVariable] = Field(default_factory=dict)
    measurements: dict[str, MeasurementSpecification] = Field(default_factory=dict)
    conditions: dict[str, ExperimentalCondition] = Field(default_factory=dict)
    predictions: dict[UUID, Prediction] = Field(default_factory=dict)
    plans: dict[UUID, ExperimentPlan] = Field(default_factory=dict)
    results: dict[UUID, ExperimentResultReference] = Field(default_factory=dict)
    history: dict[UUID, list[dict[str, Any]]] = Field(default_factory=dict)
