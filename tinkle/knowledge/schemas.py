from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class SearchMode(str, Enum):
    broad='BROAD'; deep='DEEP'; contradiction='CONTRADICTION'; failure='FAILURE'; prior_art='PRIOR_ART'; negative='NEGATIVE'

class EvidenceType(str, Enum):
    source='SOURCE'; observation='OBSERVATION'; calculation='CALCULATION'; simulation='SIMULATION'; experiment='EXPERIMENTAL'; inference='INFERRED'; hypothesis='HYPOTHESIS'

def utc_now(): return datetime.now(timezone.utc)

class SourceProfile(BaseModel):
    authority: float = Field(default=.5, ge=0, le=1)
    recency: float = Field(default=.5, ge=0, le=1)
    relevance: float = Field(default=.5, ge=0, le=1)
    reproducibility: float = Field(default=.5, ge=0, le=1)
    independence: float = Field(default=.5, ge=0, le=1)
    evidence_quality: float = Field(default=.5, ge=0, le=1)
    rationale: list[str] = Field(default_factory=list)

class KnowledgeDocument(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str
    source: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    source_profile: SourceProfile = Field(default_factory=SourceProfile)
    created_at: datetime = Field(default_factory=utc_now)

class KnowledgeChunk(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    text: str
    index: int
    metadata: dict[str, Any] = Field(default_factory=dict)

class Evidence(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    chunk_id: UUID
    document_id: UUID
    source: str
    text: str
    score: float = Field(ge=0, le=1)
    evidence_type: EvidenceType = EvidenceType.source
    source_profile: SourceProfile = Field(default_factory=SourceProfile)
    metadata: dict[str, Any] = Field(default_factory=dict)

class ScientificClaim(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    claim: str
    evidence_refs: list[UUID] = Field(default_factory=list)
    confidence: float = Field(default=0, ge=0, le=1)
    status: str = 'UNKNOWN'
    conditions: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)

class KnowledgeConflict(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    claim_a: str
    claim_b: str
    evidence_a: list[UUID] = Field(default_factory=list)
    evidence_b: list[UUID] = Field(default_factory=list)
    status: str = 'UNRESOLVED'
    conditions: list[str] = Field(default_factory=list)

class KnowledgeQuery(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=50)
    project_id: str | None = None
    mode: SearchMode = SearchMode.broad

class KnowledgeAnswer(BaseModel):
    query: str
    mode: SearchMode = SearchMode.broad
    evidence: list[Evidence]
    claims: list[ScientificClaim] = Field(default_factory=list)
    conflicts: list[KnowledgeConflict] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    status: str
    gaps: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
