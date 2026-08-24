from __future__ import annotations
from enum import Enum
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class GuardianCategory(str, Enum):
    errors = "Errors"
    contradictions = "Contradictions"
    hidden_assumptions = "Hidden Assumptions"
    missing_data = "Missing Data"
    edge_cases = "Edge Cases"
    failure_modes = "Failure Modes"
    model_limitations = "Model Limitations"


class GuardianRequest(BaseModel):
    result: str = Field(min_length=1, max_length=50000)
    context: dict[str, Any] = {}
    evidence: list[str] = []
    assumptions: list[str] = []
    known_limitations: list[str] = []
    requested_categories: list[GuardianCategory] | None = None


class GuardianFinding(BaseModel):
    category: GuardianCategory
    severity: str = "review"
    statement: str
    basis: str


class GuardianResult(BaseModel):
    review_id: UUID = Field(default_factory=uuid4)
    result: str
    findings: list[GuardianFinding]
    categories_checked: list[GuardianCategory]
    status: str = "REVIEW_READY"
    conclusion: str
