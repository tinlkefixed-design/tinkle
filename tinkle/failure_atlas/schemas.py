from __future__ import annotations
from datetime import datetime, timezone
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class FailureRecord(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    failure: str = Field(min_length=1, max_length=5000)
    cause: str = Field(min_length=1, max_length=5000)
    conditions: list[str] = Field(default_factory=list, max_length=50)
    symptoms: list[str] = Field(default_factory=list, max_length=50)
    detection: list[str] = Field(default_factory=list, max_length=50)
    prevention: list[str] = Field(default_factory=list, max_length=50)
    lesson: str = Field(min_length=1, max_length=5000)
    created_at: datetime = Field(default_factory=utc_now)


class FailureAtlasRequest(BaseModel):
    failure: str = Field(min_length=1, max_length=5000)
    cause: str = Field(min_length=1, max_length=5000)
    conditions: list[str] = Field(default_factory=list, max_length=50)
    symptoms: list[str] = Field(default_factory=list, max_length=50)
    detection: list[str] = Field(default_factory=list, max_length=50)
    prevention: list[str] = Field(default_factory=list, max_length=50)
    lesson: str = Field(min_length=1, max_length=5000)


class FailureAtlasResult(BaseModel):
    record: FailureRecord
    status: str = "FAILURE_KNOWLEDGE_RECORDED"
    knowledge: dict[str, object]
    limitations: list[str] = Field(default_factory=list)
