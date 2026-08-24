from __future__ import annotations
from datetime import datetime, timezone
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Skill(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(min_length=1, max_length=200)
    procedure: list[str] = Field(min_length=1, max_length=100)
    tools: list[str] = Field(default_factory=list, max_length=50)
    prerequisites: list[str] = Field(default_factory=list, max_length=50)
    benchmarks: list[str] = Field(default_factory=list, max_length=50)
    failure_modes: list[str] = Field(default_factory=list, max_length=50)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    version: int = Field(default=1, ge=1)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class SkillEvolutionRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    procedure: list[str] = Field(min_length=1, max_length=100)
    tools: list[str] = Field(default_factory=list, max_length=50)
    prerequisites: list[str] = Field(default_factory=list, max_length=50)
    benchmarks: list[str] = Field(default_factory=list, max_length=50)
    failure_modes: list[str] = Field(default_factory=list, max_length=50)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    previous_skill_id: UUID | None = None
    benchmark_passed: bool | None = None
    observed_failure: str | None = Field(default=None, max_length=2000)


class SkillEvolutionResult(BaseModel):
    skill: Skill
    status: str
    limitations: list[str] = Field(default_factory=list)


class SkillListResult(BaseModel):
    skills: list[Skill]
    count: int
