from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from tinkle.reality_engine import ClaimStatus
from tinkle.simulation_engine import MechanicsSimulationRequest


def utc_now() -> datetime:
    return datetime.now(UTC)


class ResearchQuestion(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    question: str = Field(min_length=1, max_length=5000)
    objective: str = ""
    domain: str = ""
    variables: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    unknowns: list[str] = Field(default_factory=list)
    evidence_requirements: list[str] = Field(default_factory=list)
    provenance: dict[str, Any] = Field(default_factory=dict)
    epistemic_state: ClaimStatus = ClaimStatus.UNKNOWN
    created_at: datetime = Field(default_factory=utc_now)


class ResearchHypothesis(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    question_id: UUID
    statement: str = Field(min_length=1, max_length=5000)
    variables: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    predictions: list[str] = Field(default_factory=list)
    expected_relationships: list[str] = Field(default_factory=list)
    falsification_criterion: str = Field(min_length=1, max_length=5000)
    supporting_evidence: list[str] = Field(default_factory=list)
    contradicting_evidence: list[str] = Field(default_factory=list)
    lifecycle_state: str = "NEW"
    confidence: float = Field(default=0.0, ge=0, le=1)
    provenance: dict[str, Any] = Field(default_factory=dict)
    epistemic_state: ClaimStatus = ClaimStatus.UNVALIDATED


class Prediction(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    hypothesis_id: UUID
    input_conditions: dict[str, Any] = Field(default_factory=dict)
    expected_output: dict[str, float | str] = Field(default_factory=dict)
    expected_range: dict[str, tuple[float, float]] = Field(default_factory=dict)
    model_id: UUID | None = None
    simulation_id: UUID | None = None
    assumptions: list[str] = Field(default_factory=list)
    provenance: dict[str, Any] = Field(default_factory=dict)
    epistemic_state: ClaimStatus = ClaimStatus.UNVALIDATED


class ExecutionType(str, Enum):
    PLANNED = "PLANNED"
    SIMULATION = "SIMULATION"
    HUMAN_RECORDED = "HUMAN_RECORDED"


class ResearchExperiment(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    question_id: UUID
    hypothesis_id: UUID
    prediction_id: UUID
    variables: list[str] = Field(default_factory=list)
    inputs: dict[str, Any] = Field(default_factory=dict)
    controls: list[str] = Field(default_factory=list)
    procedure: list[str] = Field(default_factory=list)
    expected_result: dict[str, float | str] = Field(default_factory=dict)
    falsification_criteria: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)
    human_approval_required: bool = True
    execution_type: ExecutionType = ExecutionType.PLANNED
    simulation_request: MechanicsSimulationRequest | None = None
    provenance: dict[str, Any] = Field(default_factory=dict)
    epistemic_state: ClaimStatus = ClaimStatus.UNVALIDATED


class HumanMeasurement(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    experiment_id: UUID
    variable: str
    value: float | str
    unit: str
    timestamp: datetime = Field(default_factory=utc_now)
    source: str
    method: str
    instrument_notes: str = ""
    uncertainty: float | None = Field(default=None, ge=0)
    epistemic_state: ClaimStatus = ClaimStatus.UNKNOWN
    provenance: dict[str, Any] = Field(default_factory=dict)


class ExperimentResult(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    experiment_id: UUID
    execution_type: ExecutionType
    values: dict[str, float | str] = Field(default_factory=dict)
    simulation_id: UUID | None = None
    epistemic_state: ClaimStatus
    provenance: dict[str, Any] = Field(default_factory=dict)


class Comparison(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    prediction_id: UUID
    result_id: UUID
    predicted_range: dict[str, tuple[float, float]] = Field(default_factory=dict)
    observed_or_simulated: dict[str, float | str] = Field(default_factory=dict)
    deviation: dict[str, float] = Field(default_factory=dict)
    comparison_method: str = "range_membership"
    state: str = "INSUFFICIENT_DATA"
    limitations: list[str] = Field(default_factory=list)
    provenance: dict[str, Any] = Field(default_factory=dict)
    epistemic_state: ClaimStatus = ClaimStatus.UNVALIDATED


class ResearchHistoryEvent(BaseModel):
    event: str
    artifact_id: UUID
    state: str
    timestamp: datetime = Field(default_factory=utc_now)
    details: dict[str, Any] = Field(default_factory=dict)


class ResearchWorkflow(BaseModel):
    question: ResearchQuestion
    hypothesis: ResearchHypothesis
    prediction: Prediction | None = None
    experiment: ResearchExperiment | None = None
    result: ExperimentResult | None = None
    measurements: list[HumanMeasurement] = Field(default_factory=list)
    comparison: Comparison | None = None
    history: list[ResearchHistoryEvent] = Field(default_factory=list)
    graph_node_ids: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class MeasurementRequest(BaseModel):
    measurement: HumanMeasurement


class ComparisonRequest(BaseModel):
    result_id: UUID
    predicted_range: dict[str, tuple[float, float]] = Field(default_factory=dict)


class ResearchWorkflowRequest(BaseModel):
    question: ResearchQuestion
    hypothesis: ResearchHypothesis
    experiment: ResearchExperiment | None = None
    prediction: Prediction | None = None
