from __future__ import annotations
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class TwinSignal(BaseModel):
    name: str = Field(min_length=1)
    value: float
    unit: str = ''
    expected: float | None = None
    tolerance: float = Field(default=0.05, ge=0)

class TwinSnapshot(BaseModel):
    timestamp: float
    state: dict[str, float]
    signals: list[TwinSignal]
    health_score: float = Field(ge=0, le=1)

class TwinComparison(BaseModel):
    signal: str
    expected: float
    observed: float
    absolute_error: float
    relative_error: float
    within_tolerance: bool

class DigitalTwinRequest(BaseModel):
    name: str = Field(min_length=1, max_length=300)
    model_id: str = Field(default='prototype')
    parameters: dict[str, float] = Field(default_factory=dict)
    signals: list[TwinSignal] = Field(default_factory=list, max_length=500)
    duration_s: float = Field(default=1.0, gt=0, le=86400)
    sample_rate_hz: float = Field(default=10.0, gt=0, le=10000)

class DigitalTwinResult(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    model_id: str
    snapshots: list[TwinSnapshot]
    comparisons: list[TwinComparison]
    health_score: float = Field(ge=0, le=1)
    warnings: list[str]
    provenance: dict[str, Any]
