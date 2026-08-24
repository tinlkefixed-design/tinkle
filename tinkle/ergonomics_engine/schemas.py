from __future__ import annotations
from pydantic import BaseModel, Field

class RangeOfMotion(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    min_deg: float
    max_deg: float
    user_min_deg: float
    user_max_deg: float

class ErgonomicsRequest(BaseModel):
    user_mass_kg: float = Field(gt=1, le=300)
    stature_m: float = Field(gt=0.5, le=2.5)
    segment_lengths_m: dict[str, float] = Field(min_length=1, max_length=20)
    rom: list[RangeOfMotion] = Field(default_factory=list, max_length=32)
    suit_mass_kg: float = Field(ge=0, le=200)
    attachment_offsets_m: dict[str, float] = Field(default_factory=dict, max_length=32)

class ErgonomicsResult(BaseModel):
    status: str
    segment_estimates_m: dict[str, float]
    rom_checks: list[dict[str, object]]
    balance: dict[str, float]
    fit_warnings: list[str]
    verification_gates: list[str]
    limitations: list[str]
