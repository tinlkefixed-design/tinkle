from __future__ import annotations
from enum import Enum
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class RiskLevel(str, Enum):
    LOW='LOW'; MEDIUM='MEDIUM'; HIGH='HIGH'; CRITICAL='CRITICAL'

class ExperimentStatus(str, Enum):
    PROPOSED='PROPOSED'; APPROVAL_REQUIRED='APPROVAL_REQUIRED'; APPROVED='APPROVED'; EXECUTED='EXECUTED'; REJECTED='REJECTED'

class ExperimentRequest(BaseModel):
    objective: str = Field(min_length=1, max_length=10000)
    hypotheses: list[str] = Field(default_factory=list, max_length=50)
    variables: list[str] = Field(default_factory=list, max_length=100)
    controls: list[str] = Field(default_factory=list, max_length=100)
    measurements: list[str] = Field(default_factory=list, max_length=100)
    equipment: list[str] = Field(default_factory=list, max_length=100)
    expected_outcomes: list[str] = Field(default_factory=list, max_length=100)
    failure_conditions: list[str] = Field(default_factory=list, max_length=100)
    safety_requirements: list[str] = Field(default_factory=list, max_length=100)
    risk_level: RiskLevel = RiskLevel.LOW
    estimated_cost: float = Field(default=0.0, ge=0)
    estimated_time_seconds: float = Field(default=0.0, ge=0)

class ExperimentPlan(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    objective: str
    hypotheses: list[str]
    variables: list[str]
    controls: list[str]
    measurements: list[str]
    equipment: list[str]
    procedure: list[str]
    expected_outcomes: list[str]
    failure_conditions: list[str]
    safety_requirements: list[str]
    risk_level: RiskLevel
    status: ExperimentStatus
    human_approval_required: bool
    provenance: dict[str, Any] = Field(default_factory=dict)

class ExperimentCandidate(BaseModel):
    plan: ExperimentPlan
    information_gain: float = Field(ge=0)
    value_score: float = Field(ge=0)
    cost_risk_time: float = Field(ge=0)
    priority_score: float

class ExperimentResult(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    experiment_id: UUID
    status: ExperimentStatus
    measurements: dict[str, float | str | bool] = Field(default_factory=dict)
    expected_outcomes: list[str] = Field(default_factory=list)
    deviations: list[str] = Field(default_factory=list)
    evidence_class: str = 'EXPERIMENTAL'
    provenance: dict[str, Any] = Field(default_factory=dict)
