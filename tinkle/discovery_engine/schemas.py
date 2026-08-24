from __future__ import annotations
from enum import Enum
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class DiscoveryStatus(str, Enum):
    CANDIDATE = 'CANDIDATE'
    NEEDS_VERIFICATION = 'NEEDS_VERIFICATION'
    VERIFIED = 'VERIFIED'
    REJECTED = 'REJECTED'

class PatternObservation(BaseModel):
    domain: str = Field(min_length=1, max_length=200)
    pattern: str = Field(min_length=1, max_length=2000)
    evidence: list[str] = Field(default_factory=list, max_length=20)
    confidence: float = Field(default=0.0, ge=0, le=1)

class DiscoveryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=5000)
    observations: list[PatternObservation] = Field(default_factory=list, max_length=50)
    mathematical_structures: list[str] = Field(default_factory=list, max_length=20)
    verify: bool = False
    verification_result: str | None = None

class DiscoveryCandidate(BaseModel):
    id: str
    statement: str
    source_domains: list[str]
    patterns: list[str]
    mathematical_structures: list[str]
    status: DiscoveryStatus
    confidence: float = Field(ge=0, le=1)
    evidence: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

class DiscoveryResult(BaseModel):
    discovery_id: UUID = Field(default_factory=uuid4)
    question: str
    candidates: list[DiscoveryCandidate]
    status: str
    cross_domain: bool
    limitations: list[str] = Field(default_factory=list)
