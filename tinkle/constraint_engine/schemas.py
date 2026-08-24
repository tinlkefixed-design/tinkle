from __future__ import annotations
from enum import Enum
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from tinkle.scientific_core.schemas import ConstraintKind

class ConstraintStatus(str, Enum):
    POSSIBLE="POSSIBLE"; BLOCKED="BLOCKED"; UNKNOWN="UNKNOWN"; RELAXABLE="RELAXABLE"

class ConstraintAssessment(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    expression: str
    kind: ConstraintKind
    status: ConstraintStatus
    reason: str
    governing_laws: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    scope: str = ""
    confidence: float = Field(ge=0, le=1, default=0)
    alternatives: list[str] = Field(default_factory=list)

class ImpossibilityAssessment(BaseModel):
    claim: str
    conclusion: str
    assessments: list[ConstraintAssessment] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    scope: str = ""
    proof_level: str = "NONE"

class RelaxationCandidate(BaseModel):
    original_assumption: str
    alternative: str
    rationale: str
    expected_effect: str
    status: str = "CANDIDATE"
