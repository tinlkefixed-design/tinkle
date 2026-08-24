from __future__ import annotations
from enum import Enum
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class MissionStatus(str, Enum): PLANNED='PLANNED'; RUNNING='RUNNING'; PAUSED='PAUSED'; COMPLETED='COMPLETED'; FAILED='FAILED'; STOPPED='STOPPED'

class ResourceBudget(BaseModel):
    token_budget:int=Field(default=10000, ge=0); compute_budget:float=Field(default=100.0, ge=0)
    time_budget_seconds:int=Field(default=3600, ge=0); simulation_budget:int=Field(default=100, ge=0)
    search_budget:int=Field(default=50, ge=0); storage_budget_mb:int=Field(default=100, ge=0); tool_budget:int=Field(default=100, ge=0)

class MissionRequest(BaseModel):
    mission:str=Field(min_length=1,max_length=10000)
    hypotheses:list[dict[str,Any]]=Field(default_factory=list,max_length=100)
    candidate_designs:list[dict[str,Any]]=Field(default_factory=list,max_length=100)
    budget:ResourceBudget=Field(default_factory=ResourceBudget)
    max_iterations:int=Field(default=3,ge=1,le=100)
    stop_on_fatal:bool=True

class DiscoveryNode(BaseModel):
    id:str; parent_id:str|None=None; kind:str; label:str; status:str='OPEN'; metadata:dict[str,Any]=Field(default_factory=dict)

class Checkpoint(BaseModel):
    id:str=Field(default_factory=lambda:str(uuid4())); iteration:int; status:MissionStatus; state:dict[str,Any]; remaining_budget:ResourceBudget

class DiscoveryRun(BaseModel):
    run_id:UUID=Field(default_factory=uuid4); mission:str; status:MissionStatus; iteration:int
    nodes:list[DiscoveryNode]; checkpoints:list[Checkpoint]; open_hypotheses:list[dict[str,Any]]
    selected_actions:list[dict[str,Any]]; failures:list[dict[str,Any]]; best_candidates:list[dict[str,Any]]
    resource_used:dict[str,float]=Field(default_factory=dict); provenance:dict[str,Any]=Field(default_factory=dict)
