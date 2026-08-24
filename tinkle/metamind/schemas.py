from enum import Enum
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class TaskType(str, Enum):
    simple = "simple"
    reasoning = "reasoning"
    research = "research"
    coding = "coding"
    data_analysis = "data_analysis"
    creative = "creative"
    scientific = "scientific"
    unknown = "unknown"

class TaskRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=20000)
    project_id: str | None = None
    context: dict[str, Any] = {}

class PlanStep(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    action: str
    reason: str
    dependencies: list[str] = []

class MetaMindPlan(BaseModel):
    task_id: UUID = Field(default_factory=uuid4)
    prompt: str
    task_type: TaskType
    reframed_goal: str
    constraints: list[str]
    steps: list[PlanStep]
    model_strategy: str
    tool_strategy: list[str]
    verification_strategy: list[str]
    status: str = "PLANNED"
