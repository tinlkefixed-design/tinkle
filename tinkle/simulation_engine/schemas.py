from __future__ import annotations
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

class SimulationStage(str, Enum):
    model = 'Model'
    parameters = 'Parameters'
    simulation = 'Simulation'
    results = 'Results'
    visualization = 'Visualization'
    optimization = 'Optimization'

class SimulationRequest(BaseModel):
    model: dict[str, Any] = Field(..., min_length=1)
    parameters: dict[str, float] = Field(default_factory=dict)
    steps: int = Field(default=10, ge=1, le=10000)
    dt: float = Field(default=1.0, gt=0.0, le=1e6)
    optimize: bool = False

class SimulationResult(BaseModel):
    status: str
    stages: list[SimulationStage]
    model: dict[str, Any]
    parameters: dict[str, float]
    results: list[dict[str, float]]
    visualization: dict[str, Any]
    optimization: dict[str, Any] | None = None
    limitations: list[str] = Field(default_factory=list)
