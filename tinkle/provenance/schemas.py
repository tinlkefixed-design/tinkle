from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class ProvenanceStatus(str, Enum):
    verified = "verified"
    provisional = "provisional"
    disputed = "disputed"
    stale = "stale"
    unknown = "unknown"

class ProvenanceRecord(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    claim: str
    source: str
    author: str | None = None
    date: datetime | None = None
    location: str | None = None
    evidence: list[str] = []
    confidence: float = Field(default=0.0, ge=0, le=1)
    status: ProvenanceStatus = ProvenanceStatus.unknown
    supporting_sources: list[str] = []
    opposing_sources: list[str] = []
    obtained_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = {}

class ProvenanceQuery(BaseModel):
    claim: str = Field(min_length=1, max_length=2000)

class ProvenanceReport(BaseModel):
    claim: str
    records: list[ProvenanceRecord]
    confidence: float
    status: ProvenanceStatus
