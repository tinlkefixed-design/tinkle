from fastapi import APIRouter, Depends, HTTPException
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.exoskeleton_engine import ExoskeletonEngine, ExoskeletonRequest, ExoskeletonDesign
router=APIRouter(prefix='/api/v1/exoskeleton', tags=['exoskeleton-engine'])
engine=ExoskeletonEngine()
@router.post('/design', response_model=ExoskeletonDesign)
def design(req: ExoskeletonRequest, p: Principal=Depends(principal_from_key)):
    require(p, Permission.execute)
    try: return engine.design(req)
    except ValueError as exc: raise HTTPException(422, str(exc)) from exc
