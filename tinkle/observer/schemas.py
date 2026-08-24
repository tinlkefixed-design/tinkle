from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

METRICS = [
    'Accuracy', 'Hallucinations', 'Retrieval Quality', 'Memory Quality',
    'Latency', 'Agent Loops', 'Failures', 'Model Drift', 'Resource Usage',
    'Tool Errors', 'Security Events'
]

class ObserverEventRequest(BaseModel):
    metric: Literal['Accuracy','Hallucinations','Retrieval Quality','Memory Quality','Latency','Agent Loops','Failures','Model Drift','Resource Usage','Tool Errors','Security Events']
    value: float | None = None
    status: str = Field(default='OBSERVED', min_length=1, max_length=64)
    source: str = Field(min_length=1, max_length=256)
    details: dict[str, Any] = Field(default_factory=dict)

class ObserverEvent(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    metric: str
    value: float | None = None
    status: str
    source: str
    details: dict[str, Any] = Field(default_factory=dict)
    observed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ObserverMetric(BaseModel):
    metric: str
    count: int
    latest_value: float | None = None
    latest_status: str | None = None
    latest_source: str | None = None

class ObserverSnapshot(BaseModel):
    phase: int = 23
    metrics: list[ObserverMetric]
    total_events: int
    limitations: list[str] = Field(default_factory=list)
