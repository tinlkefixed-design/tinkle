from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ClaimStatus(str, Enum):
    KNOWN = "KNOWN"
    MEASURED = "MEASURED"
    SOURCE_BACKED = "SOURCE_BACKED"
    ESTIMATED = "ESTIMATED"
    ASSUMED = "ASSUMED"
    INFERRED = "INFERRED"
    SIMULATED = "SIMULATED"
    UNKNOWN = "UNKNOWN"
    UNVALIDATED = "UNVALIDATED"
    CONTRADICTED = "CONTRADICTED"
    FALSIFIED = "FALSIFIED"


class ClaimKind(str, Enum):
    FACT = "FACT"
    MEASUREMENT = "MEASUREMENT"
    SOURCE = "SOURCE"
    ESTIMATE = "ESTIMATE"
    ASSUMPTION = "ASSUMPTION"
    INFERENCE = "INFERENCE"
    SIMULATION = "SIMULATION"
    UNKNOWN = "UNKNOWN"
    HYPOTHESIS = "HYPOTHESIS"
    SPECULATION = "SPECULATION"


class Claim(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    statement: str = Field(min_length=1, max_length=20000)
    kind: ClaimKind = ClaimKind.UNKNOWN
    status: ClaimStatus = ClaimStatus.UNKNOWN
    confidence: float = Field(default=0.0, ge=0, le=1)
    evidence_ids: list[UUID] = Field(default_factory=list)
    source_ids: list[UUID] = Field(default_factory=list)
    assumption_ids: list[UUID] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    dependencies: list[str] = Field(default_factory=list)


class Assumption(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    assumption: str = Field(min_length=1, max_length=5000)
    status: ClaimStatus = ClaimStatus.ASSUMED
    impact: str = "MEDIUM"
    dependencies: list[str] = Field(default_factory=list)
    notes: str | None = None
    created_at: datetime = Field(default_factory=utc_now)


class EvidenceRecord(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    description: str = Field(min_length=1, max_length=5000)
    source: str | None = None
    evidence_type: str = "UNKNOWN"
    status: ClaimStatus = ClaimStatus.UNKNOWN
    confidence: float = Field(default=0.0, ge=0, le=1)
    created_at: datetime = Field(default_factory=utc_now)


class ValueProvenance(BaseModel):
    name: str
    value: Any = None
    source: str | None = None
    status: ClaimStatus = ClaimStatus.UNKNOWN
    confidence: float = Field(default=0.0, ge=0, le=1)
    notes: str | None = None


class ParameterSweepRequest(BaseModel):
    base_values: dict[str, float] = Field(default_factory=dict)
    variations: dict[str, list[float]] = Field(default_factory=dict)
    base_output: float | None = None
    model: Any = None
    description: str = ""


class DependencyNode(BaseModel):
    id: str
    type: str
    label: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class DependencyEdge(BaseModel):
    source: str
    target: str
    relation: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgeDependencyGraph(BaseModel):
    nodes: list[DependencyNode] = Field(default_factory=list)
    edges: list[DependencyEdge] = Field(default_factory=list)


class ResearchProjectState(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    idea: str = ""
    goals: list[str] = Field(default_factory=list)
    functional_requirements: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    scientific_domains: list[str] = Field(default_factory=list)
    knowledge: list[str] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    assumptions: list[Assumption] = Field(default_factory=list)
    unknowns: list[str] = Field(default_factory=list)
    hypotheses: list[str] = Field(default_factory=list)
    models: list[str] = Field(default_factory=list)
    simulations: list[str] = Field(default_factory=list)
    results: list[str] = Field(default_factory=list)
    failures: list[str] = Field(default_factory=list)
    alternatives: list[str] = Field(default_factory=list)
    experiments: list[str] = Field(default_factory=list)
    conclusions: list[str] = Field(default_factory=list)
    discovery_ledger: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class RealityCheckRequest(BaseModel):
    claim: str = Field(min_length=1, max_length=20000)
    evidence: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    required_parameters: list[str] = Field(default_factory=list)
    known_values: dict[str, Any] = Field(default_factory=dict)
    simulation: dict[str, Any] | None = None
