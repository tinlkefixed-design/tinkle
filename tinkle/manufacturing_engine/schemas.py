from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field

class ManufacturingOperation(BaseModel):
    sequence: int = Field(gt=0)
    operation: str = Field(min_length=1)
    method: str = Field(min_length=1)
    setup_min: float = Field(default=0, ge=0)
    cycle_min: float = Field(default=0, ge=0)
    inspection: str = ''
    notes: list[str] = Field(default_factory=list)

class ManufacturingRequest(BaseModel):
    product: str = Field(min_length=1, max_length=300)
    bom: list[dict[str, Any]] = Field(default_factory=list, max_length=1000)
    material: str = ''
    target_quantity: int = Field(default=1, gt=0, le=1_000_000)
    preferred_method: str = ''
    machine_rate_per_hour: float = Field(default=0, ge=0)
    material_cost: float = Field(default=0, ge=0)

class ManufacturingPlan(BaseModel):
    product: str
    quantity: int
    operations: list[ManufacturingOperation]
    required_material: str
    estimated_setup_min: float
    estimated_cycle_min: float
    estimated_total_min: float
    estimated_cost: float
    inspection_gates: list[str]
    warnings: list[str]
    provenance: dict[str, Any]
