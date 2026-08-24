from __future__ import annotations
from enum import Enum
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class NoveltyClass(str, Enum):
    KNOWN='KNOWN'; IMPROVEMENT='IMPROVEMENT'; COMBINATION='COMBINATION'; NOVEL_CANDIDATE='NOVEL_CANDIDATE'; HIGHLY_NOVEL='HIGHLY_NOVEL'

class DesignGenome(BaseModel):
    architecture: str
    materials: list[str]=Field(default_factory=list)
    parameters: dict[str, float|str]=Field(default_factory=dict)
    mechanisms: list[str]=Field(default_factory=list)
    energy_flow: list[str]=Field(default_factory=list)
    control: list[str]=Field(default_factory=list)
    geometry: list[str]=Field(default_factory=list)
    interfaces: list[str]=Field(default_factory=list)

class Invention(BaseModel):
    id: UUID=Field(default_factory=uuid4)
    title: str
    problem: str
    architecture: str
    mechanism: str
    materials: list[str]=Field(default_factory=list)
    process: str|None=None
    algorithm: str|None=None
    genome: DesignGenome
    novelty: NoveltyClass=NoveltyClass.COMBINATION
    novelty_rationale: list[str]=Field(default_factory=list)
    parent_ids: list[UUID]=Field(default_factory=list)
    evidence_refs: list[str]=Field(default_factory=list)
    assumptions: list[str]=Field(default_factory=list)
    risks: list[str]=Field(default_factory=list)
    status: str='CANDIDATE'
    provenance: dict[str,Any]=Field(default_factory=dict)

class InventionRequest(BaseModel):
    problem: str=Field(min_length=1,max_length=10000)
    architectures: list[str]=Field(default_factory=list,max_length=20)
    mechanisms: list[str]=Field(default_factory=list,max_length=30)
    materials: list[str]=Field(default_factory=list,max_length=30)
    processes: list[str]=Field(default_factory=list,max_length=20)
    algorithms: list[str]=Field(default_factory=list,max_length=20)
    constraints: list[str]=Field(default_factory=list,max_length=30)
    known_designs: list[str]=Field(default_factory=list,max_length=50)
    max_candidates: int=Field(default=100,ge=1,le=1000)

class InventionResult(BaseModel):
    run_id: UUID=Field(default_factory=uuid4)
    problem: str
    candidates: list[Invention]
    search_space_size: int
    generated_count: int
    limitations: list[str]=Field(default_factory=list)
