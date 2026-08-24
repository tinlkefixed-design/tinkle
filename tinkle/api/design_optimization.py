from fastapi import APIRouter, Depends, HTTPException
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.design_optimization import DesignOptimizationEngine, OptimizationRequest, OptimizationResult
router=APIRouter(prefix='/api/v1/design-optimization',tags=['design-optimization'])
engine=DesignOptimizationEngine()
@router.post('/run',response_model=OptimizationResult)
def run(req:OptimizationRequest,p:Principal=Depends(principal_from_key)):
    require(p,Permission.execute)
    try:return engine.run(req)
    except ValueError as exc: raise HTTPException(422,str(exc)) from exc
