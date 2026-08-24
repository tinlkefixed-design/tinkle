from __future__ import annotations

from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from tinkle.reality_engine import ClaimStatus


class NoveltyClass(str, Enum):
    KNOWN='KNOWN'; IMPROVEMENT='IMPROVEMENT'; COMBINATION='COMBINATION'; NOVEL_CANDIDATE='NOVEL_CANDIDATE'; HIGHLY_NOVEL='HIGHLY_NOVEL'

class DesignGenome(BaseModel):
    architecture: str
    materials: list[str]=Field(default_factory=list)
    parameters: dict[str, float|str]=Field(default_factory=dict)
    mechanisms: list[str]=Field(default_factory=list)
    energy_flow: list[str]=Field(default_factory=list)
    control: list[str]=Field(default_factory=list)
    geometry: list[str]=Field(default_factory=list)
    interfaces: list[str]=Field(default_factory=list)

class Invention(BaseModel):
    id: UUID=Field(default_factory=uuid4)
    title: str
    problem: str
    architecture: str
    mechanism: str
    materials: list[str]=Field(default_factory=list)
    process: str|None=None
    algorithm: str|None=None
    genome: DesignGenome
    novelty: NoveltyClass=NoveltyClass.COMBINATION
    novelty_rationale: list[str]=Field(default_factory=list)
    parent_ids: list[UUID]=Field(default_factory=list)
    evidence_refs: list[str]=Field(default_factory=list)
    assumptions: list[str]=Field(default_factory=list)
    risks: list[str]=Field(default_factory=list)
    status: str='CANDIDATE'
    epistemic_state: ClaimStatus = ClaimStatus.UNVALIDATED
    provenance: dict[str,Any]=Field(default_factory=dict)

class InventionRequest(BaseModel):
    problem: str=Field(min_length=1,max_length=10000)
    architectures: list[str]=Field(default_factory=list,max_length=20)
    mechanisms: list[str]=Field(default_factory=list,max_length=30)
    materials: list[str]=Field(default_factory=list,max_length=30)
    processes: list[str]=Field(default_factory=list,max_length=20)
    algorithms: list[str]=Field(default_factory=list,max_length=20)
    constraints: list[str]=Field(default_factory=list,max_length=30)
    known_designs: list[str]=Field(default_factory=list,max_length=50)
    max_candidates: int=Field(default=100,ge=1,le=1000)

class InventionResult(BaseModel):
    run_id: UUID=Field(default_factory=uuid4)
    problem: str
    candidates: list[Invention]
    search_space_size: int
    generated_count: int
    limitations: list[str]=Field(default_factory=list)


class FeasibilityStatus(str, Enum):
    FEASIBLE = 'FEASIBLE'
    CONDITIONALLY_FEASIBLE = 'CONDITIONALLY_FEASIBLE'
    UNCERTAIN = 'UNCERTAIN'
    INFEASIBLE = 'INFEASIBLE'


class InventionGoal(BaseModel):
    text: str = Field(min_length=1, max_length=10000)
    primary_function: str
    epistemic_state: ClaimStatus = ClaimStatus.UNKNOWN


class FunctionalRequirement(BaseModel):
    identifier: str
    description: str
    target: float | str | None = None
    units: str | None = None
    tolerance: float | str | None = None
    priority: int = Field(default=3, ge=1, le=5)
    source: str = 'INFERRED_FROM_GOAL'
    epistemic_state: ClaimStatus = ClaimStatus.UNKNOWN
    confidence: float = Field(default=0.0, ge=0, le=1)
    assumptions: list[str] = Field(default_factory=list)


class Constraint(BaseModel):
    name: str
    value: float | str | None = None
    units: str | None = None
    epistemic_state: ClaimStatus = ClaimStatus.UNKNOWN
    contradiction_risk: str = 'UNKNOWN'


class PerformanceTarget(BaseModel):
    metric: str
    target: float | str | None = None
    units: str | None = None
    epistemic_state: ClaimStatus = ClaimStatus.UNKNOWN


class DesignObjective(BaseModel):
    name: str
    direction: str = 'UNSPECIFIED'
    priority: int = Field(default=3, ge=1, le=5)


class PhysicalPrinciple(BaseModel):
    name: str
    relevance: str
    epistemic_state: ClaimStatus = ClaimStatus.SOURCE_BACKED
    confidence: float = Field(default=0.0, ge=0, le=1)


class Mechanism(BaseModel):
    name: str
    function: str
    principle: str
    advantages: list[str] = Field(default_factory=list)
    disadvantages: list[str] = Field(default_factory=list)
    requirements: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    domains: list[str] = Field(default_factory=list)
    materials: list[str] = Field(default_factory=list)
    epistemic_state: ClaimStatus = ClaimStatus.UNKNOWN


class Architecture(BaseModel):
    name: str
    description: str
    mechanism_names: list[str] = Field(default_factory=list)
    component_names: list[str] = Field(default_factory=list)
    epistemic_state: ClaimStatus = ClaimStatus.UNKNOWN


class Tradeoff(BaseModel):
    objective_a: str
    objective_b: str
    tension: str
    affected_concepts: list[str] = Field(default_factory=list)
    epistemic_state: ClaimStatus = ClaimStatus.ESTIMATED


class FailureMode(BaseModel):
    description: str
    cause: str
    affected_component: str
    affected_requirement: str
    severity: str = 'UNKNOWN'
    likelihood: str = 'UNKNOWN'
    detectability: str = 'UNKNOWN'
    mitigation: str = 'Define verification and safety limits.'
    evidence: list[str] = Field(default_factory=list)
    epistemic_state: ClaimStatus = ClaimStatus.UNKNOWN


class DesignAlternative(BaseModel):
    name: str
    rationale: str
    epistemic_state: ClaimStatus = ClaimStatus.HYPOTHETICAL if hasattr(ClaimStatus, 'HYPOTHETICAL') else ClaimStatus.UNVALIDATED


class ValidationRequirement(BaseModel):
    description: str
    acceptance_measure: str
    epistemic_state: ClaimStatus = ClaimStatus.UNVALIDATED


class SimulationRequirement(BaseModel):
    description: str
    parameters: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    epistemic_state: ClaimStatus = ClaimStatus.UNVALIDATED


class ExperimentRequirement(BaseModel):
    description: str
    measurements: list[str] = Field(default_factory=list)
    safety_gate: str = 'Human review required before physical testing.'
    epistemic_state: ClaimStatus = ClaimStatus.UNVALIDATED


class FictionalFunctionTranslation(BaseModel):
    fictional_capability: str
    real_world_function: str
    physical_requirements: list[str] = Field(default_factory=list)
    candidate_mechanisms: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    epistemic_state: ClaimStatus = ClaimStatus.UNVALIDATED


class FeasibilityAssessment(BaseModel):
    status: FeasibilityStatus
    reasons: list[str] = Field(default_factory=list)
    limiting_factors: list[str] = Field(default_factory=list)
    unknowns: list[str] = Field(default_factory=list)


class InventionHypothesis(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    statement: str
    assumptions: list[str] = Field(default_factory=list)
    predicted_outcome: str
    evidence_refs: list[str] = Field(default_factory=list)
    unknowns: list[str] = Field(default_factory=list)
    validation_requirement: str
    epistemic_state: ClaimStatus = ClaimStatus.UNVALIDATED


class InventionAnalysis(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    goal: InventionGoal
    functions: list[str] = Field(default_factory=list)
    requirements: list[FunctionalRequirement] = Field(default_factory=list)
    constraints: list[Constraint] = Field(default_factory=list)
    performance_targets: list[PerformanceTarget] = Field(default_factory=list)
    objectives: list[DesignObjective] = Field(default_factory=list)
    domains: list[str] = Field(default_factory=list)
    principles: list[PhysicalPrinciple] = Field(default_factory=list)
    mechanisms: list[Mechanism] = Field(default_factory=list)
    architectures: list[Architecture] = Field(default_factory=list)
    candidates: list[Invention] = Field(default_factory=list)
    tradeoffs: list[Tradeoff] = Field(default_factory=list)
    failures: list[FailureMode] = Field(default_factory=list)
    feasibility: list[FeasibilityAssessment] = Field(default_factory=list)
    hypotheses: list[InventionHypothesis] = Field(default_factory=list)
    hypothesis_lifecycle: list[str] = Field(default_factory=list)
    validation: list[ValidationRequirement] = Field(default_factory=list)
    simulations: list[SimulationRequirement] = Field(default_factory=list)
    experiments: list[ExperimentRequirement] = Field(default_factory=list)
    fictional_translation: FictionalFunctionTranslation | None = None
    research_gaps: list[str] = Field(default_factory=list)
    graph_node_ids: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
