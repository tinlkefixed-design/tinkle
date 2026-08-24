from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SelfEvaluationRequest(BaseModel):
    task_id: UUID | None = None
    task_summary: str = Field(min_length=1, max_length=10000)
    assumptions: list[str] = Field(default_factory=list, max_length=100)
    potential_errors: list[str] = Field(default_factory=list, max_length=100)
    verified: list[str] = Field(default_factory=list, max_length=100)
    unknowns: list[str] = Field(default_factory=list, max_length=100)
    failures: list[str] = Field(default_factory=list, max_length=100)
    improvements: list[str] = Field(default_factory=list, max_length=100)
    remember: list[str] = Field(default_factory=list, max_length=100)


class SelfEvaluationRecord(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    task_id: UUID | None = None
    task_summary: str
    assumptions: list[str]
    potential_errors: list[str]
    verified: list[str]
    unknowns: list[str]
    failures: list[str]
    improvements: list[str]
    remember: list[str]
    lessons_stored: int = 0
    created_at: datetime = Field(default_factory=utc_now)


class SelfEvaluationResult(BaseModel):
    evaluation: SelfEvaluationRecord
    lessons: list[dict[str, Any]] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
