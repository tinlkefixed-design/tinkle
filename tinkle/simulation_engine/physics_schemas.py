from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from tinkle.reality_engine import ClaimStatus


def utc_now() -> datetime:
    return datetime.now(UTC)


class PhysicsQuantity(BaseModel):
    value: float | None = None
    unit: str
    epistemic_state: ClaimStatus = ClaimStatus.UNKNOWN
    provenance: str | None = None


class ScientificModel(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(min_length=1, max_length=200)
    domain: str = "mechanics"
    description: str
    equations: list[str] = Field(default_factory=list)
    variables: list[str] = Field(default_factory=list)
    parameters: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    provenance: dict[str, Any] = Field(default_factory=dict)
    epistemic_state: ClaimStatus = ClaimStatus.SOURCE_BACKED


class MechanicsSimulationRequest(BaseModel):
    model_id: UUID | None = None
    model: ScientificModel | None = None
    mass: PhysicsQuantity
    force: PhysicsQuantity
    initial_position: PhysicsQuantity = PhysicsQuantity(value=0.0, unit="m", epistemic_state=ClaimStatus.ASSUMED)
    initial_velocity: PhysicsQuantity = PhysicsQuantity(value=0.0, unit="m/s", epistemic_state=ClaimStatus.ASSUMED)
    timestep: float = Field(default=0.1, gt=0, le=1000)
    steps: int = Field(default=10, ge=1, le=10000)
    gravity: PhysicsQuantity = PhysicsQuantity(value=9.81, unit="m/s^2", epistemic_state=ClaimStatus.SOURCE_BACKED, provenance="standard gravitational approximation")
    spring_constant: PhysicsQuantity | None = None
    spring_displacement: PhysicsQuantity | None = None
    requested_outputs: list[str] = Field(default_factory=lambda: ["position", "velocity", "acceleration"])
    assumptions: list[str] = Field(default_factory=list)
    provenance: dict[str, Any] = Field(default_factory=dict)


class MechanicsSimulationResult(BaseModel):
    simulation_id: UUID = Field(default_factory=uuid4)
    model_id: UUID
    solver: str = "deterministic_euler"
    numerical_method: str = "explicit_euler"
    inputs: dict[str, PhysicsQuantity]
    parameters: dict[str, PhysicsQuantity]
    outputs: list[dict[str, float]] = Field(default_factory=list)
    execution_metadata: dict[str, Any] = Field(default_factory=dict)
    assumptions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    uncertainty: dict[str, Any] = Field(default_factory=dict)
    provenance: dict[str, Any] = Field(default_factory=dict)
    epistemic_state: ClaimStatus = ClaimStatus.SIMULATED
    created_at: datetime = Field(default_factory=utc_now)


class PhysicsCalculation(BaseModel):
    quantity: str
    value: float
    unit: str
    equation: str
    inputs: dict[str, PhysicsQuantity]
    provenance: dict[str, Any] = Field(default_factory=dict)
    epistemic_state: ClaimStatus = ClaimStatus.SIMULATED
