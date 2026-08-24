from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ConstraintKind(str, Enum):
    fundamental='fundamental'; technology='technology'; material='material'; energy='energy'
    manufacturing='manufacturing'; economic='economic'; information='information'; assumption='assumption'
    safety='safety'; time='time'; environmental='environmental'; unknown='unknown'


class VerificationState(str, Enum):
    unknown='UNKNOWN'; hypothesis='HYPOTHESIS'; candidate='CANDIDATE'; simulated='SIMULATED'
    experimental='EXPERIMENTAL'; reproduced='REPRODUCED'; independently_tested='INDEPENDENTLY_TESTED'
    validated='VALIDATED'; disputed='DISPUTED'; failed='FAILED'


class UnitQuantity(BaseModel):
    value: float
    unit: str
    dimension: str


class Variable(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(min_length=1, max_length=128)
    symbol: str | None = None
    role: str = 'variable'
    description: str | None = None
    unit: str | None = None
    dimension: str | None = None
    value: float | str | None = None
    bounds: tuple[float, float] | None = None


class Constraint(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    kind: ConstraintKind = ConstraintKind.unknown
    expression: str
    rationale: str | None = None
    source_refs: list[UUID] = Field(default_factory=list)
    hard: bool = True


class EvidenceRef(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    claim: str
    source: str
    evidence_type: str = 'UNKNOWN'
    confidence: float = Field(default=0.0, ge=0, le=1)
    obtained_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ScientificProblem(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    version: int = 1
    parent_id: UUID | None = None
    objective: str
    domains: list[str] = Field(default_factory=list)
    inputs: list[Variable] = Field(default_factory=list)
    outputs: list[Variable] = Field(default_factory=list)
    variables: list[Variable] = Field(default_factory=list)
    parameters: list[Variable] = Field(default_factory=list)
    constants: list[Variable] = Field(default_factory=list)
    constraints: list[Constraint] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    known_laws: list[str] = Field(default_factory=list)
    unknowns: list[str] = Field(default_factory=list)
    desired_performance: dict[str, Any] = Field(default_factory=dict)
    failure_conditions: list[str] = Field(default_factory=list)
    safety_constraints: list[str] = Field(default_factory=list)
    cost_constraints: list[str] = Field(default_factory=list)
    time_constraints: list[str] = Field(default_factory=list)
    environmental_constraints: list[str] = Field(default_factory=list)
    evidence: list[EvidenceRef] = Field(default_factory=list)
    hypotheses: list[str] = Field(default_factory=list)
    candidate_solutions: list[str] = Field(default_factory=list)
    simulations: list[UUID] = Field(default_factory=list)
    experiments: list[UUID] = Field(default_factory=list)
    failures: list[UUID] = Field(default_factory=list)
    verification_state: VerificationState = VerificationState.unknown
    provenance: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class ScientificProblemGraph(BaseModel):
    problem_id: UUID
    nodes: list[dict[str, Any]] = Field(default_factory=list)
    edges: list[dict[str, Any]] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=utc_now)
