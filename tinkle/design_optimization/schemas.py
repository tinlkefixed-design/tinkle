from __future__ import annotations
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from tinkle.exoskeleton_engine.schemas import ExoskeletonRequest

class OptimizationVariable(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    minimum: float
    maximum: float
    step: float = Field(gt=0)

class OptimizationRequest(BaseModel):
    design: ExoskeletonRequest
    variables: list[OptimizationVariable] = Field(min_length=1, max_length=8)
    objectives: list[str] = Field(min_length=1, max_length=8)
    max_peak_power_w: float | None = Field(default=None, gt=0)
    max_battery_energy_wh: float | None = Field(default=None, gt=0)
    min_efficiency: float | None = Field(default=None, gt=0, le=1)
    evaluations: int = Field(default=120, ge=8, le=5000)
    seed: int = 0

class OptimizationCandidate(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    variables: dict[str, float]
    metrics: dict[str, float]
    feasible: bool
    constraint_violations: list[str] = Field(default_factory=list)
    score: float

class OptimizationResult(BaseModel):
    status: str
    best: OptimizationCandidate
    pareto_front: list[OptimizationCandidate]
    evaluations: int
    seed: int
    limitations: list[str] = Field(default_factory=list)
    provenance: dict[str, Any] = Field(default_factory=dict)
