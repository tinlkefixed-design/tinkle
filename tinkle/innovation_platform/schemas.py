from __future__ import annotations
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from tinkle.experiment_engine.schemas import ExperimentCandidate
from tinkle.prototype_engine.schemas import PrototypePlan

class ResearchMission(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    mission: str = Field(min_length=1, max_length=10000)
    constraints: list[str] = Field(default_factory=list)
    hypotheses: list[dict[str,Any]] = Field(default_factory=list)
    candidate_inventions: list[dict[str,Any]] = Field(default_factory=list)

class DiscoveryReport(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    mission_id: UUID
    mission: str
    problem: dict[str,Any] = Field(default_factory=dict)
    existing_knowledge: list[dict[str,Any]] = Field(default_factory=list)
    knowledge_gaps: list[dict[str,Any]] = Field(default_factory=list)
    constraints: list[dict[str,Any]] = Field(default_factory=list)
    hypotheses: list[dict[str,Any]] = Field(default_factory=list)
    mathematical_models: list[dict[str,Any]] = Field(default_factory=list)
    candidate_inventions: list[dict[str,Any]] = Field(default_factory=list)
    cross_domain_principles: list[dict[str,Any]] = Field(default_factory=list)
    simulations: list[dict[str,Any]] = Field(default_factory=list)
    failures: list[dict[str,Any]] = Field(default_factory=list)
    falsification_results: list[dict[str,Any]] = Field(default_factory=list)
    experiments: list[ExperimentCandidate] = Field(default_factory=list)
    prototypes: list[PrototypePlan] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    unknowns: list[str] = Field(default_factory=list)
    novelty_assessment: str = 'UNKNOWN'
    verification_status: str = 'NOT_VALIDATED'
    final_confidence: float = Field(default=0.0, ge=0, le=1)
    evidence_labels: list[str] = Field(default_factory=list)
    provenance: dict[str,Any] = Field(default_factory=dict)
