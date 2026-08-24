from __future__ import annotations
from enum import Enum
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class PrototypeLevel(str, Enum):
    SIMULATION='SIMULATION'; DIGITAL='DIGITAL_PROTOTYPE'; LOW_FIDELITY='LOW_FIDELITY'; FUNCTIONAL='FUNCTIONAL'; ENGINEERING='ENGINEERING'; VALIDATED='VALIDATED'

class BOMItem(BaseModel):
    item: str = Field(min_length=1)
    quantity: float = Field(gt=0)
    unit: str = Field(min_length=1)
    specification: str = ''
    estimated_cost: float = Field(default=0.0, ge=0)

class PrototypeRequest(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    objective: str = Field(min_length=1, max_length=10000)
    components: list[BOMItem] = Field(default_factory=list, max_length=500)
    materials: list[str] = Field(default_factory=list, max_length=100)
    dimensions: dict[str, float | str] = Field(default_factory=dict)
    manufacturing_method: str = ''
    assembly_sequence: list[str] = Field(default_factory=list, max_length=200)
    test_procedure: list[str] = Field(default_factory=list, max_length=200)
    risk_level: str = 'LOW'

class PrototypePlan(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str
    objective: str
    level: PrototypeLevel
    bom: list[BOMItem]
    materials: list[str]
    dimensions: dict[str, float | str]
    manufacturing_method: str
    assembly_sequence: list[str]
    test_procedure: list[str]
    safety_gate: str
    provenance: dict[str, Any] = Field(default_factory=dict)
