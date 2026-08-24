from fastapi import APIRouter, Depends, HTTPException
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.evolution_engine import EvolutionEngine, EvolutionRequest, EvolutionResult
router=APIRouter(prefix='/api/v1/evolution',tags=['evolution'])
engine=EvolutionEngine()
@router.post('/search',response_model=EvolutionResult)
def search(req:EvolutionRequest,p:Principal=Depends(principal_from_key)):
    require(p,Permission.execute)
    try:return engine.run(req)
    except ValueError as exc:raise HTTPException(422,str(exc)) from exc
