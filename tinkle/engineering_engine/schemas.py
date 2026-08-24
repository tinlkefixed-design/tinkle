from __future__ import annotations

from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class EngineeringDomain(str, Enum):
    mechanical_engineering = "Mechanical Engineering"
    electrical_engineering = "Electrical Engineering"
    electronics = "Electronics"
    robotics = "Robotics"
    control_systems = "Control Systems"
    thermal_engineering = "Thermal Engineering"
    materials_engineering = "Materials Engineering"
    energy_systems = "Energy Systems"
    software_engineering = "Software Engineering"


class EngineeringRequest(BaseModel):
    problem: str = Field(min_length=1, max_length=20000)
    domain: EngineeringDomain
    context: dict[str, Any] = Field(default_factory=dict)


class EngineeringModule(BaseModel):
    domain: EngineeringDomain
    status: str
    capabilities: list[str] = Field(default_factory=list)


class EngineeringSolveRequest(BaseModel):
    problem: str = Field(min_length=1, max_length=20000)
    domain: EngineeringDomain
    model: str = Field(min_length=1, max_length=128)
    inputs: dict[str, float] = Field(default_factory=dict)


class EngineeringResult(BaseModel):
    request_id: UUID = Field(default_factory=uuid4)
    problem: str
    domain: EngineeringDomain
    status: str
    module: EngineeringModule
    solution: str | None = None
    calculation: dict[str, Any] | None = None
    requirements: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
