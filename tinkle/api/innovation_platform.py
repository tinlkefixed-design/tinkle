from fastapi import APIRouter, Depends
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.innovation_platform import InnovationPlatform, ResearchMission
from tinkle.experiment_engine.schemas import ExperimentRequest
from tinkle.prototype_engine.schemas import PrototypeRequest
from pydantic import BaseModel, Field
from typing import Any
router=APIRouter(prefix='/api/v1/innovation-platform',tags=['innovation-platform'])
platform=InnovationPlatform()
class ReportRequest(BaseModel):
    mission: ResearchMission
    problem: dict[str,Any]={}
    knowledge:list[dict[str,Any]]=Field(default_factory=list)
    gaps:list[dict[str,Any]]=Field(default_factory=list)
    constraints:list[dict[str,Any]]=Field(default_factory=list)
    hypotheses:list[dict[str,Any]]=Field(default_factory=list)
    models:list[dict[str,Any]]=Field(default_factory=list)
    inventions:list[dict[str,Any]]=Field(default_factory=list)
    principles:list[dict[str,Any]]=Field(default_factory=list)
    simulations:list[dict[str,Any]]=Field(default_factory=list)
    failures:list[dict[str,Any]]=Field(default_factory=list)
    falsification:list[dict[str,Any]]=Field(default_factory=list)
    experiment_requests:list[ExperimentRequest]=Field(default_factory=list)
    prototype_requests:list[PrototypeRequest]=Field(default_factory=list)
    risks:list[str]=Field(default_factory=list)
    unknowns:list[str]=Field(default_factory=list)
@router.post('/report')
def report(req:ReportRequest,p:Principal=Depends(principal_from_key)):
    require(p,Permission.execute)
    return platform.build_report(req.mission,problem=req.problem,knowledge=req.knowledge,gaps=req.gaps,constraints=req.constraints,hypotheses=req.hypotheses,models=req.models,inventions=req.inventions,principles=req.principles,simulations=req.simulations,failures=req.failures,falsification=req.falsification,experiment_requests=req.experiment_requests,prototype_requests=req.prototype_requests,risks=req.risks,unknowns=req.unknowns)
