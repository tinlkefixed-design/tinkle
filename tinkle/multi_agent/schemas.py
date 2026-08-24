from __future__ import annotations
from enum import Enum
from uuid import UUID, uuid4
from typing import Any
from tinkle.core.schemas import Privacy
from pydantic import BaseModel, Field


class AgentRole(str, Enum):
    researcher = "Researcher"
    scientist = "Scientist"
    mathematician = "Mathematician"
    engineer = "Engineer"
    programmer = "Programmer"
    data_scientist = "Data Scientist"
    creative_explorer = "Creative Explorer"
    skeptic = "Skeptic"
    verifier = "Verifier"
    judge = "Judge"


ROLE_OBJECTIVES = {
    AgentRole.researcher: "research and evidence gathering",
    AgentRole.scientist: "analysis of scientific problems",
    AgentRole.mathematician: "calculation and mathematical modeling",
    AgentRole.engineer: "design and engineering analysis",
    AgentRole.programmer: "programming and tool building",
    AgentRole.data_scientist: "data analysis",
    AgentRole.creative_explorer: "generation of unconventional ideas",
    AgentRole.skeptic: "attempts to prove that the solution is wrong",
    AgentRole.verifier: "verification of results and sources",
    AgentRole.judge: "comparison of solutions and selection of the best one",
}


class AgentRequest(BaseModel):
    goal: str = Field(min_length=1, max_length=20000)
    context: dict[str, Any] = {}
    roles: list[AgentRole] | None = None
    difficulty: float = Field(default=.6, ge=0, le=1)
    privacy: Privacy = Privacy.public


class AgentResult(BaseModel):
    role: AgentRole
    objective: str
    input_summary: str
    findings: list[str] = []
    status: str = "READY"
    model_id: str | None = None
    provider: str | None = None
    error: str | None = None


class MultiAgentResult(BaseModel):
    run_id: UUID = Field(default_factory=uuid4)
    goal: str
    agents: list[AgentResult]
    roles: list[AgentRole]
    status: str = "READY"
    synthesis: str | None = None
