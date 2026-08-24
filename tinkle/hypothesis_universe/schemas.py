from __future__ import annotations
from enum import Enum
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class HypothesisStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUPPORTED = "SUPPORTED"
    REJECTED = "REJECTED"
    MODIFIED = "MODIFIED"
    COMBINED = "COMBINED"
    RETEST_REQUIRED = "RETEST_REQUIRED"

class Hypothesis(BaseModel):
    id: str
    text: str = Field(min_length=1, max_length=5000)
    status: HypothesisStatus = HypothesisStatus.ACTIVE
    parent_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

class HypothesisTest(BaseModel):
    hypothesis_id: str
    outcome: str = Field(pattern="^(support|reject|inconclusive)$")
    evidence: list[str] = Field(default_factory=list, max_length=50)
    confidence: float = Field(default=0.0, ge=0, le=1)

class HypothesisRequest(BaseModel):
    question: str = Field(min_length=1, max_length=5000)
    hypotheses: list[str] = Field(default_factory=list, max_length=20)
    tests: list[HypothesisTest] = Field(default_factory=list, max_length=100)
    modifications: dict[str, str] = Field(default_factory=dict)
    combinations: list[list[str]] = Field(default_factory=list, max_length=20)
    retest: bool = True

class HypothesisResult(BaseModel):
    universe_id: UUID = Field(default_factory=uuid4)
    question: str
    hypotheses: list[Hypothesis]
    lifecycle: list[str]
    counts: dict[str, int]
    retest_required: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
