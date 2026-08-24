from __future__ import annotations

from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MathMode(str, Enum):
    exact = "exact"
    numerical = "numerical"


class MathRequest(BaseModel):
    """Structured request entering the Math Engine after upstream interpretation."""

    question: str = Field(min_length=1, max_length=20000)
    expression: str = Field(min_length=1, max_length=10000)
    mode: MathMode = MathMode.exact
    variables: dict[str, float] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)


class VerificationResult(BaseModel):
    verified: bool
    method: str
    details: str


class MathResult(BaseModel):
    calculation_id: UUID = Field(default_factory=uuid4)
    question: str
    expression: str
    mode: MathMode
    result: str
    exact_result: str | None = None
    numerical_result: float | None = None
    verification: VerificationResult
    status: str = "CALCULATED"
