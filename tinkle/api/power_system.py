from fastapi import APIRouter, Depends, HTTPException
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.power_engine import PowerSystemEngine, PowerSystemRequest, PowerSystemDesign
router=APIRouter(prefix='/api/v1/power-system', tags=['power-system-engine'])
engine=PowerSystemEngine()
@router.post('/design', response_model=PowerSystemDesign)
def design(req: PowerSystemRequest, p: Principal=Depends(principal_from_key)):
    require(p, Permission.execute)
    try: return engine.design(req)
    except ValueError as exc: raise HTTPException(422,str(exc)) from exc
