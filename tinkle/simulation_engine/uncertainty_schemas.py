from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from tinkle.reality_engine import ClaimStatus
from tinkle.simulation_engine.physics_schemas import (
    MechanicsSimulationRequest,
    MechanicsSimulationResult,
)


def utc_now() -> datetime:
    return datetime.now(UTC)


class ParameterRange(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(min_length=1, max_length=100)
    nominal: float
    lower: float
    upper: float
    unit: str | None = None
    method: str = "explicit_interval"
    provenance: str | None = None
    epistemic_state: ClaimStatus = ClaimStatus.UNKNOWN
    assumptions: list[str] = Field(default_factory=list)


class UncertaintySpec(BaseModel):
    parameter: ParameterRange
    source: str
    magnitude: str
    method: str = "interval_propagation"
    provenance: str | None = None
    epistemic_state: ClaimStatus
    assumptions: list[str] = Field(default_factory=list)


class AnalysisRequest(BaseModel):
    simulation: MechanicsSimulationRequest
    ranges: list[ParameterRange] = Field(default_factory=list)
    output: str = "velocity"
    perturbation: float = Field(default=0.1, gt=0, le=1)


class SensitivityResult(BaseModel):
    analysis_id: UUID = Field(default_factory=uuid4)
    model_id: UUID
    simulation_id: UUID
    parameter: str
    perturbation: float
    output_variable: str
    baseline_output: float
    changed_output: float
    sensitivity_metric: float
    rank: int = 0
    assumptions: list[str] = Field(default_factory=list)
    provenance: dict[str, Any] = Field(default_factory=dict)
    epistemic_state: ClaimStatus = ClaimStatus.SIMULATED


class UncertaintyAnalysisResult(BaseModel):
    analysis_id: UUID = Field(default_factory=uuid4)
    model_id: UUID
    input_parameters: list[ParameterRange]
    uncertainty_specifications: list[UncertaintySpec]
    propagation_method: str
    output_variable: str
    output_range: dict[str, float]
    evaluations: int
    assumptions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    provenance: dict[str, Any] = Field(default_factory=dict)
    epistemic_state: ClaimStatus = ClaimStatus.SIMULATED


class RobustnessResult(UncertaintyAnalysisResult):
    nominal_output: float
    variation: float
    normalized_variation: float | None = None


class OptimizationRequest(BaseModel):
    simulation: MechanicsSimulationRequest
    ranges: list[ParameterRange] = Field(min_length=1, max_length=5)
    objective: str = "maximize_final_velocity"
    constraints: dict[str, float] = Field(default_factory=dict)


class OptimizationResult(BaseModel):
    optimization_id: UUID = Field(default_factory=uuid4)
    model_id: UUID
    objective: str
    bounds: list[ParameterRange]
    candidates: list[dict[str, Any]]
    selected_configuration: dict[str, float]
    objective_value: float
    constraints: dict[str, float]
    optimization_method: str = "deterministic_grid_search"
    evaluations: int
    assumptions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    provenance: dict[str, Any] = Field(default_factory=dict)
    epistemic_state: ClaimStatus = ClaimStatus.SIMULATED


class SweepResult(BaseModel):
    analysis_id: UUID = Field(default_factory=uuid4)
    model_id: UUID
    simulations: list[MechanicsSimulationResult]
    evaluations: int
    provenance: dict[str, Any] = Field(default_factory=dict)
    epistemic_state: ClaimStatus = ClaimStatus.SIMULATED
