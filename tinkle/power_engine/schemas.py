from __future__ import annotations
from pydantic import BaseModel, Field

class PowerSystemRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    loads_w: dict[str, float] = Field(min_length=1, max_length=64)
    runtime_h: float = Field(gt=0, le=48)
    system_efficiency: float = Field(gt=0, le=1, default=0.85)
    usable_battery_fraction: float = Field(gt=0, le=1, default=0.8)
    nominal_voltage_v: float = Field(gt=0, le=1000)
    peak_multiplier: float = Field(ge=1, le=5, default=1.5)
    battery_mass_kg: float | None = Field(default=None, gt=0)
    specific_energy_wh_kg: float | None = Field(default=None, gt=0)

class PowerSystemDesign(BaseModel):
    name: str
    status: str
    load_breakdown: dict[str,float]
    energy: dict[str,float]
    electrical: dict[str,float]
    battery: dict[str,float]
    checks: dict[str,bool]
    warnings: list[str]
    limitations: list[str]
