from __future__ import annotations
from typing import Literal, Any
from pydantic import BaseModel, Field

class CAERequest(BaseModel):
    kind: Literal['axial_bar','thermal_1d','buckling_column']
    length_m: float = Field(1.0, gt=0, le=1000)
    area_m2: float = Field(1e-4, gt=0, le=10)
    youngs_modulus_pa: float = Field(200e9, gt=0)
    density_kg_m3: float = Field(7800, gt=0)
    poisson_ratio: float = Field(.3, ge=0, lt=.5)
    nodes: int = Field(11, ge=2, le=501)
    loads_n: dict[int, float] = Field(default_factory=dict)
    fixed_nodes: list[int] = Field(default_factory=lambda:[0])
    conductivity_w_mk: float = Field(45, gt=0)
    temperature_left_c: float = 100
    temperature_right_c: float = 20
    second_moment_m4: float = Field(1e-8, gt=0)
    effective_length_factor: float = Field(1.0, gt=0)
    safety_factor: float = Field(1.5, gt=0)

class CAEResult(BaseModel):
    status: str
    kind: str
    results: dict[str, Any]
    verification: dict[str, Any]
    provenance: dict[str, Any]
    limitations: list[str] = Field(default_factory=list)
