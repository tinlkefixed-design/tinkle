from __future__ import annotations
from enum import Enum
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class AttackMode(str, Enum):
    EDGE_CASES='EDGE_CASES'; EXTREME_PARAMETERS='EXTREME_PARAMETERS'; NOISE='NOISE'
    MEASUREMENT_ERROR='MEASUREMENT_ERROR'; MODEL_ERROR='MODEL_ERROR'; HIDDEN_ASSUMPTIONS='HIDDEN_ASSUMPTIONS'
    ALTERNATIVE_EXPLANATIONS='ALTERNATIVE_EXPLANATIONS'; CONTRADICTORY_DATA='CONTRADICTORY_DATA'; ADVERSARIAL_INPUTS='ADVERSARIAL_INPUTS'

class FailureSeverity(str, Enum): MINOR='MINOR'; MAJOR='MAJOR'; FATAL='FATAL'; UNKNOWN='UNKNOWN'

class AttackRequest(BaseModel):
    claim: str = Field(min_length=1, max_length=5000)
    assumptions: list[str] = Field(default_factory=list, max_length=50)
    expected: dict[str, float] = Field(default_factory=dict)
    observed: dict[str, float] = Field(default_factory=dict)
    attack_modes: list[AttackMode] = Field(default_factory=lambda: list(AttackMode))
    alternatives: list[str] = Field(default_factory=list, max_length=20)
    evidence: list[str] = Field(default_factory=list, max_length=50)

class AttackFinding(BaseModel):
    mode: AttackMode
    passed: bool
    severity: FailureSeverity
    finding: str
    evidence_refs: list[str] = Field(default_factory=list)
    repair_hint: str | None = None

class RepairCandidate(BaseModel):
    failure_ids: list[str]
    hypothesis: str
    change: str
    retest_required: bool = True
    status: str = 'REPAIR_CANDIDATE'

class AdversarialResult(BaseModel):
    run_id: UUID = Field(default_factory=uuid4)
    claim: str
    findings: list[AttackFinding]
    overall: str
    repair_candidates: list[RepairCandidate] = Field(default_factory=list)
    provenance: dict[str, Any] = Field(default_factory=dict)
