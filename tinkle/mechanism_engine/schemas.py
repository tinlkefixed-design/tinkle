from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field

class MechanismRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    mechanism: Literal['direct_drive','spur_gear','planetary_gear','belt_drive','chain_drive']
    required_output_torque_nm: float = Field(gt=0)
    output_speed_rad_s: float = Field(gt=0)
    ratio: float = Field(gt=0, le=1000)
    efficiency: float = Field(gt=0, le=1)
    safety_factor: float = Field(ge=1, le=5, default=1.5)
    service_factor: float = Field(ge=1, le=3, default=1.0)
    motor_max_speed_rad_s: float | None = Field(default=None, gt=0)
    motor_max_torque_nm: float | None = Field(default=None, gt=0)

class MechanismDesign(BaseModel):
    name: str
    status: str
    architecture: dict
    input_requirements: dict[str, float]
    output_requirements: dict[str, float]
    sizing: dict[str, float]
    checks: dict[str, bool]
    warnings: list[str]
    limitations: list[str]
