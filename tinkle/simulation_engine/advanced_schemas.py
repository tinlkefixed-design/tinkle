from __future__ import annotations
from typing import Any, Literal
from pydantic import BaseModel, Field

class AdvancedSimulationRequest(BaseModel):
    kind: Literal['ode','monte_carlo_normal','parameter_sweep']
    initial: float = 0.0
    derivative: float = 1.0
    dt: float = Field(0.1, gt=0, le=1e4)
    steps: int = Field(100, ge=1, le=100000)
    mean: float = 0.0
    std: float = Field(1.0, ge=0)
    samples: int = Field(1000, ge=1, le=2_000_000)
    seed: int = 0
    sweep: dict[str, list[float]] = Field(default_factory=dict)
    objective: str = 'sum_squares'

class AdvancedSimulationResult(BaseModel):
    status: str
    kind: str
    result: Any
    provenance: dict[str, Any]
    limitations: list[str] = Field(default_factory=list)
