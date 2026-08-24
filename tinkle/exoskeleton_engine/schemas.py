from __future__ import annotations
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class JointSpec(BaseModel):
    name: str
    degree_of_freedom: int = Field(ge=1, le=3)
    assist_force_n: float = Field(gt=0)
    lever_arm_m: float = Field(gt=0)
    angular_speed_rad_s: float = Field(gt=0)
    efficiency: float = Field(gt=0, le=1)
    safety_factor: float = Field(ge=1, le=5)
    required_torque_nm: float
    required_power_w: float

class ExoskeletonRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    user_mass_kg: float = Field(gt=1, le=500)
    assisted_load_kg: float = Field(ge=0, le=500)
    assistance_fraction: float = Field(gt=0, le=1)
    joints: list[dict[str, Any]] = Field(min_length=1, max_length=32)
    continuous_runtime_h: float = Field(gt=0, le=48)
    battery_usable_fraction: float = Field(gt=0, le=1, default=0.8)
    system_efficiency: float = Field(gt=0, le=1, default=0.75)
    mass_budget_kg: float | None = Field(default=None, gt=0, le=500)

class ExoskeletonDesign(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    status: str
    architecture: dict[str, Any]
    joints: list[JointSpec]
    power: dict[str, float]
    mass_budget: dict[str, float | None]
    verification_gates: list[str]
    warnings: list[str]
    limitations: list[str]
    provenance: dict[str, Any] = Field(default_factory=dict)
