from __future__ import annotations
from enum import Enum
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class DesignIntent(str, Enum):
    ANALYZE = "ANALYZE"
    DESIGN = "DESIGN"
    OPTIMIZE = "OPTIMIZE"
    VALIDATE = "VALIDATE"

class EngineeringRequirement(BaseModel):
    name: str
    description: str
    category: str
    priority: int = Field(ge=1, le=5)
    measurable: bool = True

class EngineeringDecision(BaseModel):
    decision: str
    rationale: str
    domains: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)

class EngineeringBrainRequest(BaseModel):
    problem: str = Field(min_length=1, max_length=20000)
    intent: DesignIntent = DesignIntent.DESIGN
    constraints: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)

class EngineeringBrainResult(BaseModel):
    request_id: UUID = Field(default_factory=uuid4)
    status: str
    intent: DesignIntent
    normalized_problem: str
    requirements: list[EngineeringRequirement]
    domains: list[str]
    decisions: list[EngineeringDecision]
    verification_plan: list[str]
    assumptions: list[str]
    unresolved_items: list[str]
    confidence: float = Field(ge=0, le=1)
    provenance: dict[str, Any] = Field(default_factory=dict)
