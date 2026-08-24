from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class ImprovementType(str, Enum):
    code = 'Code improvement'
    prompt = 'Prompt improvement'
    workflow = 'Workflow improvement'
    agent = 'Agent improvement'
    tool = 'Tool improvement'
    retrieval = 'Retrieval improvement'
    planning = 'Planning improvement'
    evaluation = 'Evaluation improvement'

class ImprovementStage(str, Enum):
    PROPOSAL = 'Proposal'
    SANDBOX = 'Sandbox'
    IMPLEMENTATION = 'Implementation'
    TESTS = 'Tests'
    BENCHMARKS = 'Benchmarks'
    SECURITY_REVIEW = 'Security Review'
    COMPARISON = 'Comparison'
    HUMAN_APPROVAL = 'Human Approval'
    PRODUCTION = 'Production'

STAGES = list(ImprovementStage)

class ImprovementProposal(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    improvement_type: ImprovementType
    title: str = Field(min_length=1, max_length=200)
    rationale: str = Field(min_length=1, max_length=4000)
    target: str = Field(min_length=1, max_length=500)
    expected_benefit: str = Field(min_length=1, max_length=2000)
    risks: list[str] = Field(default_factory=list, max_length=50)
    evidence: list[str] = Field(default_factory=list, max_length=50)
    stage: ImprovementStage = ImprovementStage.PROPOSAL
    stage_history: list[ImprovementStage] = Field(default_factory=lambda: [ImprovementStage.PROPOSAL])
    sandbox_ref: str | None = None
    test_result: str | None = None
    benchmark_result: str | None = None
    security_result: str | None = None
    comparison_result: str | None = None
    human_approved: bool = False
    production_applied: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProposalRequest(BaseModel):
    improvement_type: ImprovementType
    title: str = Field(min_length=1, max_length=200)
    rationale: str = Field(min_length=1, max_length=4000)
    target: str = Field(min_length=1, max_length=500)
    expected_benefit: str = Field(min_length=1, max_length=2000)
    risks: list[str] = Field(default_factory=list, max_length=50)
    evidence: list[str] = Field(default_factory=list, max_length=50)

class StageUpdateRequest(BaseModel):
    result: str | None = Field(default=None, max_length=4000)
    sandbox_ref: str | None = Field(default=None, max_length=500)
    human_approved: bool = False

class ImprovementResponse(BaseModel):
    proposal: ImprovementProposal
    next_stage: ImprovementStage | None = None
    limitations: list[str] = Field(default_factory=list)

class ImprovementList(BaseModel):
    items: list[ImprovementProposal]
    phase: int = 24
