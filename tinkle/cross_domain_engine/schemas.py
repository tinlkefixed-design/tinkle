from __future__ import annotations
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class DomainObservation(BaseModel):
    domain: str=Field(min_length=1,max_length=200)
    mechanism: str=Field(min_length=1,max_length=2000)
    function: str=Field(min_length=1,max_length=2000)
    constraints: list[str]=Field(default_factory=list,max_length=20)
    evidence_refs: list[str]=Field(default_factory=list,max_length=50)

class Principle(BaseModel):
    id: UUID=Field(default_factory=uuid4)
    name: str
    abstract_principle: str
    source_domains: list[str]
    target_domain: str
    mapping: str
    mechanism_mapping: str
    mathematical_mapping: str|None=None
    constraints: list[str]=Field(default_factory=list)
    verification_required: list[str]=Field(default_factory=list)
    status: str='CANDIDATE'
    provenance: dict[str,Any]=Field(default_factory=dict)

class CrossDomainRequest(BaseModel):
    problem: str=Field(min_length=1,max_length=10000)
    target_domain: str=Field(min_length=1,max_length=200)
    observations: list[DomainObservation]=Field(default_factory=list,max_length=100)
    max_principles: int=Field(default=50,ge=1,le=200)

class CrossDomainResult(BaseModel):
    run_id: UUID=Field(default_factory=uuid4)
    problem: str
    principles: list[Principle]
    domain_pairs_considered: int
    limitations: list[str]=Field(default_factory=list)
