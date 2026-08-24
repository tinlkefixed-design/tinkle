from __future__ import annotations
from enum import Enum
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from tinkle.knowledge.schemas import SearchMode, SourceProfile

class ResearchStage(str, Enum):
    question='Question'; search='Search'; sources='Sources'; evidence='Evidence'; knowledge='Knowledge'; hypotheses='Hypotheses'; analysis='Analysis'; simulation='Simulation'; criticism='Criticism'; verification='Verification'; report='Report'

class ResearchSource(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    source: str
    title: str | None = None
    author: str | None = None
    date: str | None = None
    location: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    profile: SourceProfile = Field(default_factory=SourceProfile)
    fetched: bool = False

class ResearchEvidence(BaseModel):
    source_id: UUID
    source: str
    text: str
    score: float = Field(ge=0, le=1)
    status: str = 'SUPPORTED'
    evidence_type: str = 'SOURCE'
    metadata: dict[str, Any] = Field(default_factory=dict)

class ResearchRequest(BaseModel):
    question: str = Field(min_length=1, max_length=5000)
    top_k: int = Field(default=5, ge=1, le=20)
    hypotheses: list[str] = Field(default_factory=list, max_length=20)
    simulate: bool = False
    simulation: dict[str, Any] | None = None
    search_mode: SearchMode = SearchMode.broad

class ResearchResult(BaseModel):
    research_id: UUID = Field(default_factory=uuid4)
    question: str
    stages: list[ResearchStage]
    sources: list[ResearchSource]
    evidence: list[ResearchEvidence]
    knowledge: list[str]
    hypotheses: list[str]
    analysis: list[str]
    simulation: dict[str, Any]
    criticism: dict[str, Any]
    verification: dict[str, Any]
    report: str
    confidence: float = Field(ge=0, le=1)
    status: str
    limitations: list[str] = Field(default_factory=list)
