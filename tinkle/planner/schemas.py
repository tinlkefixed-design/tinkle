from __future__ import annotations
from enum import Enum
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class PlannerPriority(str, Enum):
    critical = "critical"
    high = "high"
    normal = "normal"
    low = "low"


class PlannerTask(BaseModel):
    id: str
    name: str
    objective: str
    dependencies: list[str] = []
    priority: PlannerPriority = PlannerPriority.normal
    resource_budget: dict[str, Any] = {}
    stop_conditions: list[str] = []
    retry_limit: int = Field(default=0, ge=0, le=10)
    recovery: list[str] = []
    status: str = "PENDING"


class PlannerRequest(BaseModel):
    goal: str = Field(min_length=1, max_length=20000)
    context: dict[str, Any] = {}
    tasks: list[PlannerTask] | None = None
    resource_budget: dict[str, Any] = {}
    stop_conditions: list[str] = []
    retry_limit: int = Field(default=1, ge=0, le=10)


class PlannerResult(BaseModel):
    plan_id: UUID = Field(default_factory=uuid4)
    goal: str
    tasks: list[PlannerTask]
    verification: PlannerTask
    final_result: PlannerTask
    dependencies: dict[str, list[str]]
    priorities: dict[str, PlannerPriority]
    resource_budgets: dict[str, dict[str, Any]]
    stop_conditions: list[str]
    retry_policy: dict[str, Any]
    recovery_policy: dict[str, Any]
    status: str = "PLANNED"
