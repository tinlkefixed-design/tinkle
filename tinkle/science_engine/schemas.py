from __future__ import annotations

from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ScienceDomain(str, Enum):
    physics = "Physics"
    chemistry = "Chemistry"
    biology = "Biology"
    materials_science = "Materials Science"
    energy = "Energy"
    astronomy = "Astronomy"


class ScienceRequest(BaseModel):
    question: str = Field(min_length=1, max_length=20000)
    domain: ScienceDomain
    context: dict[str, Any] = Field(default_factory=dict)


class ScienceSolveRequest(BaseModel):
    domain: ScienceDomain
    problem: str = Field(min_length=1, max_length=20000)
    model: str = Field(min_length=1, max_length=100)
    inputs: dict[str, float] = Field(default_factory=dict)


class ScienceModule(BaseModel):
    domain: ScienceDomain
    status: str
    capabilities: list[str] = Field(default_factory=list)


class ScienceResult(BaseModel):
    request_id: UUID = Field(default_factory=uuid4)
    question: str
    domain: ScienceDomain
    status: str
    module: ScienceModule
    answer: str | None = None
    evidence_required: bool = True
    limitations: list[str] = Field(default_factory=list)
    calculation: dict[str, Any] | None = None
