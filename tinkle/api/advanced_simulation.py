from fastapi import APIRouter, Depends, HTTPException
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.simulation_engine.advanced_engine import AdvancedSimulationEngine
from tinkle.simulation_engine.advanced_schemas import AdvancedSimulationRequest, AdvancedSimulationResult
router=APIRouter(prefix='/api/v1/simulation',tags=['simulation-engine'])
engine=AdvancedSimulationEngine()
@router.post('/advanced',response_model=AdvancedSimulationResult)
def advanced(req:AdvancedSimulationRequest,p:Principal=Depends(principal_from_key)):
    require(p,Permission.execute)
    try:return engine.run(req)
    except ValueError as exc:raise HTTPException(422,str(exc)) from exc
