from fastapi import APIRouter, Depends, HTTPException
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.control_engine import ControlEngine, ControlRequest, ControlArchitecture
router=APIRouter(prefix='/api/v1/control',tags=['control-architecture'])
engine=ControlEngine()
@router.post('/analyze',response_model=ControlArchitecture)
def analyze(req:ControlRequest,p:Principal=Depends(principal_from_key)):
    require(p,Permission.execute)
    try:return engine.analyze(req)
    except ValueError as exc:raise HTTPException(422,str(exc)) from exc
