from fastapi import APIRouter, Depends
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.experiment_engine import ExperimentEngine
from tinkle.experiment_engine.schemas import ExperimentRequest
router=APIRouter(prefix='/api/v1/experiments',tags=['experiments'])
engine=ExperimentEngine()
@router.post('/plan')
def plan(req:ExperimentRequest,p:Principal=Depends(principal_from_key)):
    require(p,Permission.execute); return engine.plan(req)
@router.post('/rank')
def rank(reqs:list[ExperimentRequest],p:Principal=Depends(principal_from_key)):
    require(p,Permission.execute); return engine.rank(reqs)
